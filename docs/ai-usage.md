# AI Usage Rules

## 1. Never paste

Never share long-lived credentials (OAuth tokens, PATs, API keys, `.env` contents) into a prompt,
even when a tool needs one to act. If a tool needs to authenticate, retrieve the credential
programmatically (e.g. via a credential manager) immediately before use, never print or log it,
and treat any such retrieval as a **High**-risk action worth a second thought before doing it —
not a routine step.

*Why:* the one High-risk moment in this project's governance worksheet was retrieving a live
GitHub token to call the Actions API. It was handled carefully (never printed, `unset`
immediately after), but the right response to noticing that pattern is a rule.

## 2. Always verify

Before treating any AI-authored change as done: run it, don't just read it. For backend logic,
that means running the actual test suite (not just skimming the diff); for CI/CD changes, that
means pushing and checking the real run result, not assuming the YAML "looks right"; for anything
that can't be run in the current environment.

*Why:* this project's CI workflow looked correct and still failed twice for a real reason (bare
`pytest` vs `python -m pytest`) that only showed up by actually pushing and reading the run
result — not by re-reading the YAML more carefully.

## 3. Record AI contributions by

Keeping a short, honest log of what was proposed, what was accepted as-is, what was corrected,
and why — in the same commit or the same `docs/` note as the change itself, not in a separate
document written after the fact from memory.

*Why:* the clearest correction in this project (the same-status PATCH bug) happened *twice*
because the first fix wasn't documented clearly enough at the time to stop it from silently
reverting. A rule that would have prevented the repeat: don't just fix a rejected AI suggestion —
write down *why* it was wrong, next to the fix, so it can't quietly come back.
