from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional
import uuid

class SystemConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str # e.g., "NVIDIA_API_KEY", "TELEGRAM_BOT_TOKEN"
    value: Any
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
