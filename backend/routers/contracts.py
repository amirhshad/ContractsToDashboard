"""Contract management endpoints."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from supabase import create_client, Client

from backend.config import get_settings, Settings
from backend.models import (
    Contract,
    ContractCreate,
    ContractUpdate,
    ContractSummary,
)

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


@router.get("", response_model=list[Contract])
async def list_contracts(
    contract_type: Optional[str] = None,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """List all contracts for the authenticated user."""
    query = supabase.table("contracts").select("*").eq("user_id", user_id)

    if contract_type:
        query = query.eq("contract_type", contract_type)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/summary", response_model=ContractSummary)
async def get_summary(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Get dashboard summary statistics."""
    result = supabase.table("contracts").select("*").eq("user_id", user_id).execute()
    contracts = result.data

    total_monthly = Decimal("0")
    total_annual = Decimal("0")
    by_type: dict[str, int] = {}
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

    return ContractSummary(
        total_contracts=len(contracts),
        total_monthly_spend=total_monthly,
        total_annual_spend=total_annual,
        contracts_by_type=by_type,
        expiring_soon=expiring_soon,
        auto_renewal_count=auto_renewal_count,
    )


@router.get("/{contract_id}", response_model=Contract)
async def get_contract(
    contract_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Get a single contract by ID."""
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


@router.post("", response_model=Contract)
async def create_contract(
    contract: ContractCreate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Create a new contract."""
    data = contract.model_dump(exclude_none=True)
    data["user_id"] = user_id

    result = supabase.table("contracts").insert(data).execute()
    return result.data[0]


@router.put("/{contract_id}", response_model=Contract)
async def update_contract(
    contract_id: str,
    contract: ContractUpdate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Update an existing contract."""
    # Verify ownership
    existing = (
        supabase.table("contracts")
        .select("id")
        .eq("id", contract_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Contract not found")

    data = contract.model_dump(exclude_none=True)
    result = supabase.table("contracts").update(data).eq("id", contract_id).execute()

    return result.data[0]


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
):
    """Delete a contract."""
    # Verify ownership
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

    # Delete file from storage if exists
    if existing.data.get("file_path"):
        try:
            supabase.storage.from_("contracts").remove([existing.data["file_path"]])
        except Exception:
            pass  # File might already be deleted

    supabase.table("contracts").delete().eq("id", contract_id).execute()

    return {"status": "deleted"}
