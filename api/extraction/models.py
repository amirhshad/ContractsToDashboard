"""Pydantic models for contract extraction validation."""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


# Currency symbol to code mapping
CURRENCY_SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "C$": "CAD",
    "A$": "AUD",
    "CA$": "CAD",
    "AU$": "AUD",
}

# Valid currency codes
VALID_CURRENCIES = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY"}


class ContractParty(BaseModel):
    """A party involved in the contract."""

    name: str = Field(description="Full legal name of the party")
    role: str = Field(description="Role: provider, client, insurer, insured, landlord, tenant, etc.")


class ContractRisk(BaseModel):
    """A risk or concern identified in the contract."""

    title: str = Field(description="Short risk title")
    description: str = Field(description="Description of the risk or concern")
    severity: Literal["high", "medium", "low"] = Field(default="medium")

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v):
        """Normalize severity to lowercase."""
        if isinstance(v, str):
            v = v.lower().strip()
            if v in ("high", "medium", "low"):
                return v
        return "medium"


class DocumentAnalyzed(BaseModel):
    """Information about a document that was analyzed."""

    filename: str = Field(description="Original filename")
    document_type: str = Field(
        default="other",
        description="Type: main_agreement, sow, terms_conditions, amendment, addendum, exhibit, schedule, other"
    )
    summary: str = Field(default="", description="Brief summary of document contents")


class ExtractionResult(BaseModel):
    """Validated extraction result from Claude."""

    provider_name: str | None = Field(default=None, description="Company/service provider name")
    contract_type: str | None = Field(default=None, description="Contract type category")
    monthly_cost: float | None = Field(default=None, description="Monthly cost amount")
    annual_cost: float | None = Field(default=None, description="Annual cost amount")
    currency: str = Field(default="USD", description="Currency code (USD, EUR, GBP, etc.)")
    payment_frequency: str | None = Field(default=None, description="Payment frequency")
    start_date: str | None = Field(default=None, description="Start date in YYYY-MM-DD format")
    end_date: str | None = Field(default=None, description="End date in YYYY-MM-DD format")
    auto_renewal: bool | None = Field(default=None, description="Whether contract auto-renews")
    cancellation_notice_days: int | None = Field(default=None, description="Days notice required to cancel")
    key_terms: list[str] = Field(default_factory=list, description="Important terms and conditions")
    parties: list[ContractParty] = Field(default_factory=list, description="Parties involved in contract")
    risks: list[ContractRisk] = Field(default_factory=list, description="Identified risks and concerns")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")
    documents_analyzed: list[DocumentAnalyzed] = Field(default_factory=list, description="Documents that were analyzed")

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, v):
        """Normalize currency symbols to codes."""
        if v is None:
            return "USD"

        v = str(v).strip()

        # Check if it's a symbol
        if v in CURRENCY_SYMBOL_MAP:
            return CURRENCY_SYMBOL_MAP[v]

        # Normalize to uppercase
        v_upper = v.upper()

        # Check if it's a valid currency code
        if v_upper in VALID_CURRENCIES:
            return v_upper

        # Default to USD for unknown
        return "USD"

    @field_validator("contract_type", mode="before")
    @classmethod
    def normalize_contract_type(cls, v):
        """Normalize contract type to lowercase."""
        if v is None:
            return None
        return str(v).lower().strip()

    @field_validator("payment_frequency", mode="before")
    @classmethod
    def normalize_payment_frequency(cls, v):
        """Normalize payment frequency to lowercase."""
        if v is None:
            return None
        return str(v).lower().strip()


def parse_extraction_result(raw_data: dict) -> ExtractionResult:
    """
    Parse raw extraction data into a validated ExtractionResult.

    Uses Pydantic for validation and normalization.
    Falls back gracefully on validation errors.
    """
    try:
        return ExtractionResult.model_validate(raw_data)
    except Exception:
        # Fallback: return with defaults for fields that failed validation
        safe_data = {}

        # Copy simple fields with type coercion
        for field in ["provider_name", "contract_type", "payment_frequency", "start_date", "end_date"]:
            if field in raw_data and raw_data[field] is not None:
                safe_data[field] = str(raw_data[field])

        # Numeric fields
        for field in ["monthly_cost", "annual_cost"]:
            if field in raw_data and raw_data[field] is not None:
                try:
                    safe_data[field] = float(raw_data[field])
                except (ValueError, TypeError):
                    pass

        if "cancellation_notice_days" in raw_data and raw_data["cancellation_notice_days"] is not None:
            try:
                safe_data["cancellation_notice_days"] = int(raw_data["cancellation_notice_days"])
            except (ValueError, TypeError):
                pass

        # Boolean
        if "auto_renewal" in raw_data:
            safe_data["auto_renewal"] = bool(raw_data["auto_renewal"])

        # Confidence
        try:
            safe_data["confidence"] = float(raw_data.get("confidence", 0.0))
        except (ValueError, TypeError):
            safe_data["confidence"] = 0.0

        # Lists - just copy as-is
        safe_data["key_terms"] = raw_data.get("key_terms", [])
        safe_data["parties"] = raw_data.get("parties", [])
        safe_data["risks"] = raw_data.get("risks", [])
        safe_data["documents_analyzed"] = raw_data.get("documents_analyzed", [])

        # Currency
        safe_data["currency"] = raw_data.get("currency", "USD")

        try:
            return ExtractionResult.model_validate(safe_data)
        except Exception:
            # Ultimate fallback
            return ExtractionResult()
