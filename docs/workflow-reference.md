# Workflow Reference

Use these prompts as narrow automations instead of one giant workflow.

## Automation Stack

These files are mainly for automation or deliberate manual simulation.
They are not the default paste-into-chat prompts.

1. `01-idea-generator.md`
   Reads memory and proposes new ideas.

2. `02-video-planner.md`
   Converts one selected idea into a real video plan and a new video log draft.

3. `03-caption-hashtag-research.md`
   Builds the post package for a chosen video using memory and platform-aware packaging logic.

4. `04-results-logger.md`
   Updates one video log after posting.

5. `05-weekly-analyzer.md`
   Reviews a batch of video logs and produces a weekly analysis file.

6. `06-pattern-promoter.md`
   Promotes repeated learnings into long-term memory and updates rules.

7. `07-reality-check.md`
   Challenges the current system without editing memory.

## Separate Review Layer

- `08-screenshot-review-chat.md`
  Starter prompt for the weekly screenshot review chat that updates memory from uploaded analytics screenshots.
  This is separate from the automation chain.
  This is the main file you will paste directly into a chat.

## Recommended Cadence

- Daily:
  - Run idea generation
  - Run video planner for chosen ideas
  - Run caption and hashtag research for each chosen post
  - Post
  - Optionally run results logger if you have typed metrics

- Weekly:
  - Run weekly analyzer if structured video logs are already updated
  - Run pattern promoter after analysis
  - Optionally run reality check

## Separate Weekly Screenshot Review

- Gather screenshots for the week
- Start a review chat with `08-screenshot-review-chat.md`
- Update matching `memory/videos/*.md` files
- Create the weekly analysis file
- Feed the refreshed memory back into the automation stack

## Write Permissions

- `01-idea-generator.md`
  Optional write: `memory/ideas.md`

- `02-video-planner.md`
  Write: one new file in `memory/videos/`

- `03-caption-hashtag-research.md`
  Write: update the `Post Package` section of one file in `memory/videos/`

- `04-results-logger.md`
  Write: one existing file in `memory/videos/`

- `05-weekly-analyzer.md`
  Write: one new file in `memory/analysis/`

- `06-pattern-promoter.md`
  Write:
  - `memory/patterns/winning-hooks.md`
  - `memory/patterns/winning-formats.md`
  - `memory/patterns/failed-patterns.md`
  - `memory/patterns/caption-hashtag-patterns.md`
  - `memory/rules.md`

- `07-reality-check.md`
  No writes

- `08-screenshot-review-chat.md`
  Used in a human-assisted review chat
  Expected writes:
  - matching `memory/videos/*.md` files
  - one new `memory/analysis/*.md` file
  - optional promotion recommendations for later review

## Important Constraint

Never let single-video performance directly rewrite long-term rules.
All rule promotion should flow through:

`video logs -> weekly analysis -> pattern promoter -> rules update`

For screenshot-based workflows, use the separate review flow:

`screenshots -> review chat -> video log updates -> weekly analysis -> pattern promoter -> rules update`
