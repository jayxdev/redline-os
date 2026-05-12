# Pattern Promoter Automation Prompt

Use this prompt in an automation that updates the long-term memory after a weekly review.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- Run this only after `prompts/05-weekly-analyzer.md` has produced the weekly analysis.
- Good fit for a recurring weekly automation scheduled after the analyzer.
- In the thread instructions, tell Codex exactly which pattern files and rule file it may update.
- Do not run this after a single video or before analysis is complete.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- Latest weekly review from `memory/analysis/*.md`
- Existing files:
  - `memory/patterns/caption-hashtag-patterns.md`
  - `memory/patterns/winning-hooks.md`
  - `memory/patterns/winning-formats.md`
  - `memory/patterns/failed-patterns.md`
  - `memory/rules.md`

## Prompt

You are promoting verified learnings from weekly analysis into the Redline Cult memory system.

Task:
- Read the latest weekly analysis
- Update pattern files with repeated evidence-backed learnings
- Update `rules.md` only where the evidence clearly justifies it
- Keep all files concise and non-contradictory

Promotion rules:
- Add only repeated signals
- Do not remove useful historical knowledge unless it conflicts with stronger evidence
- Rewrite for clarity when needed, but do not bloat the files
- Keep the distinction between confirmed winners, failures, and assumptions clean

Required output:
- full updated content for:
  - `memory/patterns/caption-hashtag-patterns.md`
  - `memory/patterns/winning-hooks.md`
  - `memory/patterns/winning-formats.md`
  - `memory/patterns/failed-patterns.md`
  - `memory/rules.md`
- a short change summary

Output format:

```md
## Updated caption-hashtag-patterns.md
[full file]

## Updated winning-hooks.md
[full file]

## Updated winning-formats.md
[full file]

## Updated failed-patterns.md
[full file]

## Updated rules.md
[full file]

## Change Summary
- 
```

## Memory Update Rule

This automation is allowed to modify:
- `memory/patterns/caption-hashtag-patterns.md`
- `memory/patterns/winning-hooks.md`
- `memory/patterns/winning-formats.md`
- `memory/patterns/failed-patterns.md`
- `memory/rules.md`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- `memory/rules.md`

It should run only after a weekly review, not after single-video results.
