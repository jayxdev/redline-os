import streamlit as st
from redline.db.repositories.base_repo import BaseRepository
from redline.models.idea import Idea
from redline.providers.llm.nvidia_provider import NVIDIAProvider
from redline.providers.mongo.client import MongoManager
from redline.utils.auth import check_password
import os
import uuid

if not check_password():
    st.stop()

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

            # 2. Build prompt with structured output format
            from redline.core.response_parser import parse_agent_response, inject_response_format
            from redline.models.agent_outputs import IdeaGeneratorOutput
            
            prompt = inject_response_format(f"""Generate 3 viral content ideas for 'Redline Cult'. 
            
            HISTORY & MEMORY CONTEXT:
            {memory_context}
            
            INSTRUCTIONS:
            Based on the context above, generate 3 NEW ideas.
            For each idea, provide title, hook, concept, visual_sequence, why_it_should_work, risk, and pattern_tags.
            
            Return JSON with an "ideas" array and "top_2_recommendations" list.""")
            
            # Capture the stream
            full_response = ""
            container = st.empty()
            for chunk in llm.generate_stream(prompt):
                full_response += chunk
                container.markdown(full_response)
            
            st.success("Generation complete! Saving to database...")
            
            # Parse with unified response parser
            try:
                agent_resp, gen_data = parse_agent_response(full_response, IdeaGeneratorOutput)
                parsed_count = 0
                
                if agent_resp.parsed_ok and gen_data:
                    for item in gen_data.ideas:
                        new_idea = Idea(
                            idea_id=str(uuid.uuid4())[:8],
                            title=item.title,
                            summary=item.concept or item.why_it_should_work or "AI Generated",
                            angle=item.hook or "General",
                            rationale=item.why_it_should_work or "Potential Viral Content",
                            status="new",
                            tags=item.pattern_tags
                        )
                        idea_repo.create(new_idea)
                        st.toast(f"💾 Stored: {item.title}", icon="✅")
                        parsed_count += 1
                
                if parsed_count > 0:
                    st.success(f"✅ Successfully stored {parsed_count} ideas in the database.")
                else:
                    # FAIL-SAFE: Save raw text as one big idea
                    from datetime import datetime
                    fallback_idea = Idea(
                        idea_id=f"raw-{str(uuid.uuid4())[:4]}",
                        title=f"Bulk Generation - {datetime.now().strftime('%H:%M')}",
                        summary="Parsing failed, saving raw text for manual review.",
                        angle="Raw Output",
                        rationale=full_response,
                        status="new"
                    )
                    idea_repo.create(fallback_idea)
                    st.warning(f"⚠️ Could not parse structured ideas ({agent_resp.parse_error}), saved the entire response as one record.")
                    
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
                from redline.utils.ui import run_autonomous_agents_ui
                run_autonomous_agents_ui(idea)
            
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

# End of page
