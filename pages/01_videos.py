import streamlit as st
from redline.db.repositories.base_repo import BaseRepository
from redline.models.video import Video
from redline.utils.auth import check_password

if not check_password():
    st.stop()

st.title("🎬 VIDEOS")
st.caption("Active Production Pipeline")

video_repo = BaseRepository("videos", Video)
videos = video_repo.list(sort=[("created_at", -1)])

if not videos:
    st.info("No build packages found. Approve some ideas to start the engine!")
else:
    # Categorize
    finalized = [v for v in videos if v.status in ["drafted", "published"]]
    in_build = [v for v in videos if v.status == "planned"]
    
    st.markdown(f"### ✅ FINALIZED PACKAGES ({len(finalized)})")
    for v in finalized:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"#### {v.title.upper()}")
            if c2.button("DETAILS", key=f"v_{v.id}", use_container_width=True):
                st.session_state.selected_video = v.id
                st.switch_page("pages/03_video_planner.py")
            
            st.caption(f"Status: `{v.status.upper()}` | Built: {v.created_at.strftime('%Y-%m-%d')}")
            
            with st.expander("📦 VIEW BUILD PACKAGE"):
                tab1, tab2 = st.tabs(["SCRIPT & PLAN", "SOCIAL PACKAGE"])
                with tab1:
                    if v.plan:
                        st.markdown(f"**ANGLE:** {v.plan.angle}")
                        st.markdown(v.plan.script_outline)
                    else:
                        st.warning("No plan data found.")
                with tab2:
                    if v.post_package:
                        st.markdown(v.post_package.packaging_notes)
                    else:
                        st.warning("Social package not built yet.")

    if in_build:
        st.divider()
        st.markdown(f"### ⏳ IN-BUILD ({len(in_build)})")
        for v in in_build:
            with st.container(border=True):
                st.markdown(f"**{v.title.upper()}**")
                st.caption(f"Status: `PLANNING` | Pipeline active...")
