# Redline Cult Cloud Build Spec

## Purpose

This document defines the target cloud version of the Redline Cult system so another AI or developer can build it without guessing the product shape.

The current repo is a prompt-driven content workflow with Markdown memory files. The cloud version should preserve that workflow while moving state, execution, and review history into hosted services.

## Primary Goal

Build a hosted personal AI content operating system for Redline Cult that:

- runs without local hosting
- keeps the current workflow structure
- uses NVIDIA as the current LLM provider
- stores memory and history in MongoDB instead of only Markdown files
- exposes a Streamlit dashboard for manual use and review
- can be triggered by page visits or scheduled jobs later
- sends notifications through Telegram

## Product Position

This is a solo-use internal tool, not a public SaaS product.

It should optimize for:

- low cost
- simple deployment
- low maintenance
- easy provider switching later
- preserving human oversight for analytics review and memory promotion

It should not optimize yet for:

- multi-user auth
- public signup
- real-time bot infrastructure
- enterprise security/compliance
- large-scale analytics

## Existing Workflow To Preserve

Current core loop:

```text
Idea -> Plan -> Create -> Post -> Log -> Analyze -> Update rules -> Repeat
```

Current review loop:

```text
Post during week -> Collect analytics screenshots -> Review -> Update video logs -> Write weekly analysis -> Promote patterns -> Refresh memory
```

Cloud build must preserve those two loops.

## Proposed Architecture

```text
Streamlit Cloud
  - dashboard UI
  - manual trigger pages
  - protected job trigger page

MongoDB Atlas
  - system memory
  - video logs
  - weekly analyses
  - prompts
  - job runs
  - config

NVIDIA LLM API
  - idea generation
  - planning
  - caption/hashtag generation
  - analysis drafting
  - pattern extraction

Telegram Bot
  - notifications
  - run summaries
  - error alerts

Optional later:
GitHub Actions
  - reliable scheduling
  - backup execution path
```

## Non-Goals

- No always-on background worker is required in v1.
- No vector database is required in v1.
- No separate frontend/backend split is required in v1.
- No public API is required in v1.
- No automatic screenshot OCR pipeline is required unless clearly requested later.

## Core Product Requirements

### Functional Requirements

The system must:

- store the current Markdown-based memory as MongoDB records
- preserve the existing prompt roles as callable automation steps
- let the user manually run each workflow step from a dashboard
- let the user trigger a bundled daily or weekly job from a protected page
- store all outputs, runs, and errors
- maintain per-video records
- maintain weekly analysis records
- maintain long-term pattern memory
- maintain rules memory
- support Telegram notifications for success and failure
- allow future replacement of NVIDIA with another provider through an adapter layer

### Operational Requirements

The system must:

- be deployable on free or near-free hosting
- run safely if triggered multiple times
- avoid duplicate writes for the same scheduled window
- keep secrets out of the UI
- support partial failure logging
- be understandable to a non-expert operator

## Users

### Primary User

One solo creator/operator managing Redline Cult content strategy.

### User Capabilities Needed

The user must be able to:

- generate new ideas
- turn an idea into a structured video plan
- generate captions and hashtags
- log post results
- upload or summarize weekly metrics
- review historical performance
- inspect rules and pattern memory
- manually trigger jobs
- see what the AI did and what it changed

## Build Philosophy

The cloud system should not replace the thinking structure of the repo. It should operationalize it.

That means:

- prompts become system templates stored in code and optionally mirrored in MongoDB
- Markdown memory becomes structured MongoDB documents with optional Markdown fields
- manual review remains part of the system
- rule updates require evidence, not single-run automation

## Application Modules

The implementation should be split into clear modules.

```text
app.py
pages/
core/
providers/
jobs/
db/
models/
utils/
prompts/
```

### Suggested Structure

```text
app.py                      # Streamlit entrypoint
pages/
  01_dashboard.py
  02_ideas.py
  03_video_planner.py
  04_caption_packaging.py
  05_results_logger.py
  06_weekly_review.py
  07_patterns_and_rules.py
  08_run_history.py
  09_admin.py
  10_trigger_job.py

core/
  workflow_service.py
  idea_service.py
  planner_service.py
  packaging_service.py
  results_service.py
  analysis_service.py
  promotion_service.py
  prompt_renderer.py

providers/
  llm/
    base.py
    nvidia_provider.py
  mongo/
    client.py
  telegram/
    client.py

jobs/
  run_daily_pipeline.py
  run_weekly_pipeline.py
  run_manual_step.py

db/
  repositories/
    ideas_repo.py
    videos_repo.py
    analyses_repo.py
    patterns_repo.py
    rules_repo.py
    runs_repo.py
    config_repo.py

models/
  idea.py
  video.py
  weekly_analysis.py
  pattern_memory.py
  rules_memory.py
  run_log.py

utils/
  time.py
  ids.py
  locks.py
  markdown.py
  hashing.py
```

