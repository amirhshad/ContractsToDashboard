"""Recommendation analysis service using Claude AI."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from execution.recommendation_engine import generate_recommendations
from backend.config import get_settings


async def generate_recommendations_for_user(
    contracts: list[dict], user_id: str
) -> list[dict]:
    """Generate AI-powered recommendations for a user's contracts."""
    settings = get_settings()

    # Use the execution layer script
    recommendations = generate_recommendations(contracts, settings.anthropic_api_key)

    # Add user_id to each recommendation
    for rec in recommendations:
        rec["user_id"] = user_id

    return recommendations
