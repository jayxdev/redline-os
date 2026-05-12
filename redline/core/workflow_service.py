from redline.core.config_service import ConfigService
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.db.repositories.rules_repo import RulesRepository
from redline.utils.prompts import load_prompt

class WorkflowService:
    def __init__(self):
        self.config = ConfigService()
        api_key = self.config.get("NVIDIA_API_KEY")
        model = self.config.get("DEFAULT_LLM_MODEL", "meta/llama-3-70b-instruct")
        self.llm = NVIDIAProvider(api_key, model)
        self.rules_repo = RulesRepository()

    def get_system_context(self) -> str:
        rules = self.rules_repo.get_latest_active()
        rules_text = rules.rules_markdown if rules else "Follow general content creation best practices."
        system_role = load_prompt("00-system-role.md")
        return f"{system_role}\n\n## Current Rules\n\n{rules_text}"
