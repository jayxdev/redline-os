"""
Structured output schemas for every Redline agent.

Each schema defines the exact JSON shape we ask the LLM to return.
The response_parser validates raw LLM output against these models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ─────────────────────────────────────────────
# 01 — Idea Generator
# ─────────────────────────────────────────────
class IdeaItem(BaseModel):
    title: str
    hook: str = ""
    concept: str = ""
    visual_sequence: List[str] = []
    why_it_should_work: str = ""
    risk: str = ""
    pattern_tags: List[str] = []

class IdeaGeneratorOutput(BaseModel):
    """Output from prompt 01-idea-generator."""
    ideas: List[IdeaItem]
    top_2_recommendations: List[str] = []
    why_these_two: str = ""


# ─────────────────────────────────────────────
# 02 — Video Planner
# ─────────────────────────────────────────────
class VideoPlannerOutput(BaseModel):
    """Output from prompt 02-video-planner."""
    video_id: str = ""
    topic: str = ""
    format_type: str = ""
    hook: str
    core_payoff: str = ""
    loop_strategy: str = ""
    opening_shot: str = ""
    shot_sequence: List[str] = []
    timing_notes: str = ""
    expected_retention_driver: str = ""
    why_this_should_work: str = ""
    main_risk: str = ""
    pattern_tags: List[str] = []


# ─────────────────────────────────────────────
# 03 — Caption & Hashtag Package
# ─────────────────────────────────────────────
class CaptionPackageOutput(BaseModel):
    """Output from prompt 03-caption-hashtag-research."""
    primary_caption: str
    caption_variant_1: str = ""
    caption_variant_2: str = ""
    caption_style: str = ""
    primary_cta: str = ""
    hashtag_set: List[str] = []
    hashtag_strategy: str = ""
    why_this_package_fits: str = ""


# ─────────────────────────────────────────────
# 04 — Results Logger
# ─────────────────────────────────────────────
class ResultsLoggerOutput(BaseModel):
    """Output from prompt 04-results-logger."""
    status: str = ""
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    watch_time: Optional[float] = None
    completion_rate: Optional[float] = None
    qualitative_notes: str = ""
    verdict: str = ""


# ─────────────────────────────────────────────
# 05 — Weekly Analyzer
# ─────────────────────────────────────────────
class WeeklyAnalyzerOutput(BaseModel):
    """Output from prompt 05-weekly-analyzer."""
    wins: List[str] = []
    losses: List[str] = []
    open_questions: List[str] = []
    summary: str = ""
    hooks_to_add: List[str] = []
    formats_to_add: List[str] = []
    failures_to_add: List[str] = []
    rules_to_change: List[str] = []


# ─────────────────────────────────────────────
# 06 — Pattern Promoter
# ─────────────────────────────────────────────
class PatternPromoterOutput(BaseModel):
    """Output from prompt 06-pattern-promoter."""
    caption_hashtag_patterns: str = ""
    winning_hooks: str = ""
    winning_formats: str = ""
    failed_patterns: str = ""
    rules: str = ""
    change_summary: List[str] = []


# ─────────────────────────────────────────────
# 07 — Reality Check
# ─────────────────────────────────────────────
class RealityCheckOutput(BaseModel):
    """Output from prompt 07-reality-check."""
    what_is_working: str = ""
    what_is_wasting_time: str = ""
    where_the_data_is_being_misread: str = ""
    what_to_stop: str = ""
    what_to_double_down_on: str = ""
    what_to_test_next: str = ""


# ─────────────────────────────────────────────
# Inline / Pipeline (single idea from automation)
# ─────────────────────────────────────────────
class SingleIdeaOutput(BaseModel):
    """Quick single-idea output used by the automation pipeline."""
    title: str
    summary: str = ""
    angle: str = ""
    rationale: str = ""
