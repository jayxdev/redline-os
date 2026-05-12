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
            
            if c2.button("🗑️ DELETE", key=f"del_{v.id}", use_container_width=True, type="secondary"):
                video_repo.delete(v.id)
                st.toast(f"🗑️ Incinerated: {v.title}")
                st.rerun()
            
            st.caption(f"Status: `{v.status.upper()}` | Built: {v.created_at.strftime('%Y-%m-%d')}")
            
            with st.expander("📦 VIEW BUILD PACKAGE"):
                tab1, tab2 = st.tabs(["SCRIPT & PLAN", "SOCIAL PACKAGE"])
                with tab1:
                    if v.plan:
                        st.markdown("**HOOK**")
                        st.code(v.plan.hook, language="markdown")
                        st.markdown("**CONCEPT**")
                        st.code(v.plan.concept, language="markdown")
                        st.markdown("**BEATS**")
                        if v.plan.beats:
                            st.code("\n".join([f"- {b}" for b in v.plan.beats]), language="markdown")
                    else:
                        st.warning("No plan data found.")
                with tab2:
                    if v.post_package:
                        options = v.post_package.caption_options
                        if not options and v.post_package.selected_caption:
                            options = [v.post_package.selected_caption]
                            
                        if options:
                            st.markdown("**CAPTION OPTIONS**")
                            for idx, opt in enumerate(options):
                                st.code(opt, language="markdown")
                                
                        if v.post_package.hashtags:
                            st.markdown("**HASHTAGS**")
                            st.code(" ".join(v.post_package.hashtags), language="markdown")
                        
                        with st.expander("View Raw Packaging Strategy"):
                            st.markdown(v.post_package.packaging_notes)
                    else:
                        st.warning("Social package not built yet.")

    if in_build:
        st.divider()
        st.markdown(f"### ⏳ IN-BUILD ({len(in_build)})")
        for v in in_build:
            with st.container(border=True):
                ca, cb = st.columns([4, 1])
                ca.markdown(f"**{v.title.upper()}**")
                ca.caption(f"Status: `PLANNING` | Pipeline active...")
                if cb.button("🗑️ CANCEL", key=f"cancel_{v.id}", use_container_width=True, type="secondary"):
                    video_repo.delete(v.id)
                    st.toast(f"🗑️ Cancelled Build: {v.title}")
                    st.rerun()
