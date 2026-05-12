import streamlit as st
from redline.utils.auth import logout

def draw_sidebar():
    from redline.core.config_service import ConfigService
    config = ConfigService()
    
    st.sidebar.title("🏎️ Redline Cult OS")
    
    # AI Status Section
    st.sidebar.markdown("### 🤖 AI Status")
    current_model = config.get("DEFAULT_LLM_MODEL", "Llama 3.3 Super")
    # Clean up model name for display
    display_name = current_model.split("/")[-1].replace("-", " ").title()
    if "Nemotron" in display_name: display_name = "Llama 3.3 Super"
    
    st.sidebar.success(f"**Live:** {display_name}")
    
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 🧭 Navigation")
    # Subpages are handled by Streamlit automatically in the sidebar
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.caption("System v1.2.0-stable | 🏁 Redline Cult")
