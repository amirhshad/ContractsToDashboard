"""Contract data models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ContractType(str, Enum):
    INSURANCE = "insurance"
    UTILITY = "utility"
    SUBSCRIPTION = "subscription"
    RENTAL = "rental"
    SAAS = "saas"
    SERVICE = "service"
    OTHER = "other"


class PaymentFrequency(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    ONE_TIME = "one-time"
    OTHER = "other"


class ContractBase(BaseModel):
    """Base contract fields."""

    provider_name: str
    contract_type: Optional[ContractType] = None
    monthly_cost: Optional[Decimal] = None
    annual_cost: Optional[Decimal] = None
    currency: str = "USD"
    payment_frequency: Optional[PaymentFrequency] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    auto_renewal: bool = True
    cancellation_notice_days: Optional[int] = None
    key_terms: list[str] = Field(default_factory=list)


class ContractCreate(ContractBase):
    """Contract creation payload."""

    file_path: Optional[str] = None
    file_name: Optional[str] = None


class ContractUpdate(BaseModel):
    """Contract update payload - all fields optional."""

    provider_name: Optional[str] = None
    contract_type: Optional[ContractType] = None
    monthly_cost: Optional[Decimal] = None
    annual_cost: Optional[Decimal] = None
    currency: Optional[str] = None
    payment_frequency: Optional[PaymentFrequency] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    auto_renewal: Optional[bool] = None
    cancellation_notice_days: Optional[int] = None
    key_terms: Optional[list[str]] = None
    user_verified: Optional[bool] = None


class Contract(ContractBase):
    """Full contract with all fields."""

    id: str
    user_id: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    extracted_text: Optional[str] = None
    extraction_confidence: Optional[float] = None
    user_verified: bool = False
    raw_extraction: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractSummary(BaseModel):
    """Dashboard summary statistics."""

    total_contracts: int
    total_monthly_spend: Decimal
    total_annual_spend: Decimal
    contracts_by_type: dict[str, int]
    expiring_soon: int  # Within 30 days
    auto_renewal_count: int


class ExtractionResult(BaseModel):
    """Result from AI contract extraction."""

    provider_name: Optional[str] = None
    contract_type: Optional[str] = None
    monthly_cost: Optional[float] = None
    annual_cost: Optional[float] = None
    payment_frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    auto_renewal: Optional[bool] = None
    cancellation_notice_days: Optional[int] = None
    key_terms: list[str] = Field(default_factory=list)
    confidence: float = 0.0
