"""Contract management endpoints."""

import json
import os
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

import anthropic
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


from pydantic import BaseModel
from typing import Optional


# Q&A Request/Response models
class ContractQuery(BaseModel):
    question: str


class ContractQueryResponse(BaseModel):
    answer: str
    citations: list[str]


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


@router.post("/{contract_id}/query", response_model=ContractQueryResponse)
async def query_contract(
    contract_id: str,
    query: ContractQuery,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
):
    """Ask a question about a contract and get an AI-powered answer with citations."""
    # Fetch the contract
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

    contract = result.data

    # Build context from contract data
    key_terms = contract.get("key_terms", [])
    if isinstance(key_terms, str):
        try:
            key_terms = json.loads(key_terms)
        except json.JSONDecodeError:
            key_terms = [key_terms] if key_terms else []

    parties = contract.get("parties", [])
    if isinstance(parties, str):
        try:
            parties = json.loads(parties)
        except json.JSONDecodeError:
            parties = []

    risks = contract.get("risks", [])
    if isinstance(risks, str):
        try:
            risks = json.loads(risks)
        except json.JSONDecodeError:
            risks = []

    # Format the prompt
    prompt = f"""You are a contract analyst assistant. Your job is to answer questions about contracts based on the extracted data.

## Contract Information

**Provider:** {contract.get('provider_name', 'Unknown')}
**Type:** {contract.get('contract_type', 'Unknown')}
**Monthly Cost:** ${contract.get('monthly_cost', 'Not specified') or 'Not specified'}
**Annual Cost:** ${contract.get('annual_cost', 'Not specified') or 'Not specified'}
**Payment Frequency:** {contract.get('payment_frequency', 'Not specified') or 'Not specified'}
**Start Date:** {contract.get('start_date', 'Not specified') or 'Not specified'}
**End Date:** {contract.get('end_date', 'Not specified') or 'Not specified'}
**Auto-Renewal:** {'Yes' if contract.get('auto_renewal') else 'No'}
**Cancellation Notice:** {contract.get('cancellation_notice_days', 'Not specified') or 'Not specified'} days

**Key Terms:**
{chr(10).join(f"- {term}" for term in key_terms) if key_terms else "None extracted"}

**Parties:**
{chr(10).join(f"- {p.get('name', 'Unknown')} ({p.get('role', 'Unknown role')})" for p in parties) if parties else "None extracted"}

**Risks:**
{chr(10).join(f"- {r.get('title', 'Unknown')}: {r.get('description', '')}" for r in risks) if risks else "None identified"}

## Question
{query.question}

## Instructions
1. Answer the question based ONLY on the contract data provided
2. If the question cannot be answered from the available data, say so clearly
3. Provide specific citations from the contract data when possible
4. Be concise but thorough
5. Use plain language, avoiding legal jargon where possible

## Response Format
Return a JSON object with:
- "answer": Your answer to the question
- "citations": Array of specific quotes/text that support your answer (empty if not applicable)

Respond with ONLY valid JSON, no other text."""

    # Call Claude API
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse the JSON response
    try:
        response_data = json.loads(response_text)
        answer = response_data.get("answer", "Sorry, I couldn't parse the answer.")
        citations = response_data.get("citations", [])
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw response
        answer = response_text
        citations = []

    return ContractQueryResponse(answer=answer, citations=citations)
