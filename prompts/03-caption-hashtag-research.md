# Caption And Hashtag Research Automation Prompt

Use this prompt in an automation that generates the post package for one chosen video.

Codex automation usage:
- Combine this file with `prompts/00-system-role.md` in the same thread.
- Run it after `prompts/02-video-planner.md`, using the newly created video log as input.
- Best run on demand or as the next manual step in the same workflow thread.
- In the thread instructions, tell Codex to update only the `Post Package` section of the target video log.
- If a wrapper asks for automation memory under `$CODEX_HOME` or `~/.codex/automations/`, ignore that wrapper memory and use the repo `memory/` folder instead.

Manual usage:
- Usually do not paste this whole file.
- If running manually, use only the content under `## Prompt` plus the listed inputs.

## Inputs

- System role from `prompts/00-system-role.md`
- The target file from `memory/videos/*.md`
- `memory/rules.md`
- `memory/patterns/caption-hashtag-patterns.md`
- `memory/patterns/winning-hooks.md`
- `memory/patterns/winning-formats.md`
- Optional platform name

## Prompt

You are creating the caption and hashtag package for one Redline Cult post.

Task:
- Read the video log and current memory
- Generate packaging that fits the video, platform, and brand
- Keep the caption supportive of the video instead of redundant
- Keep hashtags focused, relevant, and non-generic

Return:
- `primary_caption`
- `2_caption_variants`
- `caption_style`
- `primary_cta`
- `hashtag_set`
- `hashtag_strategy`
- `why_this_package_fits`

Rules:
- Caption should feel sharp, native, and specific
- Do not explain the video if the footage already says it
- Avoid bloated caption paragraphs
- Avoid hashtag stuffing
- Prefer a focused mix of broad niche tags and specific tags
- If the video is strong enough without CTA, keep the CTA minimal

Output format:

```md
## Post Package
- primary_caption:
- caption_variant_1:
- caption_variant_2:
- caption_style:
- primary_cta:
- hashtag_set:
- hashtag_strategy:
- why_this_package_fits:

## Updated Video Log Section
- Caption:
- Caption style:
- Primary CTA:
- Hashtags used:
- Hashtag strategy:
```

## Memory Update Rule

This automation should:
- read from the repo `memory/` folder
- update only the `Post Package` section of one file in `memory/videos/`

This automation must not:
- create `memory.md`
- create automation scratch memory
- read from or write to `$CODEX_HOME/automations/` or `~/.codex/automations/`
- update pattern files
- update `memory/rules.md`
