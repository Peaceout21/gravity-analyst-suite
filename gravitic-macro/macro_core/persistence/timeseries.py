"""
Time-Series Persistence for Macro Event Probabilities.
Uses SQLite with (event_id, timestamp) composite key for snapshots.
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from macro_core.models import MacroEvent

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "macro_signals.db"

class TimeSeriesPersistence:
    """
    Manages time-series storage of macro event probability snapshots.
    """

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS macro_probabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_title TEXT NOT NULL,
                    category TEXT,
                    sector TEXT,
                    related_ticker TEXT,
                    probability_yes REAL NOT NULL,
                    volume_usd REAL,
                    source TEXT DEFAULT 'polymarket',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(event_id, timestamp)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_ts 
                ON macro_probabilities(event_id, timestamp DESC)
            """)
            conn.commit()
        logger.info(f"Initialized macro DB at {self.db_path}")

    def save_snapshot(self, event: MacroEvent) -> bool:
        """
        Saves a single event probability snapshot.
        
        Returns:
            True if saved successfully, False if duplicate.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO macro_probabilities 
                    (event_id, event_title, category, sector, related_ticker, probability_yes, volume_usd, source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.title,
                    event.category,
                    event.sector,
                    event.related_ticker,
                    event.probability_yes,
                    event.volume_usd,
                    event.source,
                    event.timestamp.isoformat()
                ))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"Duplicate snapshot for {event.event_id} at {event.timestamp}")
            return False
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False

    def save_batch(self, events: List[MacroEvent]) -> int:
        """
        Saves multiple events in a single transaction.
        
        Returns:
            Number of events successfully saved.
        """
        saved = 0
        for event in events:
            if self.save_snapshot(event):
                saved += 1
        logger.info(f"Saved {saved}/{len(events)} event snapshots")
        return saved

    def get_event_history(self, event_id: str, days: int = 7) -> List[dict]:
        """
        Returns probability history for a specific event.
        
        Args:
            event_id: The event condition ID.
            days: Number of days of history to fetch.
            
        Returns:
            List of dicts with timestamp and probability_yes.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT timestamp, probability_yes, volume_usd
                FROM macro_probabilities
                WHERE event_id = ?
                AND timestamp >= datetime('now', ?)
                ORDER BY timestamp ASC
            """, (event_id, f"-{days} days"))
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_probabilities(self, limit: int = 20) -> List[dict]:
        """Returns the most recent probability for each tracked event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT event_id, event_title, category, sector, related_ticker, 
                       probability_yes, volume_usd, MAX(timestamp) as timestamp
                FROM macro_probabilities
                GROUP BY event_id
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test persistence
    db = TimeSeriesPersistence()
    
    # Mock event
    test_event = MacroEvent(
        event_id="test_fed_rate_001",
        title="Will Fed cut rates in March 2025?",
        category="Economics",
        probability_yes=0.42,
        volume_usd=1500000.0
    )
    
    db.save_snapshot(test_event)
    history = db.get_event_history("test_fed_rate_001")
    print(f"History: {history}")
