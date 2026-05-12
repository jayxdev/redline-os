import streamlit as st
import os
from dotenv import load_dotenv
from redline.providers.mongo.client import MongoManager
from redline.db.repositories.base_repo import BaseRepository
from redline.models.idea import Idea
from redline.models.video import Video
from redline.models.run_log import RunLog
from redline.db.repositories.run_log_repo import RunLogRepository
from redline.utils.auth import check_password
from datetime import datetime, timedelta

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Redline Cult OS",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not check_password():
    st.stop()

# Initialize MongoDB
@st.cache_resource
def init_db():
    manager = MongoManager()
    return manager.get_db()

db = init_db()
idea_repo = BaseRepository("ideas", Idea)
video_repo = BaseRepository("videos", Video)
run_repo = RunLogRepository()

# Custom CSS for adaptive premium look
st.markdown("""
<style>
    :root {
        --card-bg: #f8f9fa;
        --card-border: #e0e0e0;
        --text-color: #262730;
        --subtext-color: #666666;
        --accent-color: #ff4b4b;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg: #1a1c24;
            --card-border: #30363d;
            --text-color: #e0e0e0;
            --subtext-color: #aaaaaa;
        }
    }

    .stApp { color: var(--text-color); }
    
    .card {
        background-color: var(--card-bg);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid var(--card-border);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        border-color: var(--accent-color);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.1);
    }

    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .status-online { background-color: #00ff0022; color: #00ff00; border: 1px solid #00ff0055; }
    .status-idle { background-color: #ffff0022; color: #ffff00; border: 1px solid #ffff0055; }
</style>
""", unsafe_allow_html=True)

# 0. Define Pages for Navigation
def dashboard():
    # Previous app.py logic for Dashboard
    st.title("🏎️ REDLINE COMMAND CENTER")
    
    # Row 1: Agent Status & Metrics
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 ACTIVE AGENTS")
        agents = [
            {"name": "Content Researcher", "status": "Online", "activity": "Scanning trends..."},
            {"name": "Scripting Engine", "status": "Idle", "activity": "Waiting for idea..."},
            {"name": "Data Analyst", "status": "Online", "activity": "Syncing MongoDB..."}
        ]
        for agent in agents:
            badge_class = "status-online" if agent["status"] == "Online" else "status-idle"
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <span style="font-weight: bold;">{agent['name'].upper()}</span> 
                <span class="status-badge {badge_class}">{agent['status'].upper()}</span>
                <div style="font-size: 0.85em; color: #888;">{agent['activity']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 SYSTEM HEALTH")
        c1, c2, c3 = st.columns(3)
        c1.metric("IDEAS", idea_repo.collection.count_documents({}))
        c2.metric("VIDEOS", video_repo.collection.count_documents({}))
        latest_runs = run_repo.get_latest_runs(limit=1)
        last_sync = latest_runs[0].created_at.strftime("%H:%M") if latest_runs else "N/A"
        c3.metric("LAST SYNC", last_sync)
        st.markdown("---")
        st.markdown("**RECENT JOB RUNS**")
        actual_runs = run_repo.get_latest_runs(limit=3)
        if not actual_runs:
            st.caption("No job runs recorded yet.")
        else:
            for run in actual_runs:
                status_icon = "✅" if run.status == "completed" else "❌" if run.status == "failed" else "⏳"
                st.caption(f"{status_icon} {run.job_name.upper()} - {run.status.upper()} ({run.created_at.strftime('%Y-%m-%d %H:%M')})")
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Recent Ideas
    st.subheader("💡 RECENT IDEAS")
    recent_ideas = idea_repo.list(limit=5, filters={"status": "new"}, sort=[("created_at", -1)])
    if not recent_ideas:
        st.info("No new ideas found. Head to the IDEATION STATION to generate some!")
    else:
        cols = st.columns(len(recent_ideas))
        for idx, idea in enumerate(recent_ideas):
            with cols[idx]:
                st.markdown(f"""
                <div class="card" style="height: 180px; overflow: hidden; margin-bottom: 5px;">
                    <div style="font-weight: bold; margin-bottom: 8px; color: var(--accent-color);">{idea.title.upper()}</div>
                    <div style="font-size: 0.85em; color: var(--subtext-color);">{idea.summary[:80]}...</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Direct Actions
                ca, cr = st.columns(2)
                if ca.button("✅", key=f"app_{idea.id}", help="Approve and Launch", use_container_width=True):
                    idea_repo.update(idea.id, {"status": "selected"})
                    
                    # Trigger instant build
                    with st.spinner(f"🚀 Building {idea.title}..."):
                        from redline.core.automation_service import AutomationService
                        auto_service = AutomationService()
                        auto_service.run_daily_pipeline(trigger_type="instant-approve")
                    
                    st.toast(f"✅ Final Build Package Ready: {idea.title}")
                    st.rerun()
                
                if cr.button("❌", key=f"rej_{idea.id}", help="Permanently Delete", use_container_width=True):
                    idea_repo.delete(idea.id)
                    st.toast(f"🗑️ Deleted: {idea.title}")
                    st.rerun()

    st.markdown("---")
    if st.button("🚀 TRIGGER DAILY PIPELINE", use_container_width=True):
        from redline.core.automation_service import AutomationService
        auto_service = AutomationService()
        with st.spinner("Executing Pipeline..."):
            success = auto_service.run_daily_pipeline(trigger_type="manual")
            if success:
                st.success("Pipeline completed! Rerunning...")
                st.rerun()

# 1. Map Pages
pg_dashboard = st.Page(dashboard, title="DASHBOARD", icon="🏎️", default=True)
pg_videos = st.Page("pages/01_videos.py", title="VIDEOS", icon="🎬")
pg_ideas = st.Page("pages/02_ideas.py", title="IDEATION STATION", icon="💡")
pg_planner = st.Page("pages/03_video_planner.py", title="VIDEO PLANNER", icon="🎬")
pg_packaging = st.Page("pages/04_caption_packaging.py", title="CAPTION PACKAGING", icon="📦")
pg_logger = st.Page("pages/05_results_logger.py", title="RESULTS LOGGER", icon="📊")
pg_review = st.Page("pages/06_weekly_review.py", title="WEEKLY REVIEW", icon="📅")
pg_patterns = st.Page("pages/07_patterns_and_rules.py", title="PATTERNS & RULES", icon="🎭")
pg_history = st.Page("pages/08_run_history.py", title="RUN HISTORY", icon="📜")
pg_admin = st.Page("pages/09_admin.py", title="ADMIN SETTINGS", icon="⚙️")

# 2. Run Navigation
pg = st.navigation({
    "MAIN": [pg_dashboard],
    "CONTENT ENGINE": [pg_ideas, pg_planner, pg_packaging, pg_videos],
    "INTELLIGENCE": [pg_review, pg_patterns],
    "SYSTEM": [pg_logger, pg_history, pg_admin]
})

# 3. Draw Sidebar (Custom header above nav)
from redline.utils.ui import draw_sidebar
draw_sidebar()

# 4. Execute Page
pg.run()
