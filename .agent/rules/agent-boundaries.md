# Agent Boundaries — No Self-Modification / No Tooling Improvisation

## Purpose

This rule prevents the job-processing agent from changing the project's execution machinery while processing a job.

## Hard prohibitions

During job processing, the agent MUST NOT:

- create a new script, helper program, generator, converter, or automation to replace a missing tool;
- edit, patch, or rewrite `scripts/`, `.agent/`, `AGENTS.md`, templates, project configuration, or dependency files;
- install or upgrade Python, Node, system, or other packages;
- create ad-hoc PDF generators or conversion pipelines;
- change the workflow because a required tool is unavailable;
- create new tracking/logging systems that are not explicitly required by the locked rules.

## Missing-tool rule

If a required existing tool or documented project mechanism is missing, unavailable, or fails:

1. STOP the current job.
2. Do NOT create a replacement.
3. Do NOT install a dependency.
4. Do NOT call `batch_controller.py complete`.
5. Report the exact missing tool/error and wait for user recovery instructions.

## Allowed work

The agent may:

- read the current job and locked project rules;
- read `master-profile.md` and the documented templates;
- create/update the current job's CV and Cover Letter outputs;
- create the single temporary execution record under `.batch/records/`;
- update `output/applications_tracker.md` when required by `.agent/rules/correspondence.md`;
- use existing documented tools for PDF generation and page-count verification;
- call `batch_controller.py current` and `complete` according to the workflow.

The agent never owns the infrastructure. If the workflow itself needs to change, stop the batch and change the repository outside job processing.
