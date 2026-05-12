# Video Planner Automation Prompt

Use this prompt in an automation that converts one selected idea into an execution-ready video plan and a video log draft.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- Use it after an idea has already been selected.
- Best run on demand, not on a blind recurring schedule.
- In the thread instructions, tell Codex to create one new file in `memory/videos/` from the returned log draft.
- This step should usually be followed by `prompts/03-caption-hashtag-research.md`.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- Selected idea
- `memory/rules.md`
- `memory/patterns/winning-hooks.md`
- `memory/patterns/winning-formats.md`
- `memory/patterns/failed-patterns.md`
- `memory/templates/video-log-template.md`

## Prompt

You are converting one chosen Redline Cult idea into a high-retention short video plan.

Task:
- Build a post-ready plan for one video
- Keep the structure aggressive, premium, and fast
- Use current memory rules and known patterns

Return:
- `video_id`
- `topic`
- `format_type`
- `hook`
- `core_payoff`
- `loop_strategy`
- `opening_shot`
- `shot_sequence`
- `timing_notes`
- `expected_retention_driver`
- `why_this_should_work`
- `main_risk`
- `pattern_tags`

Then return a second section:
- a markdown block already formatted to paste into a new file in `memory/videos/`

Requirements:
- Opening must stop scroll immediately
- Sequence must escalate
- Payoff must land before the ending
- The log draft must match the project template structure

Output format:

```md
## Video Plan
- video_id:
- topic:
- format_type:
- hook:
- core_payoff:
- loop_strategy:
- opening_shot:
- shot_sequence:
- timing_notes:
- expected_retention_driver:
- why_this_should_work:
- main_risk:
- pattern_tags:

## Video Log Draft
[paste complete markdown file content]
```

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- create one new file in `memory/videos/`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- modify pattern files
- modify `memory/rules.md`
