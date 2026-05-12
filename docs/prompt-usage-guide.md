# Prompt Usage Guide

This file answers one question:

`What exactly do I paste, and when?`

## Paste Into Chat

### Fastest option

Folder:
- `copy-ready/`

These are plain paste-only files with no wrapper instructions.

### Weekly analytics review

Best file:
- `copy-ready/08-weekly-screenshot-review.txt`

What to paste:
- Paste the full file contents.

Alternative source:
- `prompts/08-screenshot-review-chat.md`
- If you use that file instead, paste only the text inside the fenced code block.

Then:
- upload your screenshots
- tell the chat which video ID or filename each screenshot belongs to

## Do Not Paste By Default

These files are prompt definitions for automation or deliberate manual simulation:

- `prompts/00-system-role.md`
- `prompts/01-idea-generator.md`
- `prompts/02-video-planner.md`
- `prompts/03-caption-hashtag-research.md`
- `prompts/04-results-logger.md`
- `prompts/05-weekly-analyzer.md`
- `prompts/06-pattern-promoter.md`
- `prompts/07-reality-check.md`

Use them when:
- you are wiring automations
- you want to manually simulate a specific step on purpose

If running one manually:
1. Open the file
2. Copy only the content under `## Prompt`
3. Provide the inputs listed in that file
4. Ask for the exact output format shown there

## Best Simple Rule

Right now, the main prompt you actually paste into a chat is:

- `copy-ready/08-weekly-screenshot-review.txt`

Everything else is system structure unless you intentionally want to run a step manually.

## Copy-Ready Manual Files

- `copy-ready/01-idea-generator.txt`
- `copy-ready/02-video-planner.txt`
- `copy-ready/03-caption-hashtag-research.txt`
- `copy-ready/04-results-logger.txt`
- `copy-ready/05-weekly-analyzer.txt`
- `copy-ready/06-pattern-promoter.txt`
- `copy-ready/07-reality-check.txt`
- `copy-ready/08-weekly-screenshot-review.txt`
