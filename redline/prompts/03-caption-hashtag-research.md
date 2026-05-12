# Caption And Hashtag Research Automation Prompt

Use this prompt in an automation that generates the post package for one chosen video.

You are creating the caption and hashtag package for one Redline Cult post.

Task:
- Generate packaging that fits the video plan, platform, and brand
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
```
