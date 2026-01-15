from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Entity(Base):
    """
    SOTA Entity Tracking: Manages unique companies and their global scrape freshness.
    """
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    canonical_name = Column(String, index=True)
    last_scraped_at = Column(DateTime, nullable=True)
    
    signals = relationship("ScrapedSignal", back_populates="entity", cascade="all, delete-orphan")

class ScrapedSignal(Base):
    """
    SOTA Signal Event Store: Stores flexible JSON payloads for alternative data signals.
    """
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    provider = Column(String, index=True, nullable=False) # 'hiring', 'shipping', 'digital'
    signal_value = Column(Float, nullable=True) # Normalized score (e.g. velocity)
    raw_payload = Column(JSON, nullable=False) # Full structured data from Firecrawl/LLM
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    entity = relationship("Entity", back_populates="signals")
