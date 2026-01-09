"""
Pydantic schemas for Market Sentinel API.

Defines request/response models and the Signal Packet schema.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Severity(str, Enum):
    """Severity level enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EntityType(str, Enum):
    """Entity type enumeration."""
    ORGANIZATION = "organization"
    PORT = "port"
    COUNTRY = "country"
    VESSEL = "vessel"
    COMMODITY = "commodity"


class AffectedLane(BaseModel):
    """Affected shipping lane with risk assessment."""
    origin: str = Field(..., description="Origin location code")
    destination: str = Field(..., description="Destination location code")
    risk: RiskLevel = Field(..., description="Risk level: low, medium, or high")


class Entity(BaseModel):
    """Named entity extracted from events."""
    name: str = Field(..., description="Entity name")
    type: EntityType = Field(..., description="Entity type")


class Citation(BaseModel):
    """Source citation with URL."""
    title: str = Field(..., description="Article or source title")
    url: str = Field(..., description="Source URL")


class SignalPacket(BaseModel):
    """
    Final output schema for Market Sentinel workflow.
    
    This is the validated JSON output from the orchestrator agent.
    """
    signal_id: str = Field(
        ..., 
        pattern=r"^SIG-\d{4}-\d{2}-\d{2}-\d{5}$", 
        description="Signal ID: SIG-YYYY-MM-DD-XXXXX"
    )
    timestamp_utc: str = Field(..., description="ISO8601 timestamp")
    summary: str = Field(..., description="Human-readable summary of the signal")
    affected_lanes: list[AffectedLane] = Field(
        default_factory=list, 
        description="Affected shipping lanes"
    )
    entities: list[Entity] = Field(
        default_factory=list, 
        description="Named entities"
    )
    severity: Severity = Field(..., description="Signal severity level")
    expected_horizon_days: int = Field(
        ..., 
        ge=0, 
        description="Expected impact horizon in days"
    )
    recommended_next_flows: list[str] = Field(
        default_factory=list, 
        description="Recommended downstream workflows"
    )
    citations: list[Citation] = Field(
        default_factory=list, 
        description="Source citations"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score 0.0-1.0"
    )
    debug: Optional[dict[str, Any]] = Field(
        default=None, 
        description="Optional debug information"
    )


class SensitivityConfig(BaseModel):
    """Sensitivity configuration for signal detection."""
    min_severity: Severity = Field(
        default=Severity.MEDIUM, 
        description="Minimum severity to report"
    )
    min_confidence: float = Field(
        default=0.6, 
        ge=0.0, 
        le=1.0, 
        description="Minimum confidence threshold"
    )


class MarketSentinelRequest(BaseModel):
    """Request body for Market Sentinel endpoint."""
    watchlist: dict[str, Any] = Field(
        ..., 
        description="Watchlist configuration with lanes and entities"
    )
    time_window_hours: int = Field(
        default=24, 
        ge=1, 
        le=168, 
        description="Time window in hours for news search"
    )
    sensitivity: SensitivityConfig = Field(
        default_factory=SensitivityConfig, 
        description="Sensitivity thresholds"
    )
    active_shipments_subset: Optional[list[str]] = Field(
        default=None, 
        description="Optional shipment IDs to focus on"
    )
    returns_symbols: list[str] = Field(
        default=["^spx"], 
        description="Stock symbols for returns analysis"
    )
    returns_days: int = Field(
        default=10, 
        ge=1, 
        le=365, 
        description="Days of historical returns to analyze"
    )


class MarketSentinelResponse(BaseModel):
    """Response from Market Sentinel endpoint."""
    thread_id: str = Field(..., description="Azure AI Foundry thread ID")
    signal_packet: SignalPacket = Field(..., description="Validated Signal Packet")
    raw_text: str = Field(..., description="Raw text output from orchestrator")
    request_echo: dict[str, Any] = Field(..., description="Echo of the original request")


class ReturnsSnapshot(BaseModel):
    """Market returns snapshot from pandas-datareader."""
    symbol: str = Field(..., description="Stock symbol")
    period_days: int = Field(..., description="Analysis period in days")
    start_date: str = Field(..., description="Start date ISO8601")
    end_date: str = Field(..., description="End date ISO8601")
    start_price: float = Field(..., description="Starting price")
    end_price: float = Field(..., description="Ending price")
    total_return_pct: float = Field(..., description="Total return percentage")
    daily_volatility_pct: float = Field(..., description="Daily volatility (std dev) percentage")
    annualized_volatility_pct: float = Field(..., description="Annualized volatility percentage")


