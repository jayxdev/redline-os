"""
Unified agent response parser.

Every LLM call in the system should route through parse_agent_response()
to get consistent, validated output with graceful fallbacks.
"""
import json
import re
import logging
from typing import TypeVar, Type, Optional, Generic
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class AgentResponse(BaseModel):
    """
    Standardised wrapper returned by parse_agent_response().

    Attributes:
        raw_text:    The full, unmodified LLM output (always preserved).
        summary:     The human-readable text section extracted before the JSON.
        data:        The parsed Pydantic model (None if parsing failed).
        parsed_ok:   True if JSON was extracted and validated successfully.
        parse_error: Diagnostic message when parsed_ok is False.
    """
    raw_text: str
    summary: str = ""
    data: Optional[dict] = None  # serialised from the Pydantic model
    parsed_ok: bool = False
    parse_error: Optional[str] = None


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

def _extract_summary(text: str) -> str:
    """Pull out the ## Summary section (everything between ## Summary and ## Output / ```json)."""
    # Look for an explicit ## Summary header
    summary_match = re.search(
        r'##\s*Summary\s*\n(.*?)(?=##\s*Output|```json|```\s*json|\Z)',
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if summary_match:
        return summary_match.group(1).strip()
    
    # Fallback: everything before the first fenced JSON block
    pre_json = re.split(r'```\s*json', text, maxsplit=1, flags=re.IGNORECASE)
    if len(pre_json) > 1:
        return pre_json[0].strip()
    
    # No JSON block at all — the whole text is the "summary"
    return text.strip()


def _extract_json_block(text: str) -> Optional[str]:
    """Extract the first fenced ```json ... ``` block."""
    match = re.search(r'```\s*json\s*\n(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _try_bare_json(text: str) -> Optional[str]:
    """Last-resort: find the outermost { ... } or [ ... ] in the text."""
    # Try object
    obj_match = re.search(r'(\{[\s\S]*\})', text)
    if obj_match:
        candidate = obj_match.group(1)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    
    # Try array
    arr_match = re.search(r'(\[[\s\S]*\])', text)
    if arr_match:
        candidate = arr_match.group(1)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    
    return None


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def parse_agent_response(raw_text: str, schema: Type[T]) -> tuple[AgentResponse, Optional[T]]:
    """
    Parse an LLM response into a validated Pydantic model.

    Returns a tuple of (AgentResponse metadata, parsed model or None).

    Usage::

        from redline.models.agent_outputs import VideoPlannerOutput
        resp, plan_data = parse_agent_response(llm_result["raw_text"], VideoPlannerOutput)
        if resp.parsed_ok:
            # plan_data is a fully validated VideoPlannerOutput
            ...
        else:
            # degrade gracefully — resp.summary has the human-readable text
            logger.warning(f"Parse failed: {resp.parse_error}")
    """
    summary = _extract_summary(raw_text)

    # 1. Try fenced JSON block
    json_str = _extract_json_block(raw_text)

    # 2. Fallback: bare JSON
    if json_str is None:
        json_str = _try_bare_json(raw_text)

    if json_str is None:
        return AgentResponse(
            raw_text=raw_text,
            summary=summary,
            parsed_ok=False,
            parse_error="No JSON block found in response.",
        ), None

    # 3. Parse JSON string
    try:
        raw_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return AgentResponse(
            raw_text=raw_text,
            summary=summary,
            parsed_ok=False,
            parse_error=f"JSON decode error: {e}",
        ), None

    # 4. Validate against Pydantic schema
    try:
        model_instance = schema.model_validate(raw_data)
        return AgentResponse(
            raw_text=raw_text,
            summary=summary,
            data=model_instance.model_dump(),
            parsed_ok=True,
        ), model_instance
    except ValidationError as e:
        return AgentResponse(
            raw_text=raw_text,
            summary=summary,
            data=raw_data if isinstance(raw_data, dict) else None,
            parsed_ok=False,
            parse_error=f"Schema validation error: {e}",
        ), None


# ──────────────────────────────────────────────
# Prompt suffix
# ──────────────────────────────────────────────

RESPONSE_FORMAT_SUFFIX = """

---
## RESPONSE FORMAT (MANDATORY)

Your response MUST contain exactly two sections:

### Section 1: Summary
Write a short, human-readable summary of your output. This is displayed directly in the UI.
Start this section with `## Summary`.

### Section 2: Structured Output
Return a single fenced JSON block containing all structured data matching the fields requested above.
Start this section with `## Output` followed by a fenced code block:

```json
{ ... }
```

Both sections are required. The JSON must be valid and parseable.
---
"""


def inject_response_format(prompt_text: str) -> str:
    """Append the standard dual-output instruction to any agent prompt."""
    return prompt_text + RESPONSE_FORMAT_SUFFIX
