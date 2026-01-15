import sqlite3
import logging
import os
from typing import List, Optional
from macro_core.models_index import MarketMetadata
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketIndex:
    """
    Persistence layer for the Local Market Index.
    Uses SQLite FTS5 for full-text search capability.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            # Use absolute path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.abspath(os.path.join(base_dir, "..", "..", "market_index.db"))
            
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database with FTS5 support."""
        with sqlite3.connect(self.db_path) as conn:
            # Main table for metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    market_id TEXT,
                    title TEXT,
                    description TEXT,
                    slug TEXT,
                    tags TEXT,
                    volume_usd REAL,
                    end_date TEXT
                )
            """)
            
            # FTS5 Virtual Table for Search
            # We index title, description, and tags
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS market_fts USING fts5(
                        event_id, title, description, tags, slug
                    )
                """)
            except Exception as e:
                logger.warning(f"FTS5 might not be supported on this SQLite version: {e}")

    def upsert_markets(self, markets: List[MarketMetadata]) -> int:
        """
        Inserts or updates markets in the local index.
        Returns count of upserted items.
        """
        count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                for m in markets:
                    # 1. Update Main Table
                    conn.execute("""
                        INSERT INTO market_metadata (
                            event_id, market_id, title, description, slug, tags, volume_usd, end_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(event_id) DO UPDATE SET
                            volume_usd = excluded.volume_usd,
                            title = excluded.title
                    """, (
                        m.event_id, m.market_id, m.title, m.description, 
                        m.slug, m.tags, m.volume_usd,
                        m.end_date.isoformat() if m.end_date else None
                    ))
                    
                    # 2. Update FTS Index (Delete + Insert to ensure consistent state)
                    # Note: Ideally we use triggers, but manual sync is fine for this batch size
                    conn.execute("DELETE FROM market_fts WHERE event_id = ?", (m.event_id,))
                    conn.execute("""
                        INSERT INTO market_fts (event_id, title, description, tags, slug)
                        VALUES (?, ?, ?, ?, ?)
                    """, (m.event_id, m.title, m.description or "", m.tags, m.slug or ""))
                    
                    count += 1
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to upsert markets: {e}")
        return count

    def search(self, query: str, limit: int = 20) -> List[MarketMetadata]:
        """
        Performs a Full-Text Search on the local index.
        """
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # FTS Match Query
                # We join back to metadata to get volume for sorting/ranking if needed
                cursor = conn.execute("""
                    SELECT m.* 
                    FROM market_fts f
                    JOIN market_metadata m ON f.event_id = m.event_id
                    WHERE market_fts MATCH ?
                    ORDER BY m.volume_usd DESC
                    LIMIT ?
                """, (query, limit)) 
                
                for row in cursor:
                    results.append(MarketMetadata(
                        event_id=row['event_id'],
                        market_id=row['market_id'] or "",
                        title=row['title'],
                        description=row['description'],
                        slug=row['slug'],
                        tags=row['tags'] or "",
                        volume_usd=row['volume_usd'],
                        end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None
                    ))
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Fallback to simple LIKE if FTS fails or syntax error
            return self._search_fallback(query, limit)
            
        return results

    def _search_fallback(self, query: str, limit: int = 20) -> List[MarketMetadata]:
        """Simple LIKE search if FTS fails."""
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM market_metadata 
                WHERE title LIKE ? OR tags LIKE ?
                ORDER BY volume_usd DESC LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit))
            for row in cursor:
                 results.append(MarketMetadata(
                        event_id=row['event_id'],
                        market_id=row['market_id'] or "",
                        title=row['title'],
                        description=row['description'],
                        slug=row['slug'],
                        tags=row['tags'] or "",
                        volume_usd=row['volume_usd'],
                        end_date=datetime.fromisoformat(row['end_date']) if row['end_date'] else None
                    ))
        return results

    def get_count(self) -> int:
        """Returns the total number of markets in the index."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM market_metadata")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def is_empty(self) -> bool:
        """Returns True if the index has no markets."""
        return self.get_count() == 0

    def get_last_update_time(self) -> Optional[datetime]:
        """
        Returns the modification time of the database file.
        Used to detect staleness.
        """
        try:
            if os.path.exists(self.db_path):
                mtime = os.path.getmtime(self.db_path)
                return datetime.fromtimestamp(mtime)
        except Exception:
            pass
        return None

    def is_stale(self, max_age_hours: int = 6) -> bool:
        """
        Returns True if the index hasn't been updated in max_age_hours.
        """
        last_update = self.get_last_update_time()
        if not last_update:
            return True
        age = datetime.now() - last_update
        return age.total_seconds() > (max_age_hours * 3600)
