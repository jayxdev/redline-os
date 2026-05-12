import streamlit as st
from redline.db.repositories.videos_repo import VideoRepository
from redline.utils.auth import check_password
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.utils.prompts import load_prompt
import os

if not check_password():
    st.stop()

st.title("🏷️ Caption & Hashtags")

@st.cache_resource
def get_video_repo():
    return VideoRepository()

video_repo = get_video_repo()
videos = video_repo.list(filters={"status": "planned"})

if not videos:
    st.info("No planned videos found. Create a plan first.")
    st.stop()

selected_vid_title = st.selectbox("Select video to package:", [v.title for v in videos])
video = next(v for v in videos if v.title == selected_vid_title)

st.write(f"**Hook:** {video.plan.hook if video.plan else 'N/A'}")

if st.button("Generate Packaging Options", type="primary"):
    from redline.core.config_service import ConfigService
    config = ConfigService()
    api_key = config.get("NVIDIA_API_KEY")
    model = config.get("DEFAULT_LLM_MODEL")
    
    if not api_key or not model:
        st.error("⚠️ AI Configuration Incomplete. Please set your NVIDIA API Key and Default Model in the Admin Settings.")
        st.stop()
        
    llm = NVIDIAProvider(api_key, model)
    
    with st.spinner("Generating options..."):
        prompt_tmpl = load_prompt("03-caption-hashtag-research.md")
        prompt = f"{prompt_tmpl}\n\nVideo Plan:\n{video.plan.model_dump_json() if video.plan else 'N/A'}"
        
        full_response = ""
        placeholder = st.empty()
        for chunk in llm.generate_stream(prompt):
            full_response += chunk
            placeholder.markdown(full_response)
        
        # Parse with unified response parser
        from redline.models.agent_outputs import CaptionPackageOutput
        from redline.core.response_parser import parse_agent_response
        
        agent_resp, cap_data = parse_agent_response(full_response, CaptionPackageOutput)
        
        if agent_resp.parsed_ok and cap_data:
            caption = cap_data.primary_caption
            hashtags = cap_data.hashtag_set
        else:
            caption = agent_resp.summary[:200] if agent_resp.summary else "See packaging notes."
            hashtags = []
        
        # Save directly
        updates = {
            "status": "drafted",
            "post_package": {
                "selected_caption": caption,
                "hashtags": hashtags,
                "packaging_notes": full_response
            }
        }
        video_repo.update(video.id, updates)
        st.success("✨ Packaging generated and saved automatically!")
        st.session_state.packaging_options = full_response
        st.rerun()

if video.post_package:
    st.markdown("### ✨ Final Build Package")
    st.markdown(f"**Final Caption:**\n\n{video.post_package.selected_caption}")
    st.markdown(f"**Hashtags:** {', '.join(video.post_package.hashtags) if video.post_package.hashtags else 'None'}")
    
    with st.expander("View Full AI Packaging Notes"):
        st.markdown(video.post_package.packaging_notes)

