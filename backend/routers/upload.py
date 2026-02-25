"""File upload and contract extraction endpoints."""

import base64
import json
import logging
import traceback
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from supabase import create_client, Client

from backend.config import get_settings, Settings
from backend.models import Contract, ExtractionResult
from backend.services.extraction import extract_contract_from_pdf

logger = logging.getLogger(__name__)

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
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.post("/extract", response_model=ExtractionResult)
async def extract_contract(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
):
    """Upload a PDF and extract contract data using AI."""
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file content
    content = await file.read()

    # Check file size (10MB limit)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")

    # Extract contract data using Claude
    try:
        logger.info(f"Starting extraction for file: {file.filename}, size: {len(content)} bytes")
        extraction = await extract_contract_from_pdf(content)
        logger.info(f"Extraction completed successfully")
        return extraction
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


VALID_CONTRACT_TYPES = {'insurance', 'utility', 'subscription', 'rental', 'saas', 'service', 'other'}


@router.post("/confirm", response_model=Contract)
async def confirm_extraction(
    file: UploadFile = File(...),
    provider_name: str = "",
    contract_type: Optional[str] = None,
    monthly_cost: Optional[float] = None,
    annual_cost: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    auto_renewal: bool = True,
    cancellation_notice_days: Optional[int] = None,
    key_terms: Optional[str] = None,
    parties: Optional[str] = None,
    risks: Optional[str] = None,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Confirm extraction and save the contract."""
    # Validate required fields
    if not provider_name or not provider_name.strip():
        raise HTTPException(status_code=400, detail="Provider name is required")

    provider_name = provider_name.strip()

    # Validate contract_type if provided
    if contract_type and contract_type not in VALID_CONTRACT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid contract type. Must be one of: {', '.join(VALID_CONTRACT_TYPES)}"
        )

    # Validate costs are non-negative
    if monthly_cost is not None and monthly_cost < 0:
        raise HTTPException(status_code=400, detail="Monthly cost cannot be negative")
    if annual_cost is not None and annual_cost < 0:
        raise HTTPException(status_code=400, detail="Annual cost cannot be negative")

    # Validate cancellation notice days
    if cancellation_notice_days is not None and cancellation_notice_days < 0:
        raise HTTPException(status_code=400, detail="Cancellation notice days cannot be negative")

    # Read and upload file to Supabase Storage
    content = await file.read()
    file_path = f"{user_id}/{file.filename}"

    try:
        supabase.storage.from_("contracts").upload(
            file_path,
            content,
            {"content-type": "application/pdf"},
        )
    except Exception as e:
        # File might already exist, try to update
        try:
            supabase.storage.from_("contracts").update(
                file_path,
                content,
                {"content-type": "application/pdf"},
            )
        except Exception:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Create contract record
    contract_data = {
        "user_id": user_id,
        "provider_name": provider_name,
        "contract_type": contract_type,
        "monthly_cost": monthly_cost,
        "annual_cost": annual_cost,
        "start_date": start_date,
        "end_date": end_date,
        "auto_renewal": auto_renewal,
        "cancellation_notice_days": cancellation_notice_days,
        "file_path": file_path,
        "file_name": file.filename,
        "user_verified": True,
    }

    # Add key_terms, parties, and risks if provided (JSON strings from form data)
    if key_terms:
        try:
            contract_data["key_terms"] = json.loads(key_terms) if isinstance(key_terms, str) else key_terms
        except (json.JSONDecodeError, TypeError):
            pass  # Skip if invalid JSON

    if parties:
        try:
            contract_data["parties"] = json.loads(parties) if isinstance(parties, str) else parties
        except (json.JSONDecodeError, TypeError):
            pass

    if risks:
        try:
            contract_data["risks"] = json.loads(risks) if isinstance(risks, str) else risks
        except (json.JSONDecodeError, TypeError):
            pass

    # Remove None values
    contract_data = {k: v for k, v in contract_data.items() if v is not None}

    result = supabase.table("contracts").insert(contract_data).execute()

    return result.data[0]
