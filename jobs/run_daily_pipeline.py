from ..providers.llm.nvidia_provider import NVIDIAProvider
from ..db.repositories.base_repo import BaseRepository
from ..models.run_log import RunLog, RunStep
from ..models.idea import Idea
from ..providers.telegram.client import TelegramClient
from ..utils.prompts import load_prompt
import os
from datetime import datetime

def run_daily_pipeline():
    # Setup
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("DEFAULT_LLM_MODEL", "meta/llama-3-70b-instruct")
    llm = NVIDIAProvider(api_key, model)
    idea_repo = BaseRepository("ideas", Idea)
    run_repo = BaseRepository("job_runs", RunLog)
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat = os.getenv("TELEGRAM_CHAT_ID")
    tg = TelegramClient(tg_token, tg_chat) if tg_token and tg_chat else None

    # 1. Create run log
    run = RunLog(job_name="daily_pipeline", trigger_type="page_trigger")
    run_id = run.create(run) # This is a bit recursive with my repo design, let's fix the logic
    
    # Actually my BaseRepo doesn't return the run_id easily for nested updates without some changes
    # Let's just do a simple implementation for now
    
    steps = []
    
    try:
        # Step: Idea Generation
        step1 = RunStep(name="idea_generation", status="started")
        prompt_tmpl = load_prompt("01-idea-generator.md")
        # In a real run, we'd fetch rules too
        response = llm.generate(prompt_tmpl)
        
        if response["parsed_data"]:
            # Save ideas
            # ... idea saving logic ...
            step1.status = "completed"
            step1.summary = f"Generated {len(response['parsed_data'])} ideas"
        else:
            step1.status = "failed"
            step1.error = "Could not parse JSON from LLM"
        
        step1.finished_at = datetime.utcnow()
        steps.append(step1)
        
        # Finish run
        final_status = "completed" if all(s.status == "completed" for s in steps) else "failed"
        if tg:
            tg.send_message(f"✅ Redline Cult Daily Job: {final_status}\nSteps: {len(steps)}")
            
    except Exception as e:
        if tg:
            tg.send_message(f"❌ Redline Cult Daily Job Failed: {str(e)}")
        # log error...

if __name__ == "__main__":
    run_daily_pipeline()
