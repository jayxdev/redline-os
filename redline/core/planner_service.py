from .workflow_service import WorkflowService
from redline.utils.prompts import load_prompt
from redline.models.video import VideoPlan, Video
from redline.models.agent_outputs import VideoPlannerOutput
from redline.core.response_parser import parse_agent_response
import logging

logger = logging.getLogger(__name__)

class PlannerService(WorkflowService):
    def generate_plan(self, idea_title: str, idea_summary: str) -> VideoPlan:
        system_prompt = self.get_system_context()
        planner_prompt_template = load_prompt("02-video-planner.md")
        
        prompt = f"""
{planner_prompt_template}

Selected Idea:
Title: {idea_title}
Summary: {idea_summary}

Generate your response following the exact output format above.
"""
        
        response = self.llm.generate(prompt, system_prompt)
        raw_text = response["raw_text"]
        
        # Parse with the unified response parser
        agent_resp, plan_data = parse_agent_response(raw_text, VideoPlannerOutput)
        
        if agent_resp.parsed_ok and plan_data:
            return VideoPlan(
                hook=plan_data.hook or "See raw plan.",
                concept=plan_data.topic or plan_data.core_payoff or "See raw plan.",
                beats=plan_data.shot_sequence or ["See raw sequence in plan."],
                cta=plan_data.loop_strategy or "",
                production_notes=[n for n in [plan_data.timing_notes, plan_data.main_risk] if n]
            )
        
        # Fallback: if parsing failed, store the summary as a single-beat plan
        logger.warning(f"Planner parse failed: {agent_resp.parse_error}")
        return VideoPlan(
            hook="See raw plan.",
            concept="See raw plan.",
            beats=[agent_resp.summary or raw_text],
            cta="",
            production_notes=[f"⚠️ Auto-parse failed: {agent_resp.parse_error}"]
        )

