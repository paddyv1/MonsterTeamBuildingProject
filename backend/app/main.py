from fastapi import FastAPI

app = FastAPI(title="Monster Team Builder API")


@app.get("/api/health")
async def health():
    return {"ok": True}

@app.get("/api/healthz")
async def healthz():
    return {"healthyz": True}
