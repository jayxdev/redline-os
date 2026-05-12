from redline.core.config_service import ConfigService
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.db.repositories.rules_repo import RulesRepository
from redline.utils.prompts import load_prompt

class WorkflowService:
    def __init__(self):
        self.config = ConfigService()
        api_key = self.config.get("NVIDIA_API_KEY")
        model = self.config.get("DEFAULT_LLM_MODEL")
        if not api_key or not model:
            raise ValueError("AI Configuration Incomplete. Missing NVIDIA_API_KEY or DEFAULT_LLM_MODEL in system_config.")
        self.llm = NVIDIAProvider(api_key, model)
        self.rules_repo = RulesRepository()

    def get_system_context(self) -> str:
        # 1. Fetch Core Rules
        rules = self.rules_repo.get_latest_active()
        rules_text = rules.rules_markdown if rules else "Follow general content creation best practices."
        
        # 2. Fetch Latest Performance Insights
        from redline.db.repositories.base_repo import BaseRepository
        from redline.models.weekly_analysis import WeeklyAnalysis
        from redline.models.pattern_memory import PatternMemory
        
        analysis_repo = BaseRepository("weekly_analyses", WeeklyAnalysis)
        pattern_repo = BaseRepository("patterns", PatternMemory)
        
        latest_analysis = analysis_repo.list(sort=[("week_end", -1)], limit=1)
        patterns = pattern_repo.list(filters={"confidence": {"$gte": 0.7}}, limit=3) # High confidence only
        
        insights = "\n### Recent Performance Insights\n"
        if latest_analysis:
            a = latest_analysis[0]
            insights += f"- Wins: {', '.join(a.wins)}\n- Losses: {', '.join(a.losses)}\n"
        
        if patterns:
            insights += "\n### Established Patterns\n"
            for p in patterns:
                insights += f"- {p.title}: {p.statement}\n"

        system_role = load_prompt("00-system-role.md")
        return f"{system_role}\n\n## Current Rules\n\n{rules_text}\n\n{insights}"
