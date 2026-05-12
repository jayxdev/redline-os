from redline.core.workflow_service import WorkflowService
from redline.models.run_log import RunLog, RunStep
from redline.db.repositories.run_log_repo import RunLogRepository
from redline.db.repositories.ideas_repo import IdeaRepository
from redline.providers.telegram.client import TelegramClient
from redline.models.idea import Idea
from redline.models.agent_outputs import CaptionPackageOutput, SingleIdeaOutput
from redline.core.response_parser import parse_agent_response, inject_response_format
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class AutomationService(WorkflowService):
    def __init__(self):
        super().__init__()
        self.run_repo = RunLogRepository()
        self.idea_repo = IdeaRepository()
        
        bot_token = self.config.get("TELEGRAM_BOT_TOKEN")
        chat_id = self.config.get("TELEGRAM_CHAT_ID")
        self.tg = TelegramClient(bot_token, chat_id) if bot_token and chat_id else None

    def run_daily_pipeline(self, trigger_type: str = "manual"):
        run_log = RunLog(job_name="Autonomous Production", trigger_type=trigger_type)
        self.run_repo.create(run_log)
        
        try:
            system_prompt = self.get_system_context()
            
            # Step 1: Process Approved Ideas (The "Auto-Pilot" Flow)
            step1 = RunStep(name="Production Pipeline", status="started")
            run_log.steps.append(step1)
            
            approved_ideas = self.idea_repo.list(filters={"status": "selected"}) # 'selected' means 'approved' in UI
            if approved_ideas:
                from redline.core.planner_service import PlannerService
                planner = PlannerService()
                
                for idea in approved_ideas:
                    # 1. Generate Plan
                    plan = planner.generate_plan(idea.title, idea.summary)
                    
                    # 2. Create Video Project
                    from redline.models.video import Video, PostPackage
                    from redline.db.repositories.videos_repo import VideoRepository
                    video_repo = VideoRepository()
                    
                    video_id = f"auto-{datetime.now().strftime('%m%d')}-{idea.idea_id}"
                    new_video = Video(
                        video_id=video_id,
                        title=idea.title,
                        idea_id=idea.idea_id,
                        status="planned",
                        plan=plan
                    )
                    
                    # 3. Generate Captions via structured output
                    from redline.utils.prompts import load_prompt
                    
                    caption_tmpl = load_prompt("03-caption-hashtag-research.md")
                    caption_prompt = f"{caption_tmpl}\n\nVideo Plan:\n{plan.model_dump_json()}"
                    cap_res = self.llm.generate(caption_prompt, system_prompt)
                    
                    agent_resp, cap_data = parse_agent_response(cap_res["raw_text"], CaptionPackageOutput)
                    
                    if agent_resp.parsed_ok and cap_data:
                        caption = cap_data.primary_caption
                        hashtags = cap_data.hashtag_set
                    else:
                        logger.warning(f"Caption parse failed: {agent_resp.parse_error}")
                        caption = agent_resp.summary[:200] if agent_resp.summary else "See packaging notes."
                        hashtags = []
                    
                    new_video.post_package = PostPackage(
                        selected_caption=caption,
                        hashtags=hashtags,
                        packaging_notes=cap_res["raw_text"]
                    )
                    new_video.status = "drafted"
                    
                    video_repo.create(new_video)
                    
                    # 4. Mark Idea Processed
                    self.idea_repo.update(idea.id, {"status": "processed"})
                    
                    if self.tg:
                        self.tg.send_message(f"✅ *Autonomous Production Complete*\n\nProject: *{idea.title}*\nStatus: Ready for review in Dashboard.")
                
                step1.status = "completed"
                step1.summary = f"Processed {len(approved_ideas)} ideas into drafted projects."
            else:
                step1.status = "completed"
                step1.summary = "No approved ideas found to process."

            # Step 2: Intelligent Idea Generation (Refilling the hopper)
            step2 = RunStep(name="Trend Ideation", status="started")
            run_log.steps.append(step2)
            self.run_repo.update(run_log.id, run_log)
            
            prompt = inject_response_format(
                "Generate 1 viral video idea for 'Redline Cult' that doubles down on our recent 'Wins'. "
                "Return JSON with 'title', 'summary', 'angle', 'rationale'."
            )
            response = self.llm.generate(prompt, system_prompt)
            
            agent_resp, idea_data = parse_agent_response(response["raw_text"], SingleIdeaOutput)
            
            if agent_resp.parsed_ok and idea_data:
                new_idea = Idea(
                    idea_id=str(uuid.uuid4())[:8],
                    title=idea_data.title,
                    summary=idea_data.summary,
                    angle=idea_data.angle or "Experimental",
                    rationale=idea_data.rationale,
                    status="new"
                )
                self.idea_repo.create(new_idea)
                step2.status = "completed"
                step2.summary = f"Generated idea: {new_idea.title}"
            else:
                raise Exception(f"Failed to generate structured idea data: {agent_resp.parse_error}")
            
            # Step 3: Telegram Notification
            if self.tg:
                self.tg.send_message(f"🚀 *Daily Update*\n\nGenerated: *{new_idea.title}*\n\nStatus: Systems nominal. Memory updated.")
            
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

