import streamlit as st
from cloud_build.db.repositories.videos_repo import VideoRepository
from cloud_build.utils.auth import check_password
from datetime import datetime

if not check_password():
    st.stop()

st.title("📈 Results Logger")

video_repo = VideoRepository()
# Show drafted or posted videos
videos = video_repo.list(filters={"status": {"$in": ["drafted", "posted"]}})

if not videos:
    st.info("No videos ready for logging.")
    st.stop()

selected_vid_title = st.selectbox("Select video:", [v.title for v in videos])
video = next(v for v in videos if v.title == selected_vid_title)

with st.form("metrics_form"):
    st.subheader(f"Log metrics for: {video.video_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        views = st.number_input("Views", min_value=0, value=video.metrics.views)
        likes = st.number_input("Likes", min_value=0, value=video.metrics.likes)
        comments = st.number_input("Comments", min_value=0, value=video.metrics.comments)
    with col2:
        shares = st.number_input("Shares", min_value=0, value=video.metrics.shares)
        saves = st.number_input("Saves", min_value=0, value=video.metrics.saves)
        status = st.selectbox("Update Status", ["drafted", "posted", "reviewed"], 
                            index=["drafted", "posted", "reviewed"].index(video.status))

    review_notes = st.text_area("Review Notes / Performance Analysis")

    submit = st.form_submit_button("Save Metrics")

if submit:
    snapshot = {
        "captured_at": datetime.utcnow(),
        "source": "manual",
        "metrics": {"views": views, "likes": likes, "comments": comments, "shares": shares, "saves": saves}
    }
    
    updates = {
        "metrics": {
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves
        },
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    # Append snapshot to list
    video_repo.collection.update_one(
        {"id": video.id},
        {"$push": {"metric_snapshots": snapshot}, "$set": updates}
    )
    
    if review_notes:
        video_repo.collection.update_one(
            {"id": video.id},
            {"$push": {"review_notes": review_notes}}
        )
        
    st.success("Metrics updated successfully!")
    st.rerun()
