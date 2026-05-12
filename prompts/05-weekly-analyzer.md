# Weekly Analyzer Automation Prompt

Use this prompt in an automation that reviews a batch of video logs and produces a weekly analysis file.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- Run this only after the weekly video logs are already updated.
- Good fit for a recurring weekly automation.
- In the thread instructions, tell Codex to read recent `memory/videos/*.md` files and write one new file to `memory/analysis/`.
- If your workflow relies on screenshots, run the screenshot review chat first and only then run this step.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- 7-10 recent files from `memory/videos/*.md`
- `memory/rules.md`
- `memory/patterns/winning-hooks.md`
- `memory/patterns/winning-formats.md`
- `memory/patterns/failed-patterns.md`
- `memory/templates/weekly-review-template.md`

## Prompt

You are running a weekly Redline Cult performance review.

Task:
- Analyze the provided video logs as a batch
- Identify repeated winners, repeated losers, and unclear signals
- Distinguish between hook issues, topic issues, pacing issues, and payoff issues
- Recommend what to repeat, test, stop, and gather more data on

Constraints:
- Do not overfit from one outlier
- Only call a pattern "repeated" if there is evidence across multiple videos
- Keep conclusions evidence-based and concise

Return:
- a completed weekly review in the project template structure
- a short promotion candidate summary for hook patterns, format patterns, failed patterns, and rule changes

Output format:

```md
## Weekly Review
[paste completed weekly review markdown]

## Promotion Candidates
- hooks_to_add:
- formats_to_add:
- failures_to_add:
- rules_to_change:
```

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- create one new file in `memory/analysis/`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- directly edit pattern files
- directly edit `memory/rules.md`
