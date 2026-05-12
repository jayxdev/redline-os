from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    title: str
    summary: str
    angle: str
    rationale: str
    status: str = "new" # new, selected, rejected, archived
    source_run_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []

    class Config:
        populate_by_name = True
