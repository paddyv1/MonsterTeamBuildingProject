import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.cookies import clear_session_cookie, set_session_cookie
from app.auth.deps import get_current_user
from app.database.models.user import User
from app.database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"{name} is not set")
    return v


@router.get("/github/login")
async def github_login() -> Response:
    client_id = _env("GITHUB_CLIENT_ID")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    redirect_uri = f"{backend_url}/auth/github/callback"

    state = secrets.token_urlsafe(32)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user",
        "state": state,
    }

    url = "https://github.com/login/oauth/authorize?" + urlencode(params)

    resp = RedirectResponse(url=url, status_code=302)
    resp.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/auth/github",
        max_age=60 * 10,  # 10 min
    )
    return resp


@router.get("/github/callback")
async def github_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    # 1) verify state
    expected_state = request.cookies.get("oauth_state")
    if not expected_state or expected_state != state:
        raise HTTPException(status_code=400, detail="Invalid oauth state")

    client_id = _env("GITHUB_CLIENT_ID")
    client_secret = _env("GITHUB_CLIENT_SECRET")
    frontend_url = _env("FRONTEND_URL")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    redirect_uri = f"{backend_url}/auth/github/callback"

    # 2) exchange code -> access token
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access_token returned from GitHub")

        # 3) fetch GitHub user
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        user_resp.raise_for_status()
        gh = user_resp.json()

    github_id = str(gh["id"])
    username = gh["login"]
    #avatar_url = gh.get("avatar_url")

    # 4) upsert user by github_id
    result = await db.execute(select(User).where(User.github_id == github_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(github_id=github_id, username=username)
        db.add(user)
    else:
        user.username = username
        #user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)

    # 5) set session cookie + clear oauth_state cookie
    resp = RedirectResponse(url=frontend_url, status_code=302)
    set_session_cookie(resp, str(user.id))
    resp.delete_cookie("oauth_state", path="/auth/github")
    return resp


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "github_id": user.github_id,
        "username": user.username,
        #"avatar_url": user.avatar_url,
    }


@router.post("/logout")
async def logout() -> Response:
    resp = Response(content='{"ok": true}', media_type="application/json")
    clear_session_cookie(resp)
    return resp