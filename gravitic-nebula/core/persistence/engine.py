import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .models import Entity, ScrapedSignal

logger = logging.getLogger(__name__)

class SignalStore:
    """
    SOTA Persistence Engine: Manages caching and retrieval to prevent 'doing work twice'.
    """
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        init_db() # Ensure tables exist on init

    def get_session(self) -> Session:
        return SessionLocal()

    def get_latest_signal(self, ticker: str, provider: str) -> Optional[Dict]:
        """
        Check if a fresh signal exists for the given ticker and provider.
        Returns the data if it's within the TTL, otherwise None.
        """
        session = self.get_session()
        try:
            # 1. Check if entity exists
            entity = session.query(Entity).filter(Entity.ticker == ticker).first()
            if not entity:
                return None

            # 2. Find latest signal for this provider
            latest = session.query(ScrapedSignal)\
                .filter(ScrapedSignal.entity_id == entity.id)\
                .filter(ScrapedSignal.provider == provider)\
                .order_by(ScrapedSignal.timestamp.desc())\
                .first()

            if not latest:
                return None

            # 3. Check TTL
            if datetime.utcnow() - latest.timestamp < timedelta(hours=self.ttl_hours):
                logger.info(f"✅ SOTA Cache Hit for {ticker} [{provider}]. Signal is fresh.")
                return latest.raw_payload
            
            logger.info(f"⌛ SOTA Cache Stale for {ticker} [{provider}]. Signal expired.")
            return None
        finally:
            session.close()

    def save_signal(self, ticker: str, provider: str, payload: Dict, signal_value: float = 0.0, canonical_name: Optional[str] = None):
        """
        Store a new signal event and update the entity's harvest timestamp.
        """
        session = self.get_session()
        try:
            # Ensure entity exists
            entity = session.query(Entity).filter(Entity.ticker == ticker).first()
            if not entity:
                entity = Entity(ticker=ticker, canonical_name=canonical_name or ticker)
                session.add(entity)
                session.commit()
                session.refresh(entity)
            
            # Create signal event
            new_signal = ScrapedSignal(
                entity_id=entity.id,
                provider=provider,
                signal_value=signal_value,
                raw_payload=payload,
                timestamp=datetime.utcnow()
            )
            
            # Update entity state
            entity.last_scraped_at = datetime.utcnow()
            if canonical_name:
                entity.canonical_name = canonical_name
                
            session.add(new_signal)
            session.commit()
            logger.info(f"💾 Persisted {provider} signal for {ticker} [ID: {new_signal.id}]")
        finally:
            session.close()

# Singleton for easy access across scrapers
default_store = SignalStore()
