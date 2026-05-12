from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
import uuid

class RunStep(BaseModel):
    name: str
    status: str # started, completed, failed
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    summary: Optional[str] = None
    error: Optional[str] = None

class RunLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_name: str
    trigger_type: str = "manual" # manual, page_trigger, scheduled
    scheduled_for: Optional[datetime] = None
    status: str = "started" # started, completed, failed, skipped
    steps: List[RunStep] = []
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
