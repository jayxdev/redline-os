import streamlit as st
from redline.db.repositories.base_repo import BaseRepository
from redline.models.idea import Idea
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.utils.auth import check_password
import os

from redline.utils.ui import draw_sidebar

if not check_password():
    st.stop()

draw_sidebar()

st.title("💡 Idea Generation")

# Repositories
@st.cache_resource
def get_idea_repo():
    return BaseRepository("ideas", Idea)

idea_repo = get_idea_repo()

# LLM Provider
def get_llm():
    from redline.core.config_service import ConfigService
    config = ConfigService()
    
    api_key = config.get("NVIDIA_API_KEY")
    model = config.get("DEFAULT_LLM_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1")
    
    if not api_key:
        st.error("NVIDIA_API_KEY not found in configuration.")
        return None
    return NVIDIAProvider(api_key, model)

# Sidebar actions
with st.sidebar:
    st.header("Actions")
    if st.button("Generate New Ideas", use_container_width=True):
        st.session_state.generating = True

if 'generating' in st.session_state and st.session_state.generating:
    st.subheader("Generating new content ideas...")
    llm = get_llm()
    if llm:
        with st.spinner("Consulting the AI..."):
            prompt = "Generate 3 viral content ideas for a bike/car enthusiast channel called Redline Cult. Focus on high-speed aesthetics and technical knowledge. Return in a clean markdown list format with titles and bullet points."
            
            # Using stream for better UX
            st.write_stream(llm.generate_stream(prompt))
            st.success("Generation complete!")
    
    if st.button("Clear"):
        st.session_state.generating = False
        st.rerun()

st.divider()

# List existing ideas
st.subheader("Recent Ideas")
ideas = idea_repo.list(sort=[("created_at", -1)])

if not ideas:
    st.write("No ideas found in the database.")
else:
    for idea in ideas:
        with st.expander(f"{idea.title} ({idea.status})"):
            st.write(f"**Angle:** {idea.angle}")
            st.write(f"**Rationale:** {idea.rationale}")
            st.write(f"**Summary:** {idea.summary}")
            st.caption(f"Created: {idea.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Select for Planning", key=f"sel_{idea.id}"):
                    idea_repo.update(idea.id, {"status": "selected"})
                    st.rerun()
            with col2:
                if st.button("Reject", key=f"rej_{idea.id}"):
                    idea_repo.update(idea.id, {"status": "rejected"})
                    st.rerun()
