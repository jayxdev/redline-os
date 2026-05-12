import streamlit as st
from redline.db.repositories.base_repo import BaseRepository
from redline.models.idea import Idea
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.providers.mongo.client import MongoManager
from redline.utils.auth import check_password
import os
import uuid

from redline.utils.ui import draw_sidebar

if not check_password():
    st.stop()

draw_sidebar()

st.title("💡 Idea Generation")

# Repositories
@st.cache_resource
def get_idea_repo():
    return BaseRepository("ideas", Idea)

idea_repo = get_idea_repo()

# LLM Provider
def get_llm():
    from redline.core.config_service import ConfigService
    config = ConfigService()
    
    api_key = config.get("NVIDIA_API_KEY")
    model = config.get("DEFAULT_LLM_MODEL")
    
    if not api_key or not model:
        st.error("⚠️ AI Configuration Incomplete. Please set your NVIDIA API Key and Default Model in the Admin Settings.")
        st.stop()
    return NVIDIAProvider(api_key, model)

# Sidebar actions
with st.sidebar:
    st.header("Actions")
    if st.button("Generate New Ideas", use_container_width=True):
        st.session_state.generating = True

if 'generating' in st.session_state and st.session_state.generating:
    st.subheader("Generating new content ideas...")
    llm = get_llm()
    if llm:
        with st.spinner("Analyzing memory & consulting the AI..."):
            # 1. Fetch Context Memory
            from redline.db.repositories.base_repo import BaseRepository
            from redline.models.weekly_analysis import WeeklyAnalysis
            from redline.db.repositories.rules_repo import RulesRepository
            
            analysis_repo = BaseRepository("weekly_analyses", WeeklyAnalysis)
            rules_repo = RulesRepository()
            
            latest_analysis = analysis_repo.list(sort=[("week_end", -1)], limit=1)
            active_rules = rules_repo.get_latest_active()
            
            memory_context = ""
            if latest_analysis:
                analysis = latest_analysis[0]
                memory_context += f"\nLatest Wins: {', '.join(analysis.wins)}\nLatest Losses: {', '.join(analysis.losses)}"
            
            if active_rules:
                memory_context += f"\nActive Channel Rules:\n{active_rules.rules_markdown[:1000]}"

            # 2. Update prompt with context
            prompt = f"""Generate 3 viral content ideas for 'Redline Cult'. 
            
            HISTORY & MEMORY CONTEXT:
            {memory_context}
            
            INSTRUCTIONS:
            Based on the context above, generate 3 NEW ideas.
            For each idea, provide:
            - Title: [Short Title]
            - Summary: [One sentence]
            - Angle: [The hook]
            - Rationale: [Why it will go viral based on memory]
            
            Return in a clean format."""
            
            # Capture the stream
            full_response = ""
            container = st.empty()
            for chunk in llm.generate_stream(prompt):
                full_response += chunk
                container.markdown(full_response)
            
            st.success("Generation complete! Saving to database...")
            
            # Resilient Parser
            try:
                import re
                parsed_count = 0
                
                # Split by common idea delimiters
                blocks = re.split(r'(?i)Idea \d+:|Idea:|Title:|\d+\. ', full_response)
                
                for block in blocks:
                    clean_block = block.strip()
                    if len(clean_block) < 30: continue # Skip fragments
                    
                    # Extract fields with flexible lookups
                    lines = [l.strip() for l in clean_block.split('\n') if l.strip()]
                    if not lines: continue
                    
                    # HEURISTIC: First line is the title, clean it up
                    title = lines[0].replace('**', '').replace('-', '').replace('#', '').strip()[:100]
                    if not title: title = "Unnamed Idea"
                    
                    summary = "AI Generated"
                    angle = "General"
                    rationale = "Potential Viral Content"
                    
                    for line in lines:
                        l_low = line.lower()
                        if "summary:" in l_low: summary = line.split(":", 1)[1].strip()
                        if "angle:" in l_low: angle = line.split(":", 1)[1].strip()
                        if "rationale:" in l_low: rationale = line.split(":", 1)[1].strip()

                    new_idea = Idea(
                        idea_id=str(uuid.uuid4())[:8],
                        title=title,
                        summary=summary,
                        angle=angle,
                        rationale=rationale,
                        status="new"
                    )
                    idea_repo.create(new_idea)
                    st.toast(f"💾 Stored: {title}", icon="✅")
                    parsed_count += 1
                
                if parsed_count > 0:
                    st.success(f"✅ Successfully stored {parsed_count} ideas in the database.")
                else:
                    # FAIL-SAFE: Save raw text as one big idea
                    fallback_idea = Idea(
                        idea_id=f"raw-{str(uuid.uuid4())[:4]}",
                        title=f"Bulk Generation - {datetime.now().strftime('%H:%M')}",
                        summary="Parsing failed, saving raw text for manual review.",
                        angle="Raw Output",
                        rationale="Fail-safe backup",
                        status="new"
                    )
                    # We store the raw text in the rationale or a new field
                    fallback_idea.rationale = full_response
                    idea_repo.create(fallback_idea)
                    st.warning("⚠️ Could not split ideas, saved the entire response as one record.")
                    
            except Exception as e:
                st.error(f"❌ Storage Failed: {str(e)}")
    
    if st.button("Finish & Refresh"):
        st.session_state.generating = False
        st.rerun()

