from fastapi import FastAPI

app = FastAPI(title="Monster Team Builder API")


@app.get("/api/health")
async def health():
    return {"ok": True}


