"""
Pydantic models for Macro Signals (Prediction Markets).
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class MacroEvent(BaseModel):
    """Represents a single prediction market event."""
    event_id: str = Field(..., description="Unique identifier for the event (Polymarket condition_id)")
    title: str = Field(..., description="Event question (e.g., 'Will Fed cut rates in March?')")
    category: Optional[str] = Field(None, description="Event category (e.g., 'Politics', 'Crypto')")
    sector: Optional[str] = Field(None, description="Investment sector (e.g., 'AI', 'Macro', 'Energy')")
    related_ticker: Optional[str] = Field(None, description="Ticker symbol linked to this event")
    probability_yes: float = Field(..., ge=0.0, le=1.0, description="Probability of 'Yes' outcome (0-1)")
    outcomes: Optional[List[Dict]] = Field(None, description="List of possible outcomes and their probabilities for multi-choice events")
    volume_usd: Optional[float] = Field(None, description="Total trading volume in USD")
    end_date: Optional[datetime] = Field(None, description="Resolution date of the event")
    source: str = Field(default="polymarket", description="Data source identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Snapshot timestamp")

class MacroEventList(BaseModel):
    """Container for a list of macro events."""
    events: List[MacroEvent]
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    keyword_filter: Optional[str] = None
