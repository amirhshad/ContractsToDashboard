"""Vercel serverless function entry point for FastAPI backend."""

import os
import sys

# Add the project root to sys.path for imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, Request, HTTPException, Header, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import json

# Initialize FastAPI app
app = FastAPI(title="Contract Optimizer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import Supabase client
try:
    from supabase import create_client
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    supabase_available = SUPABASE_URL and SUPABASE_SERVICE_KEY
except ImportError:
    supabase_available = False


def get_supabase():
    """Get Supabase client with service key."""
    if not supabase_available:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


async def get_user_id(authorization: str = Header(...)) -> str:
    """Extract user ID from JWT token."""
    if not supabase_available:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

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


@app.get("/api/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Contract Optimizer API"}


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.get("/api/contracts")
async def list_contracts(
    contract_type: Optional[str] = None,
    user_id: str = Depends(get_user_id),
):
    """List all contracts for the authenticated user."""
    supabase = get_supabase()
    query = supabase.table("contracts").select("*").eq("user_id", user_id)

    if contract_type:
        query = query.eq("contract_type", contract_type)

    result = query.order("created_at", desc=True).execute()
    return result.data


@app.get("/api/contracts/summary")
async def get_summary(user_id: str = Depends(get_user_id)):
    """Get dashboard summary statistics."""
    from datetime import date, timedelta
    from decimal import Decimal

    supabase = get_supabase()
    result = supabase.table("contracts").select("*").eq("user_id", user_id).execute()
    contracts = result.data

    total_monthly = Decimal("0")
    total_annual = Decimal("0")
    by_type = {}
    expiring_soon = 0
    auto_renewal_count = 0

    today = date.today()
    thirty_days = today + timedelta(days=30)

    for c in contracts:
        if c.get("monthly_cost"):
            total_monthly += Decimal(str(c["monthly_cost"]))
        if c.get("annual_cost"):
            total_annual += Decimal(str(c["annual_cost"]))

        ctype = c.get("contract_type") or "other"
        by_type[ctype] = by_type.get(ctype, 0) + 1

        if c.get("end_date"):
            end = date.fromisoformat(c["end_date"])
            if today <= end <= thirty_days:
                expiring_soon += 1

        if c.get("auto_renewal"):
            auto_renewal_count += 1

    return {
        "total_contracts": len(contracts),
        "total_monthly_spend": float(total_monthly),
        "total_annual_spend": float(total_annual),
        "contracts_by_type": by_type,
        "expiring_soon": expiring_soon,
        "auto_renewal_count": auto_renewal_count,
    }


@app.get("/api/contracts/{contract_id}")
async def get_contract(contract_id: str, user_id: str = Depends(get_user_id)):
    """Get a single contract by ID."""
    supabase = get_supabase()
    result = (
        supabase.table("contracts")
        .select("*")
        .eq("id", contract_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Contract not found")

    return result.data


@app.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: str, user_id: str = Depends(get_user_id)):
    """Delete a contract."""
    supabase = get_supabase()

    existing = (
        supabase.table("contracts")
        .select("id, file_path")
        .eq("id", contract_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Contract not found")

    if existing.data.get("file_path"):
        try:
            supabase.storage.from_("contracts").remove([existing.data["file_path"]])
        except Exception:
            pass

    supabase.table("contracts").delete().eq("id", contract_id).execute()
    return {"status": "deleted"}


@app.get("/api/recommendations")
async def list_recommendations(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user_id: str = Depends(get_user_id),
):
    """List all recommendations for the authenticated user."""
    supabase = get_supabase()
    query = supabase.table("recommendations").select("*").eq("user_id", user_id)

    if status:
        query = query.eq("status", status)
    if priority:
        query = query.eq("priority", priority)

    result = query.order("created_at", desc=True).execute()
    return result.data


@app.post("/api/upload/extract")
async def extract_contract(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
):
    """Extract contract data from uploaded PDF using Claude Vision API."""
    import anthropic
    import base64

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Anthropic API not configured")

    content = await file.read()
    base64_content = base64.standard_b64encode(content).decode("utf-8")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    extraction_prompt = """Analyze this contract document and extract the following information in JSON format:
    {
        "provider_name": "Company/service provider name",
        "contract_type": "One of: insurance, utility, subscription, rental, saas, service, other",
        "monthly_cost": "Monthly cost as a number or null",
        "annual_cost": "Annual cost as a number or null",
        "start_date": "Start date in YYYY-MM-DD format or null",
        "end_date": "End date in YYYY-MM-DD format or null",
        "auto_renewal": true/false,
        "cancellation_notice_days": "Number of days notice required or null",
        "key_terms": ["List of important terms or conditions"],
        "confidence": 0.0-1.0 confidence score
    }

    Return ONLY the JSON object, no additional text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64_content,
                            },
                        },
                        {
                            "type": "text",
                            "text": extraction_prompt,
                        },
                    ],
                }
            ],
        )

        result_text = response.content[0].text

        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        extraction = json.loads(result_text.strip())
        extraction["file_name"] = file.filename

        return extraction

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


VALID_CONTRACT_TYPES = {'insurance', 'utility', 'subscription', 'rental', 'saas', 'service', 'other'}


@app.post("/api/upload/confirm")
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
    user_id: str = Depends(get_user_id),
):
    """Confirm extraction and save the contract."""
    if not provider_name or not provider_name.strip():
        raise HTTPException(status_code=400, detail="Provider name is required")

    provider_name = provider_name.strip()

    if contract_type and contract_type not in VALID_CONTRACT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid contract type. Must be one of: {', '.join(VALID_CONTRACT_TYPES)}"
        )

    if monthly_cost is not None and monthly_cost < 0:
        raise HTTPException(status_code=400, detail="Monthly cost cannot be negative")
    if annual_cost is not None and annual_cost < 0:
        raise HTTPException(status_code=400, detail="Annual cost cannot be negative")
    if cancellation_notice_days is not None and cancellation_notice_days < 0:
        raise HTTPException(status_code=400, detail="Cancellation notice days cannot be negative")

    supabase = get_supabase()

    content = await file.read()
    file_path = f"{user_id}/{file.filename}"

    try:
        supabase.storage.from_("contracts").upload(
            file_path,
            content,
            {"content-type": "application/pdf"}
        )
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

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

    contract_data = {k: v for k, v in contract_data.items() if v is not None}

    result = supabase.table("contracts").insert(contract_data).execute()

    return result.data[0]


# Export the app for Vercel
handler = app
