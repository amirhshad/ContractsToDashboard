"""Vercel serverless function entry point for FastAPI backend."""

import sys
import os

# Add the project root to the path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from backend.main import app

# Create the handler for Vercel/AWS Lambda
handler = Mangum(app, lifespan="off")
