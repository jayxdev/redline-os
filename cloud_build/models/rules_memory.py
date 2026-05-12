from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class RulesMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ruleset_id: str
    version: int
    status: str = "active" # active, archived
    rules_markdown: str
    change_summary: List[str] = []
    evidence_analysis_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
