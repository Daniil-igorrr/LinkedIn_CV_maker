# Workflow — Step-by-Step Task Execution

This document outlines the mandatory step-by-step procedure the agent follows whenever a new job description is submitted (either as a file in `inbox/` or pasted directly into chat).

## Step 0 (before Step 1): Batch Mode

If the user asks to process everything in inbox/, switch to batch mode.

Hard limit: process at most 5 files per batch run. If more than 5 files are present in inbox/, process only the first 5 (alphabetically), move them to inbox/processed/, and tell the user how many remain for the next run. Do not exceed this limit even if asked — if the user wants more processed, they run the batch command again.

For EACH file in the batch (not once at the start of the whole batch):

Re-read .agent/rules/domain-fit-gate.md, .agent/rules/anti-hallucination.md, .agent/rules/output-format.md, and .agent/rules/pdf-page-limit.md fresh from disk, even if you already read them for a previous file in this same batch run. Do not rely on what you recall from earlier in this session.
Run the full pipeline (domain-fit-gate → anti-hallucination → workflow Steps 1-5) for this one file.
Append a structured entry to output/execution_log.md per .agent/rules/execution-log.md BEFORE moving to the next file.

After all files in this batch are processed, present ONE consolidated report (same format as before — Skipped / Generated sections), and move the processed files to inbox/processed/.

---

## Step 1: Ingestion & Job Analysis
1. Read the complete job description carefully.
2. Extract and structure the following metadata:
   - **Company Name**
   - **Target Role / Title**
   - **Core Requirements & Responsibilities**
   - **Preferred Tech Stack / Tools**
   - **Key Industry Keywords**

---

## Step 2: Cross-Referencing with `master-profile.md`
1. Read `master-profile.md`.
2. Compare each extracted job requirement against the facts in `master-profile.md`:
   - Identify direct matches (skills, tools, achievements, languages).
   - Identify transferable/adjacent matches strictly rooted in existing facts.
   - Identify unfulfilled requirements (gaps).

---

## Step 3: Resume Generation
1. Load `templates/resume-template.md`.
2. Populate the template strictly following the fixed section order:
   - **Header / Contact Information:** Taken verbatim from `master-profile.md`.
   - **Professional Summary:** 2–3 concise sentences tailored to the role using only verified facts.
   - **Experience:** Prioritize and reorder bullet points from the CLG Project entry to emphasize the most relevant achievements for this role.
   - **Skills:** Group and highlight matching tools and skills from the profile.
   - **Education:** Degree and schedule details from `master-profile.md`.
   - **Availability & Work Authorization:** Verified availability and location preferences.
3. Ensure length fits within 1 standard A4 page.
4. Perform the self-verification checklist from `.agent/rules/anti-hallucination.md`.

---

## Step 4: Cover Letter Generation
1. Load `templates/cover-letter-template.md`.
2. Draft a targeted cover letter:
   - **Length:** Strictly 150–200 words.
   - **Content:** Include 2–3 concrete, verified achievements/metrics from `master-profile.md` that address the employer's key pain points.
   - **Tone:** Confident, direct, factual, and free of fluff.
3. Perform the self-verification checklist from `.agent/rules/anti-hallucination.md`.

---

## Step 5: Saving Output Files
Save the resulting markdown documents into the `output/` directory with clean, standardized filenames:
- `output/{Company}_{Role}_CV.md`
- `output/{Company}_{Role}_CoverLetter.md`

*(Note: Replace spaces and special characters with underscores if needed, e.g., `output/Stripe_SDR_CV.md`)*

---

## Step 6: Presenting Response & Gap Report
In the chat output to the user:
1. Provide clickable links to the newly generated CV and Cover Letter in `output/`.
2. Present a **Gap Report** listing any job requirements or preferred qualifications from the job posting that are **not** covered by `master-profile.md`.
3. If any ambiguous points were encountered, highlight them for user clarification.

---

## Step 7: Application Boundaries
> [!NOTE]
> The agent only prepares tailored documents and analysis. The agent **NEVER** sends emails, submits online applications, or contacts recruiters automatically. All submission decisions and actions are handled exclusively by the user.
