# Results Logger Automation Prompt

Use this prompt in an automation that updates a specific video log after posting.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- Use this only when you have direct typed metrics or structured exports.
- This is an alternative to the screenshot review path, not something you must always run.
- In the thread instructions, tell Codex to update only the target file in `memory/videos/`.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- Existing target file from `memory/videos/*.md`
- New metrics provided by the operator or platform export

## Prompt

You are updating an existing Redline Cult video log with new performance data.

Task:
- Read the current video log
- Merge in the provided metrics
- Keep the file tidy and consistent
- Do not change the original concept fields unless the current file is clearly incomplete

Update:
- `Status`
- `Performance`
- `Qualitative Notes`
- `Verdict`

Decision rules:
- If data is too early, mark the verdict as provisional in notes
- Do not call something a confirmed winner based on one early metric snapshot
- Keep interpretation separate from raw metrics

Output format:

```md
## Updated File
[paste the full updated markdown file]
```

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- update only one file inside `memory/videos/`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- update `memory/rules.md`
- update pattern files
