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
    idea_repo = IdeaRepository()
    idea_repo.update(idea.id, {"status": "selected"})
    
    with st.status(f"🚀 Launching Agents for '{idea.title}'...", expanded=True) as status:
        st.write("🤖 Video Planner is scanning the concept...")
        from redline.core.planner_service import PlannerService
        planner = PlannerService()
        plan = planner.generate_plan(idea.title, idea.summary)
        st.write("✅ Video Plan constructed.")
        
        st.write("🤖 Caption Agent is analyzing hooks for social packaging...")
        from redline.core.automation_service import AutomationService
        from redline.models.video import Video, PostPackage
        from redline.db.repositories.videos_repo import VideoRepository
        from redline.utils.prompts import load_prompt
        from datetime import datetime
        import re
        
        auto = AutomationService()
        caption_tmpl = load_prompt("03-caption-hashtag-research.md")
        caption_prompt = f"{caption_tmpl}\n\nVideo Plan:\n{plan.model_dump_json()}"
        cap_res = auto.llm.generate(caption_prompt, auto.get_system_context())
        full_response = cap_res["raw_text"]
        
        cap_match = re.search(r'-\s*(?:primary_caption|Caption):\s*(.*)', full_response, re.IGNORECASE)
        caption = cap_match.group(1).strip() if cap_match else "See packaging notes."
        
        hash_match = re.search(r'-\s*(?:hashtag_set|Hashtags used):\s*(.*)', full_response, re.IGNORECASE)
        hashtags_str = hash_match.group(1).strip() if hash_match else ""
        hashtags = [h.strip() for h in hashtags_str.split(",") if h.strip()]
        
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
                hashtags=hashtags,
                packaging_notes=full_response
            )
        )
        video_repo.create(new_video)
        idea_repo.update(idea.id, {"status": "processed"})
        st.write("✅ Captions & Hashtags locked.")
        
        status.update(label="🏁 Package Build Complete!", state="complete", expanded=False)
    
    st.toast(f"✅ Sent to VIDEOS Hub: {idea.title}")
    st.rerun()
