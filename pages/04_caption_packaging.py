import streamlit as st
from db.repositories.videos_repo import VideoRepository
from utils.auth import check_password
from providers.llm.nvidia_provider import NVIDIAProvider
from utils.prompts import load_prompt
import os

if not check_password():
    st.stop()

st.title("🏷️ Caption & Hashtags")

video_repo = VideoRepository()
videos = video_repo.list(filters={"status": "planned"})

if not videos:
    st.info("No planned videos found. Create a plan first.")
    st.stop()

selected_vid_title = st.selectbox("Select video to package:", [v.title for v in videos])
video = next(v for v in videos if v.title == selected_vid_title)

st.write(f"**Hook:** {video.plan.hook if video.plan else 'N/A'}")

if st.button("Generate Packaging Options", type="primary"):
    api_key = os.getenv("NVIDIA_API_KEY")
    llm = NVIDIAProvider(api_key)
    
    prompt_tmpl = load_prompt("03-caption-hashtag-research.md")
    prompt = f"{prompt_tmpl}\n\nVideo Plan:\n{video.plan.model_dump_json() if video.plan else 'N/A'}"
    
    with st.spinner("Generating options..."):
        response = llm.generate(prompt)
        st.session_state.packaging_options = response["raw_text"]

if 'packaging_options' in st.session_state:
    st.markdown("### Suggested Packaging")
    st.markdown(st.session_state.packaging_options)
    
    selected_caption = st.text_area("Final Selected Caption", height=150)
    hashtags = st.text_input("Final Hashtags (comma separated)")
    
    if st.button("Save Packaging"):
        updates = {
            "status": "drafted",
            "post_package": {
                "selected_caption": selected_caption,
                "hashtags": [h.strip() for h in hashtags.split(",")],
                "packaging_notes": st.session_state.packaging_options
            }
        }
        video_repo.update(video.id, updates)
        st.success("Packaging saved!")
        del st.session_state.packaging_options
