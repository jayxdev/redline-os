import streamlit as st
from redline.db.repositories.rules_repo import RulesRepository
from redline.db.repositories.base_repo import BaseRepository
from redline.models.pattern_memory import PatternMemory
from redline.utils.auth import check_password

if not check_password():
    st.stop()

st.title("🧠 Patterns & Rules")

rules_repo = RulesRepository()
pattern_repo = BaseRepository("patterns", PatternMemory)

tab1, tab2 = st.tabs(["Active Rules", "Pattern Memory"])

with tab1:
    latest_rules = rules_repo.get_latest_active()
    if latest_rules:
        st.subheader(f"Current Ruleset {latest_rules.ruleset_id} (v{latest_rules.version})")
        st.markdown(latest_rules.rules_markdown)
        
        with st.expander("Change History"):
            for change in latest_rules.change_summary:
                st.write(f"- {change}")
    else:
        st.info("No active ruleset found in database.")
        if st.button("Initialize Default Rules"):
            from redline.utils.prompts import load_prompt
            from redline.models.rules_memory import RulesMemory
            default_rules = load_prompt("rules.md", base_path="memory")
            new_rules = RulesMemory(
                ruleset_id="rules-init",
                version=1,
                rules_markdown=default_rules,
                change_summary=["Initial migration from Markdown memory"]
            )
            rules_repo.create(new_rules)
            st.rerun()

with tab2:
    st.subheader("Learned Patterns")
    patterns = pattern_repo.list()
    
    if not patterns:
        st.write("No patterns extracted yet.")
    else:
        for p in patterns:
            with st.expander(f"{p.type.upper()}: {p.title} ({p.confidence} confidence)"):
                st.markdown(p.statement)
                st.caption(f"Evidence: {len(p.evidence_video_ids)} videos, {len(p.evidence_analysis_ids)} reviews")
                if st.button("Archive Pattern", key=f"arch_{p.id}"):
                    pattern_repo.update(p.id, {"status": "archived"})
                    st.rerun()
