"""Contract extraction service using Claude AI."""

import base64
import json
from backend.models import ExtractionResult
from backend.config import get_settings

# Import the execution layer script
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from execution.claude_extractor import extract_contract_data


async def extract_contract_from_pdf(pdf_bytes: bytes) -> ExtractionResult:
    """Extract structured contract data from a PDF using Claude Vision API."""
    settings = get_settings()

    # Use the execution layer script
    result = extract_contract_data(pdf_bytes, settings.anthropic_api_key)

    return ExtractionResult(
        provider_name=result.get("provider_name"),
        contract_type=result.get("contract_type"),
        monthly_cost=result.get("monthly_cost"),
        annual_cost=result.get("annual_cost"),
        payment_frequency=result.get("payment_frequency"),
        start_date=result.get("start_date"),
        end_date=result.get("end_date"),
        auto_renewal=result.get("auto_renewal"),
        cancellation_notice_days=result.get("cancellation_notice_days"),
        key_terms=result.get("key_terms", []),
        confidence=result.get("confidence", 0.0),
    )
