from .workflow_service import WorkflowService
from utils.prompts import load_prompt
from models.video import VideoPlan, Video
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

Generate a detailed video plan in JSON format.
"""
        
        response = self.llm.generate(prompt, system_prompt)
        data = response["parsed_data"]
        
        if not data:
            # Fallback if parsing fails - in production we'd want more robust handling
            raise Exception(f"Failed to parse LLM response: {response['raw_text']}")
            
        return VideoPlan(
            hook=data.get("hook", ""),
            concept=data.get("concept", ""),
            beats=data.get("beats", []),
            cta=data.get("cta", ""),
            production_notes=data.get("production_notes", [])
        )