st.divider()

st.subheader("💡 Decision Queue")
st.caption("Approving an idea instantly triggers the Autonomous Production Pipeline.")

# List only NEW ideas for decision making
ideas = idea_repo.list(filters={"status": "new"}, sort=[("created_at", -1)])

if not ideas:
    st.info("The hopper is empty. Hit 'Consult the AI' above to generate fresh ideas.")
else:
    for idea in ideas:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"### {idea.title}")
            c1.write(f"**Angle:** {idea.angle}")
            c1.write(f"**Summary:** {idea.summary}")
            
            with c1.expander("Why this works (Rationale)"):
                st.write(idea.rationale)
                st.caption(f"Generated: {idea.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            if c2.button("Approve ✅", key=f"app_{idea.id}", use_container_width=True, type="primary"):
                # 1. Update Status
                idea_repo.update(idea.id, {"status": "selected"})
                
                # 2. Trigger Production AUTOMATICALLY
                from redline.core.automation_service import AutomationService
                auto = AutomationService()
                with st.spinner(f"🚀 Launching production for {idea.title}..."):
                    if auto.run_daily_pipeline(trigger_type="auto_approve"):
                        st.toast(f"Autonomous Production Complete for: {idea.title}")
                        st.rerun()
            
            if c2.button("Reject ❌", key=f"rej_{idea.id}", use_container_width=True):
                idea_repo.delete(idea.id)
                st.toast(f"🗑️ Permanently Deleted: {idea.title}")
                st.rerun()

# Show Approved Queue (Ready for the next Pipeline run)
approved = idea_repo.list(filters={"status": "selected"})
if approved:
    st.divider()
    with st.expander(f"📥 Approved Queue ({len(approved)}) - Ready for Production", expanded=False):
        for a in approved:
            st.write(f"- **{a.title}**")

# 5. Database Heartbeat (Diagnostic)
st.divider()
with st.sidebar:
    st.markdown("### 🗄️ Storage Heartbeat")
    total_ideas = len(idea_repo.list(limit=1000))
    new_ideas = len(idea_repo.list(filters={"status": "new"}))
    st.metric("Total Ideas", total_ideas)
    st.metric("New Pending", new_ideas)
    
    db_name = MongoManager().get_db().name
    st.caption(f"📍 DB: `{db_name}` | Coll: `ideas`")
    
    if st.button("🧹 Purge Rejected", use_container_width=True):
        idea_repo.collection.delete_many({"status": "rejected"})
        st.rerun()
