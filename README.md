# Redline Cult Content System

This repo is a feedback-driven content system for short-form car and bike content.

Main automation loop:

```text
Idea -> Plan -> Create -> Post -> Log -> Analyze -> Update rules -> Repeat
```

Separate screenshot review loop:

```text
Post during week -> Collect analytics screenshots -> Paste starter prompt in review chat -> Upload screenshots -> Update video logs -> Write weekly analysis -> Promote confirmed patterns -> Automations read refreshed memory
```

## Folder Structure

```text
copy-ready/
docs/
memory/
  analysis/
  patterns/
  templates/
  videos/
  ideas.md
  rules.md
prompts/
```

## What To Paste

Start here if you are unsure what to copy into chat:

- `docs/prompt-usage-guide.md`

Short version:
- paste `copy-ready/08-weekly-screenshot-review.txt` into the weekly screenshot review chat
- use `copy-ready/` if you want plain paste-only versions of the manual prompts
- treat the other files in `prompts/` as automation definitions unless you are intentionally simulating a step

## How To Use

1. Generate 2-3 ideas using your prompt stack.
2. Pick the best one and create a new file in `memory/videos/` from `memory/templates/video-log-template.md`.
3. Use the caption and hashtag prompt to generate the post package before publishing.
4. Fill in the pre-post section before creating the video.
5. Post the video and keep the file ready for metrics.
6. If you have direct metrics during the week, update the relevant `memory/videos/*.md` file.
7. At the end of the week, use the separate screenshot review chat with `copy-ready/08-weekly-screenshot-review.txt`.
8. Use that chat to update the matching `memory/videos/*.md` files and create a weekly review from `memory/templates/weekly-review-template.md`.
9. Promote only repeated signals into:
   - `memory/patterns/winning-hooks.md`
   - `memory/patterns/winning-formats.md`
   - `memory/patterns/failed-patterns.md`
   - `memory/patterns/caption-hashtag-patterns.md`
   - `memory/rules.md`

## Main Automation Flow

```text
idea generation -> video planner -> caption/hashtag research -> post
```

## Video ID Convention

Use:

```text
rc-YYYY-MM-DD-01
```

Examples:
- `rc-2026-04-29-01`
- `rc-2026-04-29-02`

Use the same ID:
- in the video log filename
- inside the `Video ID` field
- when mapping screenshots

## Separate Review Flow

```text
screenshots -> review chat -> video log updates -> weekly analysis -> pattern promotion -> refreshed memory
```

## Weekly Screenshot Review Workflow

1. Gather screenshots for each posted video.
2. Make sure each screenshot set can be matched to a video ID or video filename.
3. Start a review chat and paste `copy-ready/08-weekly-screenshot-review.txt`.
4. Upload the screenshots for that week.
5. Let the chat:
   - extract metrics and visible qualitative signals
   - update the relevant `memory/videos/*.md` files
   - write one weekly analysis file in `memory/analysis/`
   - recommend pattern promotions only when evidence repeats

The screenshot review chat is intentionally separate from the automation chain.
It acts as the memory-refresh layer that the automations use afterward.

## Screenshot Rules

- Use the same analytics views each week if possible.
- Always identify which video each screenshot belongs to.
- If a metric is unclear in the screenshot, leave it blank rather than guessing.
- Treat screenshot-based conclusions as evidence-backed only when multiple videos point the same way.

## Operating Principle

- `rules.md` is the current source of truth for what the system should optimize for.
- `patterns/` stores observed wins and losses.
- `videos/` stores raw evidence.
- `analysis/` stores conclusions.
- Captions and hashtags should be treated as testable packaging variables, not filler text.

Do not update rules from one video.
Update rules only after repeated signals across multiple posts.
