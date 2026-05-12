import streamlit as st
from redline.utils.auth import logout

def draw_sidebar():
    from redline.core.config_service import ConfigService
    from redline.providers.mongo.client import MongoManager
    config = ConfigService()
    
    with st.sidebar:
        st.title("🏎️ Redline OS")
        
        # 1. System Pulse (Compact)
        current_model = config.get("DEFAULT_LLM_MODEL", "Llama 3.3")
        display_name = current_model.split("/")[-1].replace("-", " ").title()[:20]
        
        st.markdown(f"**Engine:** `{display_name}`")
        
        try:
            db = MongoManager().get_db()
            v_count = db.videos.count_documents({})
            i_count = db.ideas.count_documents({})
            st.markdown(f"📊 Projects: **{v_count}** | Ideas: **{i_count}**")
        except Exception:
            st.error("DB Offline")
        
        st.divider()
        
        # 2. Channel Vibe (Compact)
        from redline.db.repositories.rules_repo import RulesRepository
        rules = RulesRepository().get_latest_active()
        if rules:
            rule_title = rules.title[:25] + "..." if len(rules.title) > 25 else rules.title
            st.markdown(f"🎭 **Rule:** {rule_title}")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
            
        st.caption("v1.5.0 | 🏁 Redline Cult")
