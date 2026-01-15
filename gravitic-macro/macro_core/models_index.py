from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MarketMetadata(BaseModel):
    """
    Represents the searchable metadata for a Polymarket event.
    Optimized for local indexing and search.
    """
    event_id: str = Field(..., description="Polymarket condition_id")
    market_id: str = Field(..., description="Specific market/contract ID")
    title: str = Field(..., description="Event title/question")
    description: Optional[str] = Field(None, description="Event description")
    volume_usd: float = Field(0.0, description="Total volume")
    slug: Optional[str] = Field(None, description="URL slug for the event")
    tags: str = Field("", description="Comma-separated tags")
    created_at: Optional[datetime] = Field(None)
    end_date: Optional[datetime] = Field(None)
    
class SearchResult(BaseModel):
    event_id: str
    title: str
    match_score: float = 0.0  # Placeholder for future ranking
