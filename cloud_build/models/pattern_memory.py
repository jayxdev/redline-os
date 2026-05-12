from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class PatternMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str # winning_hook, winning_format, failed_pattern, caption_pattern
    title: str
    statement: str
    evidence_video_ids: List[str] = []
    evidence_analysis_ids: List[str] = []
    confidence: str = "medium" # low, medium, high
    status: str = "candidate" # candidate, confirmed, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
