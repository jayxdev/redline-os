# Idea Generator Automation Prompt

Use this prompt in an automation that reads memory and proposes new ideas.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- In the thread instructions, tell Codex to read the listed memory files before generating ideas.
- Good fit for a scheduled daily automation or an on-demand thread.
- For this project, persist the generated idea set to `memory/ideas.md` only.
- Do not create any other memory file, scratch file, or automation continuity file.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- `memory/rules.md`
- `memory/ideas.md`
- `memory/patterns/winning-hooks.md`
- `memory/patterns/winning-formats.md`
- `memory/patterns/failed-patterns.md`
- Latest baseline or pattern snapshots from `memory/patterns/*.md`
- Optional trend input from the operator

## Prompt

You are generating new Redline Cult short-form content ideas.

Read the provided memory carefully before generating anything.

Task:
- Generate 5 strong video ideas for the current cycle
- Use winning patterns where appropriate
- Avoid repeated failed patterns
- Stay within the Redline Cult brand

For each idea, return:
- `title`
- `hook`
- `concept`
- `visual sequence`
- `why_it_should_work`
- `risk`
- `pattern_tags`

Selection rules:
- Prioritize ideas that fit current winning hooks or winning formats
- If a known winner is reused, improve the angle instead of repeating it directly
- Do not generate generic montage ideas
- Do not generate ideas that conflict with current rules

After the 5 ideas, return:
- `top_2_recommendations`
- `why_these_two`

Output format:

Your response MUST contain exactly two sections:

**Section 1 — Summary:** Write a short paragraph summarising the ideas you generated and why you chose the top 2. Start with `## Summary`.

**Section 2 — Structured Output:** Return a single fenced JSON block. Start with `## Output`, then:

```json
{
  "ideas": [
    {
      "title": "...",
      "hook": "...",
      "concept": "...",
      "visual_sequence": "...",
      "why_it_should_work": "...",
      "risk": "...",
      "pattern_tags": ["tag1", "tag2"]
    }
  ],
  "top_2_recommendations": ["Idea Title 1", "Idea Title 2"],
  "why_these_two": "..."
}
```

Both sections are required. The JSON must be valid and parseable.

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- append or refresh the current idea set in `memory/ideas.md`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- update pattern files
- update `memory/rules.md`
