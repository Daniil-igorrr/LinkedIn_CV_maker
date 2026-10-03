# .agent/rules/correspondence.md

## Purpose

Allows the agent to communicate with recruiters (drafting replies, booking calls) without the risk of "lying" about past events because the agent's conversational memory does not persist between sessions. The only source of truth about correspondence is the log file, not the agent's memory.

## Communication Log

For each company with which correspondence is ongoing, maintain a file
`output/{Company}_CommunicationLog.md`. If it does not exist, create it upon the first message from that company.

Record format (append to the end, NEVER overwrite the entire file):

```markdown
## 2026-09-29 14:32 — Incoming message from {sender name}
{exact text of the incoming message}

## 2026-09-29 14:35 — Draft reply (sent by user)
{text of the proposed draft}

## 2026-09-29 15:00 — Calendar event created
Date/time: {date, time, timezone}
Event link: {calendar event link, if available}
```

## Mandatory Procedure for a New Message

1. **Always** first read `output/{Company}_CommunicationLog.md` in full (if the file exists) — **BEFORE** answering any question about the correspondence history with that company, even if it seems that it was already discussed in the same session.
2. Read `output/{Company}_{Role}_CV.md` and `CoverLetter.md` — the response must not contradict what has already been written and sent to this company (do not suddenly claim different experience or different figures).
3. Draft the reply according to the same rules as the resume:
   traceability to `master-profile.md`, no unverifiable claims
   (see `anti-hallucination.md` — this applies here too, not only to CV/CL).
4. If booking a call is being discussed — see the "Calendar" section below.
5. **Always** append a new record to the communication log —
   both the incoming message and the proposed reply, with the current date/time. This is not optional — without this step the system will not work in the next session.

## If Asked About History That Is Not in the File

If the user asks something about correspondence with a company, but it is not present in `{Company}_CommunicationLog.md`, explicitly answer "I have no record of this in the log" instead of assuming or reconstructing it from context. This is the same "No Guesswork" rule as `anti-hallucination.md` section 1.3, applied to correspondence history rather than profile facts.

## Calendar

The agent may create events in Google Calendar directly (through a script using the Calendar API, with the same OAuth credentials already configured for n8n — copy `token.json`/`credentials.json` into the agent's working folder).

Before creating an event, the agent must show the user the exact date/time/timezone and wait for confirmation "yes, book it"; do not create the event silently. The event description must include: the job posting link, company website, and company LinkedIn (if available in the communication_log or JD).

## Consolidated Tracker

In addition to the log for each company, the agent maintains one shared file
`output/applications_tracker.md` — a Markdown table:

```markdown
| Company | Role | Status | Date Applied | Last Contact | Next Action |
|---|---|---|---|---|---|
| Talnir | BDR | Skipped (commission-only) | - | - | - |
| Bigle | SDR | Applied | 2026-09-29 | 2026-09-29 | Wait for response |
```

Update the row on every event: new CV/CL generation → new row with status "Applied"; new communication_log entry → update Last Contact and Status (Applied → Interviewing → Offer/Rejected/Ghosted).

If `Last Contact` is older than 7 days and Status is not "Rejected"/"Offer", the agent should mention it in the response: "By the way, there has been no response from {Company} for N days; it may be worth sending a follow-up." Do this unobtrusively, once per session, not on every request.

## Secrets Hygiene

The agent must never print the full contents of `token.json`/`credentials.json` in chat or in any file under `output/` — even for debugging. If it is necessary to confirm that a token is valid, it is sufficient to say "credentials found, file is readable" without outputting the contents. This protects secrets from accidentally ending up in screenshots/logs that may later be forwarded elsewhere.

## What the Agent Does NOT Do

As before — the agent does not send messages on LinkedIn/email itself and does not click buttons on websites. It only prepares a reply draft and, if confirmed, creates a calendar event. Sending the text on LinkedIn is still done manually by the user.
