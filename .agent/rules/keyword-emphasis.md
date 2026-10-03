# .agent/rules/keyword-emphasis.md

This rule operates AFTER anti-hallucination.md and never overrides it — it only changes the ordering and emphasis of facts already present in master-profile.md, rather than adding new ones.

## Condition: JD Contains a Mention of AI/no-code/automation Tools

Check the job posting text for mentions (in any section, including "nice to have"):

AI, no-code, automation, vibe-coding, as well as specific tool names (ChatGPT, Make.com, Zapier, Bolt.new, Lovable, Claude Code, Cursor, Antigravity, and similar).

### If a mention is found AND master-profile.md contains a matching fact:

- Move that bullet higher in the experience/skills list (based on relevance).
- In the cover letter, add one specific sentence referring exactly to this fact — not a generic "I'm familiar with AI tools", but specifically what tool was used and for what purpose.

### If a mention is found, BUT master-profile.md has no matching fact:

- Add nothing and do not imply experience that does not exist.
- Record the requirement in the Gap Report as usual (see anti-hallucination.md).

### If the JD contains no mentions of AI/no-code/automation:

- Do not artificially force AI topics. Leave master-profile.md as is, without artificially highlighting AI skills where they were not requested — this looks like keyword stuffing both to the employer and to me when reading the draft.
