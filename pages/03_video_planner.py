import streamlit as st
from db.repositories.ideas_repo import IdeaRepository
from db.repositories.videos_repo import VideoRepository
from core.planner_service import PlannerService
from utils.auth import check_password
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
            st.session_state.current_plan = plan
            st.success("Plan generated!")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if 'current_plan' in st.session_state:
    plan = st.session_state.current_plan
    
    with st.container(border=True):
        st.markdown(f"### {selected_idea.title}")
        st.markdown(f"**Hook:** {plan.hook}")
        st.markdown("**Beats:**")
        for beat in plan.beats:
            st.markdown(f"- {beat}")
        st.markdown(f"**CTA:** {plan.cta}")
        
        with st.expander("Production Notes"):
            for note in plan.production_notes:
                st.write(f"- {note}")

    if st.button("Save as Video Project"):
        video_id = f"rc-{datetime.now().strftime('%Y-%m-%d')}-{selected_idea.idea_id.split('-')[-1]}"
        new_video = {
            "video_id": video_id,
            "title": selected_idea.title,
            "idea_id": selected_idea.idea_id,
            "status": "planned",
            "plan": plan.model_dump(),
            "updated_at": datetime.utcnow()
        }
        # In a real impl, we'd use the model and repo properly
        from models.video import Video
        video_repo.create(Video(**new_video))
        
        # Mark idea as archived/processed
        idea_repo.update(selected_idea.id, {"status": "archived"})
        
        st.success(f"Video saved as {video_id}!")
        del st.session_state.current_plan
        st.balloons()
