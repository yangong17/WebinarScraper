"""
Simplified Webinar data model.
Only tracking: Source, Title, Air Date, Link
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Webinar(BaseModel):
    """Simplified webinar model - On Demand only."""
    
    source: str = Field(..., description="Source provider (Syndio, WorldatWork, Pave)")
    title: str = Field(..., description="Webinar title")
    air_date: Optional[str] = Field(None, description="Air date as string")
    link: str = Field(..., description="URL to webinar")
    
    # For deduplication
    @property
    def unique_id(self) -> str:
        return f"{self.source}::{self.link}"
