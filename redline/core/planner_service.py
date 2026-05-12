from .workflow_service import WorkflowService
from redline.utils.prompts import load_prompt
from redline.models.video import VideoPlan, Video
import json

class PlannerService(WorkflowService):
    def generate_plan(self, idea_title: str, idea_summary: str) -> VideoPlan:
        system_prompt = self.get_system_context()
        planner_prompt_template = load_prompt("02-video-planner.md")
        
        prompt = f"""
{planner_prompt_template}

Selected Idea:
Title: {idea_title}
Summary: {idea_summary}

Generate the exact markdown block as requested above. Do not output JSON.
"""
        
        response = self.llm.generate(prompt, system_prompt)
        raw_text = response["raw_text"]
        
        import re
        
        def extract_field(field_name, default=""):
            # Flexible match for `- field:`, `- **field**:`, `field:`, etc.
            # Captures everything until the next line that looks like a field or a header.
            pattern = r'(?:^|\n)\s*(?:-\s*)?\**' + field_name + r'\**\s*:\s*(.*?)(?=\n\s*(?:-\s*)?\**[a-z_]+\**\s*:|\n\s*##|$)'
            match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else default

        hook = extract_field("hook")
        concept = extract_field("topic") or extract_field("core_payoff")
        cta = extract_field("cta") or extract_field("loop_strategy")
        
        # Extract beats/shots
        shot_raw = extract_field("shot_sequence")
        beats = []
        if shot_raw:
            # Split by line and remove bullets/numbers
            lines = shot_raw.split('\n')
            beats = [re.sub(r'^[\s\-\*\d\.]+ *', '', line).strip() for line in lines if line.strip()]
            
        # Extract notes
        timing = extract_field("timing_notes")
        risk = extract_field("main_risk")
        notes = [n for n in [timing, risk] if n]
            
        return VideoPlan(
            hook=hook or "See raw plan.",
            concept=concept or "See raw plan.",
            beats=beats or ["See raw sequence in plan."],
            cta=cta or "",
            production_notes=notes
        )
