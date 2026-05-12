from redline.models.run_log import RunLog, RunStep
from redline.db.repositories.run_log_repo import RunLogRepository
from redline.db.repositories.ideas_repo import IdeaRepository
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.providers.telegram.client import TelegramClient
from redline.core.config_service import ConfigService
from datetime import datetime
import logging

class AutomationService:
    def __init__(self):
        self.config = ConfigService()
        self.run_repo = RunLogRepository()
        self.idea_repo = IdeaRepository()
        
        # Providers will be initialized on demand to ensure latest config is used
        self.llm = None
        self.tg = None

    def _init_providers(self):
        api_key = self.config.get("NVIDIA_API_KEY")
        model = self.config.get("DEFAULT_LLM_MODEL")
        if api_key:
            self.llm = NVIDIAProvider(api_key, model)
        
        bot_token = self.config.get("TELEGRAM_BOT_TOKEN")
        chat_id = self.config.get("TELEGRAM_CHAT_ID")
        if bot_token and chat_id:
            self.tg = TelegramClient(bot_token, chat_id)

    def run_daily_pipeline(self, trigger_type: str = "manual"):
        run_log = RunLog(job_name="Daily Pipeline", trigger_type=trigger_type)
        self.run_repo.create(run_log)
        
        try:
            self._init_providers()
            
            # Step 1: Trend Research
            step1 = RunStep(name="Trend Research", status="started")
            run_log.steps.append(step1)
            self.run_repo.update(run_log.id, run_log)
            
            if not self.llm:
                raise Exception("NVIDIA API Key not configured.")

            # Simple research prompt for now
            prompt = "Generate 1 viral video idea for a car enthusiast channel called Redline Cult. Focus on raw emotion and high-performance cars. Return as JSON with 'title' and 'summary'."
            response_data = self.llm.generate(prompt)
            
            # Save Idea
            try:
                # Use pre-parsed data if available, otherwise parse raw text
                idea_data = response_data.get("parsed_data")
                if not idea_data:
                    import json
                    idea_data = json.loads(response_data.get("raw_text", "{}"))
                
                from redline.models.idea import Idea
                new_idea = Idea(title=idea_data['title'], summary=idea_data['summary'], status="new")
                self.idea_repo.create(new_idea)
                step1.status = "completed"
                step1.summary = f"Generated idea: {new_idea.title}"
            except Exception as e:
                step1.status = "failed"
                step1.error = f"JSON Parse Error: {str(e)}"
                raise e
            
            # Step 2: Telegram Notification
            if self.tg:
                self.tg.send_message(f"🚀 *New Idea Generated*\n\n*Title:* {new_idea.title}\n\nReview it on your dashboard!")
            
            run_log.status = "completed"
            run_log.finished_at = datetime.utcnow()
            self.run_repo.update(run_log.id, run_log)
            return True

        except Exception as e:
            run_log.status = "failed"
            run_log.error_message = str(e)
            run_log.finished_at = datetime.utcnow()
            self.run_repo.update(run_log.id, run_log)
            if self.tg:
                self.tg.send_message(f"❌ *Daily Pipeline Failed*\n\nError: {str(e)}")
            return False
