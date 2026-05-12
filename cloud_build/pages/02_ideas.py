import streamlit as st
from cloud_build.db.repositories.base_repo import BaseRepository
from cloud_build.models.idea import Idea
from cloud_build.providers.llm.nvidia_provider import NVIDIAProvider
from cloud_build.utils.auth import check_password
import os

from cloud_build.utils.ui import draw_sidebar

if not check_password():
    st.stop()

draw_sidebar()

st.title("💡 Idea Generation")

# Repository
idea_repo = BaseRepository("ideas", Idea)

# LLM Provider
def get_llm():
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("DEFAULT_LLM_MODEL", "meta/llama-3-70b-instruct")
    if not api_key:
        st.error("NVIDIA_API_KEY not found.")
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
            prompt = "Generate 3 viral content ideas for a bike/car enthusiast channel called Redline Cult. Focus on high-speed aesthetics and technical knowledge. Return JSON format."
            response = llm.generate(prompt)
            
            if response["parsed_data"]:
                st.success("Ideas generated!")
                st.json(response["parsed_data"])
                # In a real version, we would save these to the DB here
            else:
                st.warning("AI returned unstructured data:")
                st.markdown(response["raw_text"])
    
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
