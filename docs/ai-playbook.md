<!--
NOTICE: This playbook was drafted by Claude Code from real evidence across this project's
session history (mid-course through the Final Project — see docs/module5/governance-worksheet.md
and docs/final-ai-review.md). Module 5 is explicit that a playbook filled in by the AI isn't
really a playbook — the rules below are evidence-backed, not generic, but they still need to be
read, argued with, and rewritten in your own words before they're actually yours. Revised once
more at Final Project completion (see the last bullet under "What I am still figuring out"), but
still a draft for you to personalize, not a finished artifact.
-->

# Personal AI Playbook

## When I reach for AI first

- Scaffolding a new feature end-to-end when the shape is well understood (due dates/tags: model
  fields, storage filters, tests, frontend wiring) — AI is fast at the repetitive parts once the
  design decisions are made.
- Debugging from hard evidence: a real pytest failure, a real CI run's exit code and annotations,
  a real curl response. The CI `ModuleNotFoundError` diagnosis only worked because it was chased
  through actual reproduction (a clean venv, the exact CI invocation) instead of guessing from the
  YAML.
- A second, skeptical read of my own diffs before committing — e.g. the Dockerfile/CI review that
  caught "Docker was never actually build/run-verified" as the one finding that mattered.

## When I do not reach for AI first

- Deciding what a business rule *should* be (e.g. whether same-status is a valid transition) — AI
  can implement a rule once it's decided, but the same-status PATCH bug happened specifically
  because a rule got quietly relaxed instead of the actual conflicting requirement (frontend
  always sending status vs. the documented transition table) being resolved.
- Anything touching a live credential. Retrieving the GitHub token to trigger a CI re-run was a
  deliberate, single, immediately-`unset` action — not something to let happen routinely or
  automate away.
- Writing the trade-offs/open-questions sections of a decision note in a voice that's supposed to
  be mine — AI can draft the structure, but the actual judgment calls need to be argued with, not
  accepted.

## My non-negotiables

- Never share long-lived credentials, `.env` contents, or real personal/customer data with an AI
  tool — retrieve credentials programmatically and immediately before use if a tool genuinely
  needs one, never paste them into a prompt.
- Never accept a CI/Docker/security claim as "done" without independent evidence (a real run, a
  real curl, a real `docker exec`) — "the YAML looks right" is not verification.
- Never let an AI-authored fix for a bug replace understanding *why* the bug happened — the
  same-status PATCH issue came back a second time specifically because the first fix wasn't
  understood well enough to stick.

## My review rules

- For anything CI/CD: push it, read the actual run result, and if it fails, get the real error
  text (logs if available, or a temporary diagnostic step if not) before proposing a fix — don't
  guess from the exit code alone.
- For security or code review comments: grade every finding Valid/Useful, False Positive/Wrong, or
  Noise with a one-sentence reason, and treat "sounds like a real concern" and "is a real concern"
  as different things until checked against the actual code (the reflected-error-message finding
  in this project's security review is the concrete example: plausible, checked, rejected).
- For anything I can't run in the current environment (no Docker daemon, no `gh` CLI/token), say
  so explicitly in the deliverable rather than describing it as tested.

## What I am still figuring out

- Where the line is between "reasonable automated recovery" (a diagnostic CI step that surfaces
  a real error) and "quietly working around a problem instead of fixing it" — the two can look
  similar from the outside.
- How much of a security/governance review genuinely needs a second, independent reviewer versus
  a single careful reviewer doing two structured passes — this project's security review used the
  same agent for both, which isn't the same thing.
- Whether "record AI contributions in the commit/doc" (rule 3 in `docs/ai-usage.md`) is enough on
  its own to prevent a corrected mistake from quietly reverting, or whether that needs a test that
  actively guards the corrected behavior too.
- The Docker build has now gone undocumented-as-unverified across three separate checkpoints
  (Module 4, Module 5, Final Project) without ever actually being resolved — each time it was
  honestly flagged rather than glossed over, which is the right short-term call, but three
  checkpoints is long enough that "flag it honestly" has become a substitute for "get access to
  Docker and actually check." That's worth noticing about my own pattern, not just the project's.

## Decision Card

- **New feature:** start with a plan (what fields, what routes, what tests) before any code, then
  implement backend → tests → frontend in that order, verifying each layer before moving on.
- **Code review:** use AI for a first broad pass, but personally verify every "Valid"/"Useful"
  finding against the actual file before acting on it, and record the "Wrong"/"False Positive"
  ones too — that's where the judgment shows up, not in the list length.
- **Debugging:** always start from the exact command run and the exact output/error, never a
  paraphrase — the CI `ModuleNotFoundError` was only findable because the actual annotation text
  was retrieved, not assumed from the exit code.
- **Infrastructure (CI/Docker):** trust nothing until it's actually run once, green, then broken
  once on purpose, then fixed again — a workflow that has never failed hasn't proven it can catch
  anything.
- **Never paste:** credentials, tokens, `.env` contents, real personal or customer data.
- **My one rule:** verify with a real run, a real command, or a real file — not with how
  confident the explanation sounds.
