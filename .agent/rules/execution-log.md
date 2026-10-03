# .agent/rules/execution-log.md

## Purpose
A machine-readable append-only log of every processed job. The final chat report is not evidence of execution.

## Ownership
`output/execution_log.md` is owned by `scripts/batch_controller.py`.

The AI agent MUST NOT create, overwrite, truncate, or append to `output/execution_log.md` directly. Do not use `Create`, `Write File`, `Set-Content`, `Out-File`, `Add-Content`, `>>`, or any equivalent operation against the main log.

The agent creates only a temporary record for the current job under `.batch/records/`. The controller appends that record and moves the exact source file when `complete` is called.

## Record Format
The temporary record must contain:

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

For a SKIP job, all non-applicable checks are `N/A (skipped)`, as defined by the record format. If a check was not actually performed, write `NOT CHECKED`; never guess `PASS`.

## Required completion sequence
1. Finish the current job.
2. Write exactly one temporary record under `.batch/records/`.
3. Run:
```bash
python scripts/batch_controller.py complete "<CURRENT_JOB>" ".batch/records/<record>.record.md"
```

The controller:
- verifies the rule hashes;
- verifies the source file has not changed;
- appends the record using an actual append operation;
- moves exactly the current source file;
- advances the next pending file or closes the batch.

There is no wildcard move operation in the supported workflow.
