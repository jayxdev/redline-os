# Reality Check Automation Prompt

Use this prompt in a weekly or biweekly automation to challenge the current approach.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- This is optional and should not be responsible for writing memory directly.
- Good fit for a weekly or biweekly strategy-check automation.
- In the thread instructions, tell Codex to read recent logs, analyses, and current rules, then return recommendations only.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- Latest 10-20 video logs
- Latest weekly analyses
- Current `memory/rules.md`

## Prompt

You are performing a brutal strategic review of the Redline Cult system.

Task:
- Identify where the system is overthinking
- Identify where execution quality is weak
- Identify where the current rules may be stale or too vague
- Identify what should be doubled down on immediately

Return:
1. `what_is_working`
2. `what_is_wasting_time`
3. `where_the_data_is_being_misread`
4. `what_to_stop`
5. `what_to_double_down_on`
6. `what_to_test_next`

Rules:
- Be direct
- Use evidence from memory
- Prefer operational advice over abstract strategy

Output format:

Your response MUST contain exactly two sections:

**Section 1 — Summary:** Write a direct, no-bullshit strategic overview. Start with `## Summary`.

**Section 2 — Structured Output:** Return a single fenced JSON block. Start with `## Output`, then:

```json
{
  "what_is_working": "...",
  "what_is_wasting_time": "...",
  "where_the_data_is_being_misread": "...",
  "what_to_stop": "...",
  "what_to_double_down_on": "...",
  "what_to_test_next": "..."
}
```

Both sections are required. The JSON must be valid and parseable.

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- return recommendations only

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- directly edit memory files
