"""
Simplified SQLite database manager with duplicate checking.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set
from .models import Webinar


class DatabaseManager:
    """Manages SQLite database for webinar records."""
    
    def __init__(self, db_path: str = "data/webinars.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webinars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unique_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    air_date TEXT,
                    link TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON webinars(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_link ON webinars(link)")
            conn.commit()
    
    def get_existing_links(self, source: str) -> Set[str]:
        """Get all existing links for a source to avoid re-scraping."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT link FROM webinars WHERE source = ?", (source,)
            )
            return {row[0] for row in cursor.fetchall()}
    
    def link_exists(self, link: str) -> bool:
        """Check if a link already exists in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM webinars WHERE link = ?", (link,)
            )
            return cursor.fetchone() is not None
    
    def upsert_webinar(self, webinar: Webinar) -> bool:
        """Insert or update a webinar. Returns True if inserted."""
        unique_id = webinar.unique_id
        now = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM webinars WHERE unique_id = ?", (unique_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                conn.execute("""
                    UPDATE webinars SET
                        title = ?, air_date = ?, last_updated = ?
                    WHERE unique_id = ?
                """, (webinar.title, webinar.air_date, now, unique_id))
                conn.commit()
                return False
            else:
                conn.execute("""
                    INSERT INTO webinars (unique_id, source, title, air_date, link, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (unique_id, webinar.source, webinar.title, webinar.air_date, webinar.link, now))
                conn.commit()
                return True
    
    def bulk_upsert(self, webinars: List[Webinar]) -> tuple[int, int]:
        """Bulk insert/update. Returns (inserted, updated)."""
        inserted = updated = 0
        for w in webinars:
            if self.upsert_webinar(w):
                inserted += 1
            else:
                updated += 1
        return inserted, updated
    
    def get_all(self) -> List[dict]:
        """Get all webinars."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT source, title, air_date, link FROM webinars ORDER BY source, title")
            return [dict(row) for row in cursor.fetchall()]
