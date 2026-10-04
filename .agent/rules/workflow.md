# Workflow — Step-by-Step Task Execution

This document defines the mandatory workflow for a new job description and the deterministic batch protocol.

## Step 0 — Batch Mode

If the user asks to process everything in `inbox/`, the agent MUST use the deterministic controller.

Start:
```bash
python scripts/batch_controller.py prepare
```

The controller:
- selects at most 5 `.txt` files alphabetically;
- freezes the selected filenames and source hashes in `.batch/manifest.json`;
- freezes SHA-256 hashes of all mandatory rule files;
- marks exactly one file as `in_progress`;
- does not include later files added to `inbox/`.

Before each job, obtain the current filename:
```bash
python scripts/batch_controller.py current
```

### Job isolation
Process **ONLY** the filename returned by `current`.

### Full-batch execution
If the user asks to process/continue the batch, do NOT stop after one successful job. After `complete` returns `Next:`, immediately run `current` again and process the next job. Continue this loop until the controller prints `Batch complete.` or a controller/infrastructure error occurs. The user must not need to send another "continue" message between jobs.

Do NOT:
- create scripts, helper programs, replacement tooling, or ad-hoc generators;
- install packages or modify project dependencies while processing a job;
- inspect or process other pending files;
- choose another file;
- manage batch state manually;
- move, rename, copy, delete, or recreate files in `inbox/` or `inbox/processed/`;
- use `Move-Item`, `mv`, `cp`, `rm`, `Remove-Item`, `del`, `unlink`, or equivalent filesystem operations on batch input/processed files;
- use wildcard filesystem operations;
- write to `output/execution_log.md`.

The agent may create the current job's outputs and one temporary execution record under `.batch/records/`. It may update `output/applications_tracker.md` when required by `.agent/rules/correspondence.md`.

The official PDF pipeline is scripts/generate_pdfs.py. Run it for every PROCEED job after creating the Markdown CV and Cover Letter. It writes A4 PDFs beside the Markdown sources and verifies the actual page count with pypdf. Dependencies are declared in requirements.txt and must be installed outside job processing. If the generator or its dependencies are missing, STOP; do not create a replacement, install packages, or invent another PDF pipeline.

After the current job is finished:
```bash
python scripts/batch_controller.py complete "<CURRENT_JOB>" ".batch/records/<record>.record.md"
```

If `complete` returns **any error**, **STOP immediately**. Do not attempt to repair the filesystem, remove an existing destination, move the source manually, rerun with another filename, or otherwise bypass the controller. Report the exact error and wait for recovery instructions.

The controller verifies the source hash, appends the record to `output/execution_log.md`, moves **exactly that file** to `inbox/processed/`, and advances the next pending job.

If rule hashes changed, the controller stops the batch.

A consolidated report may be presented only after the controller reports `Batch complete.`

## Step 1: Ingestion & Job Analysis
1. Read the complete current job description.
2. Extract Company Name, Target Role / Title, Core Requirements & Responsibilities, Preferred Tech Stack / Tools, and Key Industry Keywords.

## Step 2: Cross-Referencing with `master-profile.md`
1. Read `master-profile.md`.
2. Compare each extracted requirement against verified profile facts.
3. Identify direct matches, strictly grounded transferable matches, and gaps.

## Step 3: Resume Generation
1. Load `templates/resume-template.md`.
2. Populate it strictly from verified facts.
3. Keep the CV within 1 standard A4 page.
4. Run the anti-hallucination checklist before saving.

## Step 4: Cover Letter Generation
1. Load `templates/cover-letter-template.md`.
2. Draft 150–200 words using only verified facts.
3. Run the anti-hallucination checklist before saving.

## Step 5: Saving Output Files
Save:
- `output/{Company}_{Role}_CV.md`
- `output/{Company}_{Role}_CoverLetter.md`

For a SKIP decision, do not generate CV/CL.

## Step 6: Execution Record
For every job, create one temporary record:
```text
.batch/records/<current-job-safe-name>.record.md
```
The record must follow `.agent/rules/execution-log.md`.

Never create or overwrite `output/execution_log.md` directly.

## Step 7: Presenting Response & Gap Report
Provide links to generated outputs and the Gap Report. For skipped jobs, provide the exact documented reason.

## Step 8: Application Boundaries
The agent only prepares tailored documents and analysis. It NEVER sends emails, submits applications, or contacts recruiters automatically.
