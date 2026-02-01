"""FastAPI application entry point."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import contracts, recommendations, upload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Contract Optimizer API",
    description="API for managing contracts and generating AI-powered recommendations",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Include routers
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Contract Optimizer API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
