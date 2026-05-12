from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
import uuid

class VideoPlan(BaseModel):
    hook: str
    concept: str
    beats: List[str]
    cta: str
    production_notes: List[str] = []

class PostPackage(BaseModel):
    caption_options: List[str] = []
    selected_caption: Optional[str] = None
    hashtags: List[str] = []
    packaging_notes: Optional[str] = None

class VideoMetrics(BaseModel):
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    watch_time: Optional[float] = None
    completion_rate: Optional[float] = None

class MetricSnapshot(BaseModel):
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"
    metrics: Dict[str, int]

class Video(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    title: str
    idea_id: Optional[str] = None
    status: str = "planned" # planned, drafted, posted, reviewed
    platform: str = "instagram"
    plan: Optional[VideoPlan] = None
    post_package: Optional[PostPackage] = None
    metrics: VideoMetrics = Field(default_factory=VideoMetrics)
    metric_snapshots: List[MetricSnapshot] = []
    review_notes: List[str] = []
    llm_notes_markdown: Optional[str] = None
    source_run_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
