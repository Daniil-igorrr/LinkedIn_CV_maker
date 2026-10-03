# .agent/rules/execution-log.md

## Purpose

A machine-readable log of every processing step — separate from the human-readable Batch Report. It is needed so that a separate controller agent can verify whether the rules were actually applied rather than simply trusting the final summary.

## When to Write

After processing EVERY job posting (both in batch mode and when processing a single job) — append a record to `output/execution_log.md` (Markdown, append-only, never overwrite the entire file).

## Record Format

```markdown
## {timestamp} — {Company} — {Role}
- Source file: inbox/processed/{filename}
- Domain-fit-gate verdict: SKIP | PROCEED
  - Reasoning: {exact reason with JD quote if SKIP; "no blockers found" if PROCEED}
- Anti-hallucination self-check (Section 5 checklist):
  - Line Check: PASS / FAIL / NOT CHECKED
  - Metrics Check: PASS / FAIL / NOT CHECKED
  - Tools Check: PASS / FAIL / NOT CHECKED
  - Role Title Check: PASS / FAIL / NOT CHECKED
  - Missing Skills Check: PASS / FAIL / NOT CHECKED
  - Domain Expertise Check: PASS / FAIL / NOT CHECKED
- PDF page count (from actual pdfinfo/pypdf output, not an assumption):
  CV = {N}, Cover Letter = {N}
- Output files: {paths or "none (skipped)"}
- Gap Report items: {list or "none"}
```


## Append-Only Write Method

Records must be added **ONLY** through a shell append command (`Add-Content` / `>>`), NEVER through Create/Write File — those tools overwrite the entire file.
If it is unclear which tool will be used, first run `cat output/execution_log.md` to verify that the existing records have not been lost.

## Rule

A record is mandatory for EVERY job posting without exception, including SKIP (record the verdict + reasoning; all other fields should be "N/A (skipped)").

If any checklist item was not actually checked — write "NOT CHECKED", do not guess "PASS". A false "PASS" without a real check is worse than an honest "NOT CHECKED" — this is exactly what the controller is supposed to catch.
