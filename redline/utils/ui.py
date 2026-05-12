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
