"""Recommendation data models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class RecommendationType(str, Enum):
    COST_REDUCTION = "cost_reduction"
    CONSOLIDATION = "consolidation"
    RISK_ALERT = "risk_alert"
    RENEWAL_REMINDER = "renewal_reminder"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"


class RecommendationBase(BaseModel):
    """Base recommendation fields."""

    type: RecommendationType
    title: str
    description: str
    estimated_savings: Optional[Decimal] = None
    priority: Priority = Priority.MEDIUM


class RecommendationCreate(RecommendationBase):
    """Recommendation creation payload."""

    contract_id: Optional[str] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None


class RecommendationUpdate(BaseModel):
    """Recommendation update payload."""

    status: Optional[RecommendationStatus] = None


class Recommendation(RecommendationBase):
    """Full recommendation with all fields."""

    id: str
    user_id: str
    contract_id: Optional[str] = None
    status: RecommendationStatus = RecommendationStatus.PENDING
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    acted_on_at: Optional[datetime] = None

    class Config:
        from_attributes = True
