import streamlit as st
from redline.db.repositories.base_repo import BaseRepository
from redline.models.run_log import RunLog
from redline.utils.auth import check_password

if not check_password():
    st.stop()

st.title("📜 Run History")

run_repo = BaseRepository("job_runs", RunLog)
runs = run_repo.list(sort=[("created_at", -1)], limit=50)

if not runs:
    st.info("No job runs recorded yet.")
else:
    for run in runs:
        status_color = "green" if run.status == "completed" else "red" if run.status == "failed" else "blue"
        with st.expander(f"{run.created_at.strftime('%Y-%m-%d %H:%M')} - {run.job_name} (:{status_color}[{run.status}])"):
            st.write(f"**Trigger:** {run.trigger_type}")
            if run.error_message:
                st.error(f"Error: {run.error_message}")
            
            st.markdown("#### Steps")
            for step in run.steps:
                step_status = "✅" if step.status == "completed" else "❌" if step.status == "failed" else "⏳"
                st.write(f"{step_status} **{step.name}**: {step.summary or 'No summary'}")
                if step.error:
                    st.caption(f"Error detail: {step.error}")
