import streamlit as st
from redline.db.repositories.ideas_repo import IdeaRepository
from redline.db.repositories.videos_repo import VideoRepository
from redline.core.planner_service import PlannerService
from redline.utils.auth import check_password
from datetime import datetime

if not check_password():
    st.stop()

st.title("🎬 Video Planner")

# Repositories
idea_repo = IdeaRepository()
video_repo = VideoRepository()
planner_service = PlannerService()

# 1. Selection
st.subheader("1. Select an Idea")
selected_ideas = idea_repo.list(filters={"status": "selected"})

if not selected_ideas:
    st.info("No ideas selected. Go to the Ideas page to select one first.")
    st.stop()

idea_titles = [i.title for i in selected_ideas]
selected_title = st.selectbox("Choose an idea to plan:", idea_titles)
selected_idea = next(i for i in selected_ideas if i.title == selected_title)

st.info(f"**Concept:** {selected_idea.summary}\n\n**Angle:** {selected_idea.angle}")

# 2. Planning
st.subheader("2. Generate Plan")

if st.button("Generate Detailed Plan", type="primary"):
    with st.spinner("AI is drafting the blueprint..."):
        try:
            plan = planner_service.generate_plan(selected_idea.title, selected_idea.summary)
            
            # Auto-Save Immediately
            video_id = f"rc-{datetime.now().strftime('%Y-%m-%d')}-{selected_idea.idea_id.split('-')[-1]}"
            from redline.models.video import Video
            new_video = Video(
                video_id=video_id,
                title=selected_idea.title,
                idea_id=selected_idea.idea_id,
                status="planned",
                plan=plan
            )
            video_repo.create(new_video)
            
            # Mark idea as processed
            idea_repo.update(selected_idea.id, {"status": "processed"})
            
            st.success(f"✨ Plan generated and auto-saved as {video_id}!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display Planned Video if it exists for this idea
existing_video = video_repo.collection.find_one({"idea_id": selected_idea.idea_id})
if existing_video:
    from redline.models.video import Video
    v = Video(**existing_video)
    if v.plan:
        with st.container(border=True):
            st.markdown(f"### ✨ Final Build Plan: {v.title}")
            st.markdown(f"**Hook:** {v.plan.hook}")
            st.markdown("**Beats:**")
            for beat in v.plan.beats:
                st.markdown(f"- {beat}")
            st.markdown(f"**CTA:** {v.plan.cta}")
            
            with st.expander("Production Notes"):
                for note in v.plan.production_notes:
                    st.write(f"- {note}")