## Core Workflows

### 1. Idea Generation

Input:

- current rules
- winning patterns
- failed patterns
- recent ideas
- optional user theme or content direction

Process:

- assemble prompt context from stored memory
- send to LLM
- parse structured response
- save ideas

Output:

- 2 to 5 candidate content ideas
- rationale for each
- optional confidence or novelty label

### 2. Video Planner

Input:

- selected idea
- current rules
- relevant patterns

Process:

- build plan prompt
- generate structured video plan
- create new video record

Output:

- video concept
- hook
- beat-by-beat structure
- filming notes
- CTA
- draft log entry

### 3. Caption and Hashtag Packaging

Input:

- selected video
- video plan
- caption/hashtag pattern memory
- current rules

Process:

- generate packaging options
- save best or all variants

Output:

- caption candidates
- hashtag suggestions
- packaging notes

### 4. Results Logger

Input:

- chosen video
- manually entered metrics or imported review data

Process:

- update video document
- append metric snapshots

Output:

- updated video log
- updated status fields

### 5. Weekly Review

Input:

- videos in selected date range
- manually entered weekly evidence
- optional screenshot notes

Process:

- summarize performance
- identify repeated winners and losers
- draft weekly analysis

Output:

- weekly analysis document
- promotion recommendations
- risks or unknowns

### 6. Pattern Promotion

Input:

- one or more weekly analyses
- repeated evidence from multiple video logs

Process:

- extract repeated winning hooks
- extract repeated formats
- extract failed patterns
- update rules only if evidence threshold is met

Output:

- updated pattern memory
- updated rules memory
- audit trail of what changed and why

## Important Decision Rule

Never allow one video to directly rewrite long-term rules.

Promotion path must remain:

```text
video evidence -> weekly analysis -> pattern promotion -> rules update
```

## Data Model

MongoDB should store both structured fields and original Markdown when useful.

### Collections

- `ideas`
- `videos`
- `weekly_analyses`
- `patterns`
- `rules`
- `prompt_templates`
- `job_runs`
- `system_config`
- `artifacts`

### 1. ideas

```json
{
  "_id": "uuid",
  "idea_id": "idea-2026-05-12-01",
  "title": "string",
  "summary": "string",
  "angle": "string",
  "rationale": "string",
  "status": "new|selected|rejected|archived",
  "source_run_id": "uuid",
  "created_at": "ISODate",
  "tags": ["hook", "bike", "humor"]
}
```

### 2. videos

This is the most important collection.

