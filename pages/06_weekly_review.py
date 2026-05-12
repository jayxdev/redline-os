import streamlit as st
from redline.db.repositories.videos_repo import VideoRepository
from redline.db.repositories.base_repo import BaseRepository
from redline.models.weekly_analysis import WeeklyAnalysis
from redline.utils.auth import check_password
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.utils.prompts import load_prompt
from datetime import datetime, timedelta
import os

if not check_password():
    st.stop()

st.title("🗓️ Weekly Review")

video_repo = VideoRepository()
analysis_repo = BaseRepository("weekly_analyses", WeeklyAnalysis)

# 1. Date Range
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

# 2. Select Videos
videos = video_repo.list(filters={
    "updated_at": {
        "$gte": datetime.combine(start_date, datetime.min.time()),
        "$lte": datetime.combine(end_date, datetime.max.time())
    },
    "status": {"$in": ["posted", "reviewed"]}
})

if not videos:
    st.warning("No posted videos found in this date range.")
    st.stop()

st.write(f"Found {len(videos)} videos for review.")

selected_vids = st.multiselect("Confirm videos to include:", 
                               [v.title for v in videos], 
                               default=[v.title for v in videos])

if st.button("Run Weekly Analysis", type="primary"):
    selected_data = [v.model_dump_json() for v in videos if v.title in selected_vids]
    
    api_key = os.getenv("NVIDIA_API_KEY")
    llm = NVIDIAProvider(api_key)
    
    prompt_tmpl = load_prompt("05-weekly-analyzer.md")
    prompt = f"{prompt_tmpl}\n\nDate Range: {start_date} to {end_date}\n\nVideos Data:\n" + "\n---\n".join(selected_data)
    
    with st.spinner("Analyzing weekly performance..."):
        response = llm.generate(prompt)
        st.session_state.weekly_draft = response["raw_text"]
        st.session_state.weekly_json = response["parsed_data"]

if 'weekly_draft' in st.session_state:
    st.markdown("### Draft Analysis")
    st.markdown(st.session_state.weekly_draft)
    
    if st.button("Save Weekly Analysis"):
        analysis_id = f"weekly-{start_date.strftime('%Y-%m-%d')}"
        data = st.session_state.weekly_json or {}
        
        analysis = WeeklyAnalysis(
            analysis_id=analysis_id,
            week_start=start_date,
            week_end=end_date,
            video_ids=[v.video_id for v in videos if v.title in selected_vids],
            summary_markdown=st.session_state.weekly_draft,
            wins=data.get("wins", []),
            losses=data.get("losses", []),
            promotion_candidates=data.get("promotion_candidates", {})
        )
        analysis_repo.create(analysis)
        st.success("Weekly Analysis saved!")
        del st.session_state.weekly_draft
