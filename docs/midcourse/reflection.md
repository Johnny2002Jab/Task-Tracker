# Reflection — Mid-Course Project

I used Claude Code as an in-editor assistant across the whole workflow: scoping the two
features, writing the ADR and user stories before touching code, implementing the backend
models/storage/routes and the frontend modal/card/filter changes, generating the pytest
suite, and running Break Tests. I treated it the same way the Module 1-3 prompt libraries
describe — draft, inspect, run, correct — rather than accepting the first answer for anything
that touched a business rule.

The AI helped most in the mechanical, well-specified parts: once the ADR fixed the exact
field types, validation limits, and filter contract, generating the Pydantic model changes,
the storage filter logic, and the 16 pytest tests was fast and largely correct on the first
pass. Having the constraints written down before generation (max 10 tags, 30-char limit,
case-insensitive dedup, `Done` tasks excluded from overdue) meant there was very little back
-and-forth needed on the actual feature code.

Where it slowed things down was a pre-existing bug I didn't expect to find. Before starting
either feature, running the baseline test suite (required by the brief) turned up two failing
tests. One of them was directly caused by a fix I had accepted in an earlier session: making
the backend skip status-transition validation when the status didn't change. That fix
"worked" for the immediate symptom (editing a task without touching status no longer errored)
but it silently violated the documented rule that same-status transitions must be rejected
with 422 — and the pytest suite caught it. If I had trusted the earlier fix and moved straight
into feature work, I would have shipped a change that broke a documented business rule while
looking like a bug fix.

The place my review changed the result most was catching that same issue at the design level,
not just the test level: the correct fix wasn't "adjust the backend rule," it was "stop
sending a value the user didn't change" on the frontend. That's a different fix than what an
AI would default to if you just asked it to make the failing test pass — it would have been
easy to get a green suite by loosening the business rule instead of fixing the actual caller
behavior. The same discipline applied to the two AI assumptions I rejected during design: that
any task with a past due date is overdue regardless of status, and that tags should be a
comma-separated string to minimize the diff. Both were plausible, both would have been wrong
to ship. The habit I'm taking into later modules is to treat a passing test suite as a
starting question ("does this suite even reflect the rules we want?") rather than a finish
line.
