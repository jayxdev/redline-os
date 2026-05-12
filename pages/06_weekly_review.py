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

# 3. Synthesis Chat (Memory Integration)
st.divider()
st.subheader("🧠 Performance Synthesis Chat")
st.caption("Tell the AI about your manual observations (e.g., 'The thumbnail for Video X was the reason it blew up').")

if "weekly_chat" not in st.session_state:
    st.session_state.weekly_chat = []

# Display chat history
for msg in st.session_state.weekly_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("What did you learn this week?")

if user_input:
    # Add to history
    st.session_state.weekly_chat.append({"role": "user", "content": user_input})
    
    # Prepare context for AI
    selected_data = [v.model_dump_json() for v in videos if v.title in selected_vids]
    
    from redline.core.config_service import ConfigService
    config = ConfigService()
    api_key = config.get("NVIDIA_API_KEY")
    model = config.get("DEFAULT_LLM_MODEL")
    
    if api_key and model:
        llm = NVIDIAProvider(api_key, model)
        
        # System prompt for synthesis
        chat_prompt = f"""You are the Redline Cult OS Brain. 
        We are doing the Weekly Review for {start_date} to {end_date}.
        
        DATA:
        {selected_data}
        
        USER FEEDBACK:
        {user_input}
        
        CONVERSATION SO FAR:
        {st.session_state.weekly_chat[:-1]}
        
        Respond as an expert growth strategist. Acknowledge the user's input and suggest how it affects our 'Rules' or 'Patterns'."""
        
        with st.spinner("Synthesizing..."):
            response = llm.generate(chat_prompt)
            ai_msg = response["raw_text"]
            st.session_state.weekly_chat.append({"role": "assistant", "content": ai_msg})
            st.rerun()

# 4. Final Conclusion
if st.session_state.weekly_chat:
    if st.button("🏁 Conclude & Save Weekly Memory", type="primary", use_container_width=True):
        with st.spinner("Finalizing memory..."):
            # Final one-shot to get the structured data based on the WHOLE chat
            final_prompt = f"""Summarize our entire conversation into a structured Weekly Analysis.
            
            HISTORY:
            {st.session_state.weekly_chat}
            
            Return JSON with 'wins' (list), 'losses' (list), 'summary' (markdown)."""
            
            config = ConfigService()
            llm = NVIDIAProvider(config.get("NVIDIA_API_KEY"), config.get("DEFAULT_LLM_MODEL"))
            res = llm.generate(final_prompt)
            data = res["parsed_data"] or {}
            
            analysis_id = f"weekly-{start_date.strftime('%Y-%m-%d')}"
            analysis = WeeklyAnalysis(
                analysis_id=analysis_id,
                week_start=datetime.combine(start_date, datetime.min.time()),
                week_end=datetime.combine(end_date, datetime.max.time()),
                video_ids=[v.video_id for v in videos if v.title in selected_vids],
                summary_markdown=data.get("summary", res["raw_text"]),
                wins=data.get("wins", []),
                losses=data.get("losses", []),
                promotion_candidates={}
            )
            analysis_repo.create(analysis)
            
            # CLEAR CHAT
            st.session_state.weekly_chat = []
            st.success("Weekly Memory successfully updated! 🏎️💨")
            st.balloons()
