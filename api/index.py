"""Minimal FastAPI test for Vercel."""

from fastapi import FastAPI

app = FastAPI()

@app.get("/api/")
async def root():
    return {"status": "healthy", "message": "FastAPI is working"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Export for Vercel
handler = app
