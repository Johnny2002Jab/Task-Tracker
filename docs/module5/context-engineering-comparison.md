# Context Engineering Comparison

Same task ("produce a one-page architecture document for the Task Tracker") run three times with
three different context strategies. See `architecture-A.md`, `architecture-B.md`,
`architecture-C.md` for the full outputs; `docs/architecture.md` is the combined final version.

| Question | Answer |
|---|---|
| Which strategy produced the most accurate file-level description? | **C (targeted).** Every claim traces to an actual line in `main.py`/`models.py`/`storage.py` — exact enum values, exact validator limits, exact CORS origin list. |
| Which strategy invented the most or sounded generic? | **A (minimal).** It assumed a database/ORM exists ("assumed a lightweight persistence layer... since that's the more common shape"), which is simply wrong for this repo — the clearest real error across all three. |
| Which strategy was most honest about what it had not inspected? | **C**, explicitly and repeatedly ("not visible from the files I read") — including correctly declining to describe the frontend, tests, or CI, none of which were part of its read set. B was honest about missing precision (exact limits) but still described the frontend/tests/CI at a system level, since `AGENTS.md` covered them. |
| Which output would help a new teammate fastest? | **B**, for a first orientation — it's complete enough to know where everything lives without needing to open every file first. C is better once that teammate is about to actually change one of the three files it covers. |
| Which context strategy would you use for security work, onboarding docs, or feature planning? | Security work and anything correctness-sensitive: **C** — an audit built on "not visible from what I read" is honest about its own blind spots, which matters when the cost of a wrong guess is a missed vulnerability. Onboarding docs: **B** — completeness beats precision when the goal is "get oriented fast." Feature planning: closer to **C's discipline but at B's breadth** — see `docs/decisions/comments-feature-plan.md`, where reading the actual files (not summaries) caught a wrong assumption (a database that doesn't exist) that a structured-context pass might not have caught unless the summaries happened to mention storage explicitly. |

## Verdict and rule

Kept for the final `docs/architecture.md`: C's precision as the backbone, B's system-level framing
(frontend/tests/CI existence, not their exact contents) to fill C's acknowledged gaps.

**Rule:** for task shape "correctness matters more than completeness" (security, business-rule
docs, anything trusted without independent re-verification), use targeted context (C) — an honest
gap beats a confident guess. For task shape "orientation matters more than precision"
(onboarding, first-pass architecture sketches), structured context (B) gets there faster with
acceptable precision loss.
