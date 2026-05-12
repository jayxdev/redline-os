import streamlit as st
from redline.utils.auth import logout

def draw_sidebar():
    from redline.core.config_service import ConfigService
    from redline.providers.mongo.client import MongoManager
    config = ConfigService()
    
    with st.sidebar:
        # Mini Header Row
        col_t, col_l = st.columns([3, 1])
        col_t.markdown("### 🏎️ Redline `v1.5`")
        if col_l.button("🚪", help="Logout", key="top_logout"):
            logout()
            st.rerun()
            
        # Unified Stats Row
        current_model = config.get("DEFAULT_LLM_MODEL", "Llama 3.3")
        engine = current_model.split("/")[-1]
        
        try:
            db = MongoManager().get_db()
            v_count = db.videos.count_documents({})
            i_count = db.ideas.count_documents({})
            st.caption(f"🤖 `{engine}`")
            st.caption(f"🎬 **{v_count}** Videos | 💡 **{i_count}** Ideas")
        except Exception:
            st.caption("🤖 `Offline` | ⚠️ DB Error")
        
        # 2. Channel Vibe (Mini)
        from redline.db.repositories.rules_repo import RulesRepository
        rules = RulesRepository().get_latest_active()
        if rules:
            st.caption(f"🎭 **Rule:** `{rules.ruleset_id}`")
            
        st.divider()
        # Streamlit navigation links will appear below this divider automatically

def run_autonomous_agents_ui(idea):
    """Visual wrapper for running the autonomous agents step-by-step."""
    from redline.db.repositories.ideas_repo import IdeaRepository
    from redline.db.repositories.run_log_repo import RunLogRepository
    from redline.models.run_log import RunLog, RunStep
    from datetime import datetime
    
    idea_repo = IdeaRepository()
    run_repo = RunLogRepository()
    idea_repo.update(idea.id, {"status": "selected"})
    
    # Initialize Run History
    run_log = RunLog(job_name=f"UI Build: {idea.title}", trigger_type="instant-approve")
    run_repo.create(run_log)
    
    with st.status(f"🚀 Launching Agents for '{idea.title}'...", expanded=True) as status:
        try:
            # Step 1: Planner
            step1 = RunStep(name="Video Planner", status="started")
            run_log.steps.append(step1)
            st.write("🤖 Video Planner is scanning the concept...")
            
            from redline.core.planner_service import PlannerService
            planner = PlannerService()
            plan = planner.generate_plan(idea.title, idea.summary)
            
            step1.status = "completed"
            run_repo.update(run_log.id, run_log)
            st.write("✅ Video Plan constructed.")
            
            # Step 2: Caption Agent
            step2 = RunStep(name="Caption Agent", status="started")
            run_log.steps.append(step2)
            st.write("🤖 Caption Agent is analyzing hooks for social packaging...")
            
            from redline.core.automation_service import AutomationService
            from redline.models.video import Video, PostPackage
            from redline.db.repositories.videos_repo import VideoRepository
            from redline.utils.prompts import load_prompt
            import re
            
            auto = AutomationService()
            caption_tmpl = load_prompt("03-caption-hashtag-research.md")
            caption_prompt = f"{caption_tmpl}\n\nVideo Plan:\n{plan.model_dump_json()}"
            cap_res = auto.llm.generate(caption_prompt, auto.get_system_context())
            full_response = cap_res["raw_text"]
            
            def extract_caption_field(field_name, default=""):
                pattern = r'(?:^|\n)\s*(?:-\s*)?\**' + field_name + r'\**\s*:\s*(.*?)(?=\n\s*(?:-\s*)?\**[a-z0-9_]+\**\s*:|\n\s*##|$)'
                match = re.search(pattern, full_response, re.IGNORECASE | re.DOTALL)
                return match.group(1).strip() if match else default

            caption = extract_caption_field(r"(?:primary_caption|Caption)", "See packaging notes.")
            var1 = extract_caption_field(r"caption_variant_1", "")
            var2 = extract_caption_field(r"caption_variant_2", "")
            
            caption_opts = [c for c in [caption, var1, var2] if c]
            
            hashtags_str = extract_caption_field(r"(?:hashtag_set|Hashtags used)", "")
            hashtags = [h.strip() for h in hashtags_str.replace('\n', ' ').split() if h.strip().startswith('#')]
            if not hashtags and hashtags_str:
                hashtags = [f"#{h.strip()}" for h in hashtags_str.split(",") if h.strip()]
            
            video_repo = VideoRepository()
            video_id = f"auto-{datetime.now().strftime('%m%d')}-{idea.idea_id}"
            new_video = Video(
                video_id=video_id,
                title=idea.title,
                idea_id=idea.idea_id,
                status="drafted",
                plan=plan,
                post_package=PostPackage(
                    selected_caption=caption,
                    caption_options=caption_opts,
                    hashtags=hashtags,
                    packaging_notes=full_response
                )
            )
            video_repo.create(new_video)
            idea_repo.update(idea.id, {"status": "processed"})
            
            step2.status = "completed"
            run_log.status = "completed"
            run_log.finished_at = datetime.utcnow()
            run_repo.update(run_log.id, run_log)
            st.write("✅ Captions & Hashtags locked.")
            
            status.update(label="🏁 Package Build Complete!", state="complete", expanded=False)
            st.toast(f"✅ Sent to VIDEOS Hub: {idea.title}")
            
        except Exception as e:
            run_log.status = "failed"
            run_log.error_message = str(e)
            run_log.finished_at = datetime.utcnow()
            run_repo.update(run_log.id, run_log)
            status.update(label=f"❌ Build Failed: {str(e)}", state="error", expanded=True)
            st.error(f"Agent crashed: {str(e)}")
            st.stop()
            
    st.rerun()