```json
{
  "_id": "uuid",
  "video_id": "rc-2026-04-29-01",
  "title": "string",
  "idea_id": "idea-2026-05-12-01",
  "status": "planned|drafted|posted|reviewed",
  "platform": "instagram|tiktok|youtube_shorts",
  "plan": {
    "hook": "string",
    "concept": "string",
    "beats": ["string"],
    "cta": "string",
    "production_notes": ["string"]
  },
  "post_package": {
    "caption_options": ["string"],
    "selected_caption": "string",
    "hashtags": ["string"],
    "packaging_notes": "string"
  },
  "metrics": {
    "views": 0,
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "saves": 0,
    "watch_time": null,
    "completion_rate": null
  },
  "metric_snapshots": [
    {
      "captured_at": "ISODate",
      "source": "manual|review",
      "metrics": {
        "views": 0,
        "likes": 0
      }
    }
  ],
  "review_notes": ["string"],
  "llm_notes_markdown": "string",
  "source_run_id": "uuid",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### 3. weekly_analyses

```json
{
  "_id": "uuid",
  "analysis_id": "weekly-2026-05-12",
  "week_start": "2026-05-04",
  "week_end": "2026-05-10",
  "video_ids": ["rc-2026-04-29-01"],
  "summary_markdown": "string",
  "wins": ["string"],
  "losses": ["string"],
  "open_questions": ["string"],
  "promotion_candidates": {
    "winning_hooks": ["string"],
    "winning_formats": ["string"],
    "failed_patterns": ["string"],
    "caption_patterns": ["string"]
  },
  "source_run_id": "uuid",
  "created_at": "ISODate"
}
```

### 4. patterns

This can be one collection with typed records rather than many files.

```json
{
  "_id": "uuid",
  "pattern_type": "winning_hook|winning_format|failed_pattern|caption_pattern",
  "title": "string",
  "statement": "string",
  "evidence_video_ids": ["rc-2026-04-29-01", "rc-2026-05-01-02"],
  "evidence_analysis_ids": ["weekly-2026-05-12"],
  "confidence": "low|medium|high",
  "status": "candidate|confirmed|archived",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### 5. rules

Use either one active document or versioned documents. Versioned is better.

```json
{
  "_id": "uuid",
  "ruleset_id": "rules-2026-05-12-v3",
  "version": 3,
  "status": "active|archived",
  "rules_markdown": "string",
  "change_summary": ["string"],
  "evidence_analysis_ids": ["weekly-2026-05-12"],
  "created_at": "ISODate"
}
```

### 6. job_runs

This is required for reliability.

```json
{
  "_id": "uuid",
  "run_id": "uuid",
  "job_name": "daily_pipeline",
  "trigger_type": "manual|page_trigger|scheduled",
  "scheduled_for": "2026-05-12T08:00:00Z",
  "status": "started|completed|failed|skipped",
  "steps": [
    {
      "name": "idea_generation",
      "status": "completed",
      "started_at": "ISODate",
      "finished_at": "ISODate",
      "summary": "Created 3 ideas"
    }
  ],
  "error_message": null,
  "created_at": "ISODate",
  "finished_at": "ISODate"
}
```

## Markdown Compatibility

The existing repo relies heavily on Markdown. The cloud build should preserve Markdown where it helps human readability.

Recommended rule:

- store structured fields for application logic
- store Markdown fields for human-readable summaries and editable notes

Good uses of Markdown in MongoDB:

- weekly analysis summaries
- rules text
- long-form review notes
- prompt snapshots
- operator notes

## Prompt Management

The current prompt files should become code-managed templates.

### Prompt Sources

- repo prompt files remain the canonical editable source during build
- app may mirror active prompt templates into MongoDB for runtime inspection

### Prompt IDs To Preserve

- `system_role`
- `idea_generator`
- `video_planner`
- `caption_hashtag_research`
- `results_logger`
- `weekly_analyzer`
- `pattern_promoter`
- `reality_check`
- `screenshot_review_chat`

### Prompt Template Document

```json
{
  "_id": "uuid",
  "prompt_key": "idea_generator",
  "version": 1,
  "source_type": "repo",
  "content_markdown": "string",
  "active": true,
  "created_at": "ISODate"
}
```

## Streamlit Pages

### Dashboard

Show:

- latest runs
- pending ideas
- recent videos
- active ruleset summary
- latest weekly analysis
- quick actions

### Ideas Page

Allow:

- generate new ideas
- browse past ideas
- mark one as selected

### Video Planner Page

Allow:

- choose an idea
- run planner
- inspect generated plan
- create or update video record

### Caption Packaging Page

Allow:

- choose a video
- generate caption and hashtag options
- select final packaging

### Results Logger Page

Allow:

- choose a posted video
- enter metrics manually
- append metric snapshots

### Weekly Review Page

Allow:

- choose date range
- select videos
- add review notes
- run weekly analysis

### Patterns and Rules Page

Allow:

- inspect pattern memory
- view evidence
- run pattern promotion
- inspect current ruleset
- compare ruleset versions

### Run History Page

Allow:

- inspect past job runs
- view step-level logs
- inspect errors

### Admin Page

Allow:

- manage provider settings
- manage Telegram target
- inspect secrets presence
- inspect prompt versions

### Protected Trigger Page

Purpose:

- receives a secret token
- executes a specific job when opened
- returns success/failure summary

This page exists for the keep-alive bot or remote trigger use case.

## Triggering Strategy

### Supported Trigger Types

- manual dashboard run
- protected page trigger
- optional GitHub Actions later

### Protected Trigger Requirements

- require query token or header token
- validate against secret
- accept `job=daily` or `job=weekly`
- write a `job_runs` record immediately
- acquire a lock before starting work
- skip if job window already completed

Example:

```text
/trigger?token=SECRET&job=daily
```

## Idempotency and Locking

This is mandatory.

If the same page or scheduler triggers the job more than once, the system must not duplicate work.

### Required Logic

- compute a logical job window such as `daily_pipeline + 2026-05-12`
- attempt atomic insert or upsert for a run lock
- if lock exists and run is completed, skip
- if lock exists and run is active, skip or show already running
- if prior run failed, allow retry with explicit override

### Suggested Unique Key

`job_name + scheduled_for`

## LLM Provider Abstraction

NVIDIA is the current provider, but the system must be provider-agnostic.

### Interface

```python
class LLMProvider:
    def generate(self, prompt: str, system_prompt: str | None = None) -> dict:
        ...
```

### Requirements

- one provider interface
- one NVIDIA implementation
- normalized response object
- provider-specific request/response mapping isolated to provider file

Normalized response should include:

- raw text
- parsed data if available
- model name
- token metadata if available
- provider name

## Telegram Integration

Telegram should be used for concise notifications.

### Notification Types

- job completed
- job failed
- weekly analysis ready
- rules updated

### Message Content

Keep messages short.

Example:

```text
Redline Cult daily job completed.
Ideas: 3
New plans: 1
Run ID: 1234
```

## Config and Secrets

Use Streamlit secrets or environment variables.

Required secrets:

- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `NVIDIA_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TRIGGER_TOKEN`

Optional secrets:

- `DEFAULT_LLM_MODEL`
- `APP_TIMEZONE`

## Error Handling

Each workflow step should fail independently with structured logs.

### Requirements

- if one step fails, record the failure in `job_runs`
- send Telegram failure summary
- preserve partial outputs already written
- show full error on run history page

## Minimal MVP Scope

The first working version only needs:

1. Streamlit dashboard
2. MongoDB connection
3. NVIDIA provider adapter
4. Telegram notifications
5. Idea generation flow
6. Video planner flow
7. Caption packaging flow
8. Results logging form
9. Weekly analysis flow
10. Protected trigger page
11. Run history logging

## Recommended v1 Build Order

### Phase 1

- set up project structure
- create MongoDB client and repositories
- create LLM provider abstraction
- implement NVIDIA provider
- implement Telegram client

### Phase 2

- build core models
- build dashboard shell
- build ideas page
- build planner page
- build caption page

### Phase 3

- build results logger page
- build weekly review page
- build pattern and rules page
- build run history page

### Phase 4

- build protected trigger page
- add locking and idempotency
- add Telegram notifications
- test duplicate trigger handling

## UI Expectations

This is an internal tool, so the UI should be simple and functional.

Requirements:

- clear navigation
- readable tables and summaries
- strong visibility of latest rules
- clear run status and errors
- easy copy/export of captions and ideas

Avoid:

- marketing-style design
- public homepage patterns
- unnecessary animations

## Migration Strategy From Current Repo

The current repo should be treated as source material during migration.

### Map Existing Files To Cloud Records

- `memory/ideas.md` -> `ideas`
- `memory/videos/*.md` -> `videos`
- `memory/patterns/*.md` -> `patterns`
- `memory/rules.md` -> `rules`
- `memory/analysis/*.md` -> `weekly_analyses`
- `prompts/*.md` -> `prompt_templates`

### Migration Recommendation

Do this in two stages:

1. Build app first with empty database and manual entry.
2. Add importer scripts later to convert Markdown files into MongoDB documents.

This avoids blocking the product build on migration tooling.

## Manual Review Policy

Human oversight remains important in two places:

- weekly review interpretation
- rules promotion

The app may suggest promotions, but the user should approve them before rules are changed.

## Future Enhancements

Not required for v1, but design should not block them.

- GitHub Actions scheduling
- Telegram command interface
- screenshot OCR ingestion
- better analytics normalization
- multi-platform post tracking
- A/B packaging experiments
- provider switching
- export back to Markdown

## Acceptance Criteria

The build is successful when:

- user can deploy the app to Streamlit Cloud
- user can connect MongoDB, NVIDIA, and Telegram via secrets
- user can generate ideas and save them
- user can convert an idea into a video plan
- user can generate captions and hashtags for a video
- user can manually log results
- user can generate a weekly analysis from selected videos
- user can inspect patterns and rules
- user can trigger a job from a protected page
- duplicate triggers do not duplicate work
- every run is visible in run history

## Build Prompt For Another AI

Use this if handing implementation to another AI:

```text
Build a Streamlit Cloud app for the Redline Cult content system.

Requirements:
- Python
- Streamlit frontend
- MongoDB Atlas backend
- NVIDIA API as current LLM provider behind an adapter interface
- Telegram notifications
- Protected trigger page for running jobs
- Idempotent job execution with run logging

Preserve these workflow steps:
- idea generation
- video planner
- caption/hashtag packaging
- results logging
- weekly analysis
- pattern promotion

Use MongoDB collections for ideas, videos, weekly_analyses, patterns, rules, prompt_templates, and job_runs.

Store both structured fields and Markdown fields where useful.

Do not implement multi-user auth.
Do not implement public APIs.
Do not hardcode NVIDIA-specific logic into business logic.

Build the app in a modular structure with providers, repositories, services, jobs, and Streamlit pages.

Make the protected trigger page accept a secret token and a job name. Ensure duplicate trigger calls for the same logical window do not duplicate work.

The system is for one internal user and should prioritize clarity, reliability, and low maintenance over scale.
```
