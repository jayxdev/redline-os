import streamlit as st
from redline.utils.auth import logout

def draw_sidebar():
    st.sidebar.title("🏎️ Redline Cult OS")
    st.sidebar.markdown("---")
    
    # Common stats or info could go here
    
    st.sidebar.markdown("### Navigation")
    # Subpages are handled by Streamlit automatically in the sidebar
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.caption("v1.0.0-alpha")
