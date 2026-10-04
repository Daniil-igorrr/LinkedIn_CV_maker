# Workflow — Step-by-Step Task Execution

This document defines the mandatory workflow for a new job description and the deterministic batch protocol.

## Step 0 — Batch Mode

If the user asks to process everything in inbox/, the agent MUST use the deterministic controller.

Initial bootstrap:
- The first prepare invocation may use the system Python solely to bootstrap the project .venv if needed:
  `python scripts/batch_controller.py prepare`
- After prepare succeeds, ALL project Python commands on Windows/Antigravity MUST use:
  `.venv\Scripts\python.exe`
- Never use the global Python interpreter for project execution after prepare.
- Never install packages during job processing.

The controller:
- selects at most 5 .txt files;
- freezes the selected filenames and source hashes in .batch/manifest.json;
- freezes SHA-256 hashes of all mandatory rule files;
- marks exactly one file as in_progress;
- does not include later files added to inbox/.

Before each job, obtain the current filename:
`.venv\Scripts\python.exe scripts/batch_controller.py current`

### Job isolation
Process ONLY the filename returned by current.

### Full-batch execution
If the user asks to process/continue the batch, do NOT stop after one successful job. After complete returns Next:, immediately run current again and process the next job. Continue until the controller prints Batch complete. or a controller/infrastructure error occurs. The user must not need to send another continue message between jobs.

Do NOT:
- create scripts, helper programs, replacement tooling, or ad-hoc generators;
- install packages or modify project dependencies while processing a job;
- inspect or process other pending files;
- choose another file;
- manage batch state manually;
- move, rename, copy, delete, or recreate files in inbox/ or inbox/processed/;
- use Move-Item, mv, cp, rm, Remove-Item, del, unlink, or equivalent filesystem operations on batch input/processed files;
- use wildcard filesystem operations;
- write to output/execution_log.md.

The agent may create the current job outputs and one temporary execution record under .batch/records/. It may update output/applications_tracker.md when required by .agent/rules/correspondence.md.

The official PDF pipeline is scripts/generate_pdfs.py. On Windows/Antigravity, run it ONLY with .venv\Scripts\python.exe scripts/generate_pdfs.py. Run the PDF pipeline for every PROCEED or PROCEED_WITH_GAPS job after creating the Markdown CV and Cover Letter. If the generator or its dependencies are missing, STOP; do not create a replacement, install packages, or invent another PDF pipeline.

After the current job is finished:
`.venv\Scripts\python.exe scripts/batch_controller.py complete "<CURRENT_JOB>" ".batch/records/<record>.record.md"`

If complete returns ANY error, STOP immediately. Do not repair the filesystem or bypass the controller.

The controller verifies the source hash, appends the record to output/execution_log.md, moves exactly that file to inbox/processed/, and advances the next pending job.

If rule hashes changed, the controller stops the batch.

A consolidated report may be presented only after the controller reports Batch complete.

## Step 0.5 — Mandatory Domain-Fit Gate

For EVERY current job, before drafting any CV/CL:

1. Read the complete JD.
2. Read master-profile.md.
3. Execute ALL rules in .agent/rules/domain-fit-gate.md.
4. Produce the mandatory requirement matrix:
   - requirement
   - HARD/PREFERRED
   - exact profile evidence
   - MATCH/MISMATCH
5. If ANY HARD requirement is MISMATCH or UNVERIFIED:
   - status = SKIP;
   - stop processing this job immediately;
   - do NOT generate CV, Cover Letter, PDF, tracker entry, or application record;
   - report the exact JD quote and the missing/insufficient profile evidence.
6. Only PROCEED or PROCEED_WITH_GAPS jobs may enter the document-generation steps.

There is NO exception for:
- strong overall fit;
- high keyword similarity;
- urgency;
- the candidate being able to learn the missing requirement;
- a gap report;
- LinkedIn's own match label.

A hard requirement is a gate, not a suggestion.

## Step 1 — Ingestion & Job Analysis

1. Read the complete current job description.
2. Extract Company Name, Target Role / Title, Core Requirements & Responsibilities, Preferred Tech Stack / Tools, and Key Industry Keywords.

## Step 2 — Cross-Referencing with master-profile.md

1. Read master-profile.md.
2. Compare each extracted requirement against verified profile facts.
3. Identify direct matches, strictly grounded transferable matches, and gaps.
4. Do not infer facts not explicitly supported by master-profile.md.

## Step 3 — Resume Generation

Only for PROCEED / PROCEED_WITH_GAPS jobs:
1. Load templates/resume-template.md.
2. Populate it strictly from verified facts.
3. Keep the CV within 1 standard A4 page.
4. Run the anti-hallucination checklist before saving.

## Step 4 — Cover Letter Generation

Only for PROCEED / PROCEED_WITH_GAPS jobs:
1. Load templates/cover-letter-template.md.
2. Draft 150–200 words using only verified facts.
3. Run the anti-hallucination checklist before saving.

## Step 5 — Saving Output Files

Save:
- output/{Company}_{Role}_CV.md
- output/{Company}_{Role}_CoverLetter.md

For a SKIP decision, do not generate CV/CL.

## Step 6 — Execution Record

For every processed job, create one temporary record:
.batch/records/<current-job-safe-name>.record.md

The record must follow .agent/rules/execution-log.md.

Never create or overwrite output/execution_log.md directly.

A SKIP record may exist ONLY if the workflow explicitly requires recording the decision; it must never be used to justify document generation or application tracking.

## Step 7 — Presenting Response & Gap Report

Provide links to generated outputs and the Gap Report for PROCEED jobs. For skipped jobs, provide the exact documented reason and no application-document links.

## Step 8 — Application Boundaries

The agent only prepares tailored documents and analysis. It NEVER sends emails, submits applications, or contacts recruiters automatically.

## Step 9 — Tailored Quality Pass

For every PROCEED / PROCEED_WITH_GAPS job, before creating the execution record:
1. Re-read the current JD and compare it against the drafted CV/CL.
2. Identify the 3–5 strongest job requirements.
3. Verify that the CV Summary and top experience bullets visibly prioritize the strongest factual matches.
4. Verify the Cover Letter names the target company/role and contains 2–3 concrete, job-relevant proof points from master-profile.md.
5. Remove generic filler and unsupported enthusiasm.
6. Confirm the header retains the Markdown LinkedIn link from the templates.
7. Run the official PDF generator and require its LinkedIn hyperlink verification to pass.

Use previous successful documents such as AMOX only as a style/quality reference (structure, specificity, evidence density). Never copy their claims, dates, authorization wording, or other facts unless independently supported by master-profile.md.
