from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Dict
import uuid

class PromotionCandidates(BaseModel):
    winning_hooks: List[str] = []
    winning_formats: List[str] = []
    failed_patterns: List[str] = []
    caption_patterns: List[str] = []

class WeeklyAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    week_start: datetime
    week_end: datetime
    video_ids: List[str] = []
    summary_markdown: str
    wins: List[str] = []
    losses: List[str] = []
    open_questions: List[str] = []
    promotion_candidates: PromotionCandidates = Field(default_factory=PromotionCandidates)
    source_run_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
