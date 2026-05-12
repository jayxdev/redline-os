import streamlit as st
import os
from dotenv import load_dotenv
from providers.mongo.client import MongoManager
from db.repositories.base_repo import BaseRepository
from models.idea import Idea
from models.video import Video
from models.run_log import RunLog
from db.repositories.run_log_repo import RunLogRepository
from utils.auth import check_password
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

# Sidebar
from utils.ui import draw_sidebar
draw_sidebar()

# Dashboard Header
st.title("🏎️ Redline Cult Command Center")

# Row 1: Agent Status & Metrics
col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 Active Agents")
    
    # Mocking agent status for now
    agents = [
        {"name": "Content Researcher", "status": "Online", "activity": "Scanning trends..."},
        {"name": "Scripting Engine", "status": "Idle", "activity": "Waiting for idea..."},
        {"name": "Data Analyst", "status": "Online", "activity": "Syncing MongoDB..."}
    ]
    
    for agent in agents:
        badge_class = "status-online" if agent["status"] == "Online" else "status-idle"
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <span style="font-weight: bold;">{agent['name']}</span> 
            <span class="status-badge {badge_class}">{agent['status']}</span>
            <div style="font-size: 0.85em; color: #888;">{agent['activity']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 System Health")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ideas", idea_repo.collection.count_documents({}))
    c2.metric("Videos", video_repo.collection.count_documents({}))
    
    # Get latest run for "Last Sync"
    latest_runs = run_repo.get_latest_runs(limit=1)
    last_sync = latest_runs[0].created_at.strftime("%H:%M") if latest_runs else "N/A"
    c3.metric("Last Sync", last_sync)
    
    st.markdown("---")
    st.markdown("**Recent Job Runs**")
    
    actual_runs = run_repo.get_latest_runs(limit=3)
    if not actual_runs:
        st.caption("No job runs recorded yet.")
    else:
        for run in actual_runs:
            status_icon = "✅" if run.status == "completed" else "❌" if run.status == "failed" else "⏳"
            st.caption(f"{status_icon} {run.job_name} - {run.status.capitalize()} ({run.created_at.strftime('%Y-%m-%d %H:%M')})")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Row 2: Recent Ideas
st.subheader("💡 Recent Ideas")
recent_ideas = idea_repo.list(limit=5, sort=[("created_at", -1)])

if not recent_ideas:
    st.info("No ideas found. Head to the Ideas page to generate some!")
else:
    cols = st.columns(len(recent_ideas))
    for idx, idea in enumerate(recent_ideas):
        with cols[idx]:
            st.markdown(f"""
            <div class="card" style="height: 200px; overflow: hidden;">
                <div style="font-weight: bold; margin-bottom: 8px; color: var(--accent-color);">{idea.title}</div>
                <div style="font-size: 0.85em; color: var(--subtext-color);">{idea.summary[:100]}...</div>
            </div>
            """, unsafe_allow_html=True)

# Footer Quick Actions
st.markdown("---")
if st.button("🚀 Manually Trigger Daily Pipeline", use_container_width=True):
    st.toast("Daily pipeline started...")
