"""Recommendation management endpoints."""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from supabase import create_client, Client

from backend.config import get_settings, Settings
from backend.models import (
    Recommendation,
    RecommendationUpdate,
    RecommendationStatus,
)
from backend.services.analysis import generate_recommendations_for_user

router = APIRouter()


def get_supabase(settings: Settings = Depends(get_settings)) -> Client:
    """Get Supabase client."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


async def get_user_id(authorization: str = Header(...)) -> str:
    """Extract user ID from JWT token."""
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_anon_key)

    # Properly extract token - only strip "Bearer " prefix, not all occurrences
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.get("", response_model=list[Recommendation])
async def list_recommendations(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """List all recommendations for the authenticated user."""
    query = supabase.table("recommendations").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)
    if priority:
        query = query.eq("priority", priority)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.post("/generate", response_model=list[Recommendation])
async def generate_recommendations(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Generate AI recommendations based on user's contracts."""
    # Get user's contracts
    contracts_result = (
        supabase.table("contracts").select("*").eq("user_id", user_id).execute()
    )

    if not contracts_result.data:
        return []

    # Generate recommendations
    try:
        recommendations = await generate_recommendations_for_user(
            contracts_result.data, user_id
        )

        # Save recommendations to database
        if recommendations:
            for rec in recommendations:
                rec["user_id"] = user_id

            result = supabase.table("recommendations").insert(recommendations).execute()
            return result.data

        return []

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/{recommendation_id}", response_model=Recommendation)
async def get_recommendation(
    recommendation_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Get a single recommendation by ID."""
    result = (
        supabase.table("recommendations")
        .select("*")
        .eq("id", recommendation_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Mark as viewed if pending
    if result.data.get("status") == "pending":
        supabase.table("recommendations").update({"status": "viewed"}).eq(
            "id", recommendation_id
        ).execute()
        result.data["status"] = "viewed"

    return result.data


@router.put("/{recommendation_id}", response_model=Recommendation)
async def update_recommendation(
    recommendation_id: str,
    update: RecommendationUpdate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Update a recommendation (e.g., accept or dismiss)."""
    # Verify ownership
    existing = (
        supabase.table("recommendations")
        .select("id")
        .eq("id", recommendation_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    data = update.model_dump(exclude_none=True)

    # Set acted_on_at if status is changing to accepted or dismissed
    if update.status in [RecommendationStatus.ACCEPTED, RecommendationStatus.DISMISSED]:
        data["acted_on_at"] = datetime.utcnow().isoformat()

    result = (
        supabase.table("recommendations")
        .update(data)
        .eq("id", recommendation_id)
        .execute()
    )

    return result.data[0]
