from fastapi import Response

from app.auth.sessionauth import COOKIE_NAME, sign


def set_session_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=sign(user_id),
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        path="/",
        max_age=60 * 60 * 24 * 7,  # 1 week
    )
    
    
def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")