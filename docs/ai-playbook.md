# Personal AI Playbook

## When I reach for AI first

- Scaffolding a feature end-to-end once the shape is decided (due dates/tags: model fields,
  storage filters, tests, frontend wiring) — AI is fast at the repetitive parts once the design
  calls are made.
- Debugging from hard evidence: a real pytest failure, a real CI exit code/annotation, a real curl
  response. The CI `ModuleNotFoundError` was only solvable by reproducing it (clean venv, exact CI
  invocation), not by guessing from the YAML.
- A second, skeptical pass over my own diffs before committing — the Dockerfile/CI review that
  caught "Docker was never actually build/run-verified" is the example that mattered.

## When I do not reach for AI first

- Deciding what a business rule should be. The same-status PATCH bug happened because a rule got
  quietly relaxed instead of the real conflict (frontend always sending `status` vs. the documented
  transition table) being resolved.
- Anything touching a live credential — retrieving a GitHub token to trigger a CI re-run was a
  single, deliberate, immediately-`unset` action, not something to automate away.
- Writing the trade-offs section of a decision note in a voice that's supposed to be mine. AI can
  draft structure; the judgment calls need to be argued with, not accepted.

## My non-negotiables

- Never share credentials, `.env` contents, or real personal/customer data with an AI tool —
  retrieve secrets programmatically, immediately before use, never in a prompt.
- Never accept a CI/Docker/security claim as "done" without independent evidence — "the YAML looks
  right" is not verification.
- Never let an AI-authored fix replace understanding *why* a bug happened — the same-status PATCH
  issue came back a second time because the first fix wasn't understood well enough to stick.

## My review rules

- For CI/CD: push it, read the real run result, and if it fails, get the actual error text before
  proposing a fix — never guess from the exit code alone.
- For security/code review: grade every finding Valid/Useful, False Positive/Wrong, or Noise with a
  one-sentence reason — "sounds like a real concern" and "is a real concern" are different until
  checked against the code (the reflected-error-message finding here: plausible, checked, rejected).
- For anything I can't run here (no Docker daemon, no `gh` CLI/token), say so explicitly rather than
  describing it as tested.

## What I am still figuring out

- Where "reasonable automated recovery" (a diagnostic CI step) ends and "quietly working around a
  problem" begins — the two can look identical from the outside.
- Whether a single reviewer doing two structured passes is a real substitute for an independent
  second reviewer — this project's security review used the same agent for both.
- The Docker build went unverified across three checkpoints before it was resolved.

## Decision Card

- **New feature:** plan fields/routes/tests first, then backend → tests → frontend, verifying each
  layer before moving on.
- **Code review:** AI for the first broad pass; personally verify every Valid/Useful finding against
  the file, and record the Wrong/False Positive ones too — that's where the judgment shows.
- **Debugging:** start from the exact command and exact output, never a paraphrase.
- **Infrastructure:** trust nothing until it's run once green, broken once on purpose, and fixed
  again — a workflow that's never failed hasn't proven it can catch anything.
- **Never paste:** credentials, tokens, `.env` contents, real personal or customer data.
- **My one rule:** verify with a real run, a real command, or a real file — not with how confident
  the explanation sounds.
