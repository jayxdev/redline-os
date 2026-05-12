from redline.utils.auth import check_password

if not check_password():
    st.stop()

st.title("🎬 VIDEOS")
st.caption("Active Production Pipeline")

video_repo = BaseRepository("videos", Video)

# Filters
col_f1, col_f2 = st.columns(2)
status_filter = col_f1.selectbox("Filter by Status", ["All", "drafted", "planned", "published"])
search_query = col_f2.text_input("Search Videos", "")

# Load data
filters = {}
if status_filter != "All":
    filters["status"] = status_filter
if search_query:
    filters["title"] = {"$regex": search_query, "$options": "i"}

videos = video_repo.list(filters=filters, sort=[("created_at", -1)])

if not videos:
    st.info("No videos found in this queue.")
else:
    for v in videos:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"### {v.title}")
            c2.markdown(f"**Status:** `{v.status.upper()}`")
            
            if c3.button("View Details", key=f"view_{v.id}", use_container_width=True):
                st.session_state.selected_video = v.id
                st.switch_page("pages/03_video_planner.py")
            
            # Preview of the plan if available
            if v.plan:
                with st.expander("📝 Quick Look: Video Plan"):
                    st.write(f"**Angle:** {v.plan.angle}")
                    st.write(v.plan.script_outline[:200] + "...")
            
            if v.post_package:
                 with st.expander("📦 Quick Look: Social Package"):
                    st.write(v.post_package.packaging_notes[:200] + "...")
