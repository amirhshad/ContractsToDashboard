"""Minimal FastAPI test for Vercel using Mangum."""

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/api/")
async def root():
    return {"status": "healthy", "message": "FastAPI is working"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Mangum handler for AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")
