# Anti-Hallucination Rules & Verification Checklist

> [!CRITICAL]
> Factual integrity is absolute. Under no circumstances should you extrapolate, embellish, or fabricate credentials, metrics, titles, tools, or employment history.

---

## 1. Core Principles
1. **Traceability:** Every single statement, metric, tool, or claim in a generated resume or cover letter **must be directly traceable** to a specific line in `master-profile.md`. If a fact cannot be found in `master-profile.md`, it **must not** be written.
2. **Explicit Non-Facts:** Observe all restrictions listed in the `Explicit non-facts` section of `master-profile.md` (no unlisted employment, no unlisted certifications, no hired corporate SDR titles).
3. **No Guesswork / No Assumptions:** If you are unsure whether a fact in `master-profile.md` satisfies a specific job requirement, **ask the user directly** in chat rather than making assumptions or stretching the truth.

---

## 2. Strictly Forbidden (Do NOT Invent)
- ❌ **Metrics & Numbers:** Do not modify numbers or invent new ones (e.g., quota attainment %, revenue generated, team size, pipeline value). Only use metrics explicitly stated in `master-profile.md` (e.g., 500+ prospects, 5–10 qualified leads/week, 3 discovery meetings).
- ❌ **Company Names & Titles:** Do not invent previous employers or convert independent work into formal hired employment.
- ❌ **Dates & Timelines:** Do not alter dates of education or projects.
- ❌ **Tools & Technologies:** Do not add CRM platforms, scraping tools, dialers, or software not explicitly listed in `master-profile.md` (even if standard for SDR roles, e.g., Outreach.io, ZoomInfo, Salesloft, Gong).
- ❌ **Certifications & Diplomas:** Do not list any certifications (e.g., HubSpot Inbound, Salesforce Certified, etc.).
- ❌ **Language Fluency:** Do not add languages or alter proficiency levels beyond what is stated.
- ❌ **Domain Expertise Claims (disguised fabrication):** Do not claim understanding, fluency, literacy, or passion for a domain/technology area (e.g., "AI/cloud infrastructure", "open models", "regulated finance") unless a specific fact in `master-profile.md` directly supports it. Phrases like *"I understand how to position X"*, *"I possess the technical literacy to Y"*, *"passionate about translating Z into business value"* are capability claims, not neutral rephrasing — even when they contain no invented tool, number, or employer, they are still fabrication if nothing in `master-profile.md` backs them.
  - **Red flag test:** if a sentence in the CV/cover letter closely echoes or paraphrases the job posting's own description of the ideal candidate (rather than describing something the candidate actually did), that is a strong signal this rule is being violated. The job posting describes what the employer wants — it is never itself a source of fact about the candidate.

---

## 3. Permitted Actions
- ✔️ **Rephrasing:** You may adapt phrasing to align with the vocabulary and keywords of the target job posting, provided the core meaning and facts remain 100% faithful to `master-profile.md`.
- ✔️ **Reordering / Prioritization:** You may reorder experience bullets, skills, and summary points so that the most relevant points appear first.
- ✔️ **Selective Emphasis:** You may highlight specific aspects of the candidate's experience (e.g., technical scraping vs. email copywriting) depending on the job focus.
- ✔️ **Honest Bridging:** When a job posting asks for domain expertise the candidate doesn't have, you may build an honest bridge from an adjacent, real fact — but it must explicitly acknowledge the gap, not paper over it. Template: *"While my direct experience has been in [actual domain from master-profile.md], I've built hands-on fluency with [actual tool/skill from master-profile.md] through [actual context] — and I'm eager to bring that into [target domain]."* This is permitted because every clause traces to a real fact and the gap is stated honestly, not disguised.

---

## 4. Handling Missing Requirements (Gap Report)
- When a job posting requires a skill, certification, tool, domain expertise, or experience level that the candidate does not have in `master-profile.md`:
  - **DO NOT** add it to the resume or cover letter.
  - **DO NOT** attempt to "soften" or simulate the skill in the CV.
  - **DO NOT** paraphrase the job posting's own requirement back as a claimed personal trait or "understanding" — rewording a gap into a confident-sounding sentence is still fabrication, not a permitted rephrasing (see Section 2, Domain Expertise Claims).
  - **DO** log it in a dedicated **Gap Report** section in the agent's chat response (outside the generated markdown documents).

---

## 5. Mandatory Pre-Output Self-Verification Checklist
Before saving or outputting any CV or Cover Letter, run a line-by-line verification:

- [ ] **Line Check:** Is every single bullet point and statement directly backed by a line in `master-profile.md`? (Yes / No)
  - *Action on 'No':* Remove the sentence or bullet immediately.
- [ ] **Metrics Check:** Are all numbers (500+, 5–10 leads/week, 3 meetings) strictly identical to `master-profile.md`? (Yes / No)
- [ ] **Tools Check:** Are all mentioned tools (Apollo.io, Instantly.ai, Sales Nav, HubSpot, Salesforce, Make.com, Python, ChatGPT, Claude, Antigravity CLI) only from the approved list? (Yes / No)
- [ ] **Role Title Check:** Is the role title accurately represented as "Founder & Lead Generation Specialist — CLG Project"? (Yes / No)
- [ ] **Missing Skills Check:** Are missing job requirements excluded from the CV and documented in the Gap Report? (Yes / No)
- [ ] **Domain Expertise Check:** Does any sentence claim understanding, fluency, or passion for a domain/technology without a specific `master-profile.md` fact backing it — especially any sentence that closely echoes the job posting's own wording back as a personal trait? (Yes / No)
  - *Action on 'Yes':* Rewrite using the Honest Bridging template (Section 3) or remove and move the requirement to the Gap Report.
