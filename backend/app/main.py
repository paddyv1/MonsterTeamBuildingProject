from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(title="Monster Team Builder API")


app.include_router(health_router)


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/healthz")
async def healthz():
    return {"healthyz": True}
