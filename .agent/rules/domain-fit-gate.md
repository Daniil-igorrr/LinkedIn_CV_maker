# .agent/rules/domain-fit-gate.md

## Purpose

Executed BEFORE workflow.md, for every new job posting — to avoid wasting time generating CV/CL for jobs that are filtered out at the basic domain/industry/compensation level rather than at the skill level.

## Step 0 — Preliminary Check

1. In the Qualifications/Requirements section, divide statements into:
   - **Hard requirements** — "required", "essential", "must have", or listed without softening language.
   - **Soft/nice-to-have** — "plus", "nice to have", "preferred", "a bonus", "is a plus but not required".

2. Within the hard requirements, identify those that concern specialized industries rather than general sales/B2B/tech skills (for example: life sciences, biotech, pharma, CRO, legal, healthcare compliance, regulated finance, etc.).

3. Separately, BEFORE the other checks, always scan the JD for three specific types of hard requirements, even if the job is otherwise purely IT/sales:

   - **Language requirement** — "Must be fluent in [language]", "native [language] speaker required", etc., where the language is not included in `master-profile.md` (English, Spanish, Russian).

   - **Country-specific work authorization** — "Applicants must be authorized to work in [country]", where the country does not match what is stated in `master-profile.md`. IMPORTANT: The user's authorization is ONLY Spain (national Spanish Residencia Temporal + Aut. Trabajar, not EU-wide). Treat only an explicit "Spain" in the requirement as a match. Any other EU country (Germany, Netherlands, France, etc.) must by default be treated as a mismatch, EVEN if the country is in the EU, unless the JD explicitly states that the role is fully location-agnostic (hiring as a contractor/through an EOR without requiring physical presence/residency specifically in that country). If the JD says "Location: [country]" or "must be based in [country]", this is an explicit indication of a real presence requirement, not merely a mention of a company office.

   - **Commission-only compensation** — The JD states that compensation is structured WITHOUT a fixed base salary. Trigger phrases (any one of them starts the check below): "commission-only", "100% commission", "straight commission", "commission-based" (role/structure/position), "uncapped commission", "no base salary", "draw against commission only", "1099 commission-only".

     IMPORTANT: "commission-based" is THE SAME trigger as "commission-only". The presence or absence of the word "only" does not matter — both phrases by default mean there is no fixed base. Do not downgrade "commission-based" to an "ambiguous case" merely because the word "only" is absent.

     - Check: if at least one trigger phrase appears AND nowhere in the JD (Role Description, Compensation, "Why this role", etc.) is a fixed base mentioned ("base salary", "base pay", "fixed salary", "base + commission", "base + OTE") — this is SKIP.
     - If a trigger phrase exists, but a base is explicitly mentioned elsewhere in the JD (for example, "base $40k + uncapped commission") — this is NOT SKIP; the target compensation format is confirmed.
     - The ambiguous case that is NOT SKIP and goes into the Gap Report is when compensation is NOT described AT ALL in the JD: there is no word "commission" and no word "salary"/"base"/"pay". Only then: "Compensation structure not disclosed in JD — verify base salary exists before applying."

   A mismatch with any one of these three points against the profile/requirements = immediate **SKIP**, regardless of how well everything else matches. Do not proceed to steps 4–5 below if this point is triggered — it has priority.

   Important: The LinkedIn "match well" label is NOT a substitute for this check — it mainly matches by job/skill keywords and often misses exactly these absolute requirements (including compensation structure). Always check the JD text, even if LinkedIn showed a green light.

4. Classify each such requirement:
   - **Learnable skill** — tool, CRM, methodology, IT terminology, technical product (even a complex one). Example: "Familiarity with Salesforce", "understanding of API integrations", "test automation concepts". → Does NOT block; it can be addressed through interview preparation.
   - **Network/relationship requirement** — "established network within X", "existing relationships with Y decision-makers". → Stop factor; this cannot be acquired in a reasonable amount of time.
   - **Specialized non-IT domain expertise, mandatory** — "1–2 years experience in a CRO/life sciences/legal/regulated finance..." specifically as a requirement, not a plus. → Stop factor if `master-profile.md` contains nothing similar.

5. If at least one hard requirement falls into the "network" or "specialized non-IT domain" category and there is no match in `master-profile.md` — the job status is **SKIP**.
   - Do NOT generate CV/CL.
   - Output a short explanation with the exact quote from the JD that caused the rejection.

6. If all hard requirements are learnable skills (regardless of complexity) or general soft skills, and none of the three points in step 3 triggered — status: **PROCEED**, continue to workflow.md as normal.

## Example (for agent calibration)

Job: Inside Sales Specialist, Seuss+ (life sciences/CRO consulting).
- "1–2 years of experience within a CRO, life sciences service organization..." — required, specialized non-IT domain.
- "An established network within Clinical Operations is essential" — required, network.
→ Result: SKIP. Neither reason can be closed through interview preparation.

Counterexample (for comparison — NOT a reason for SKIP): job requires "understanding of QA/test automation concepts" or "exposure to DevTools" — this is IT context, learnable, even if unfamiliar at the start.

Job: "SDR — OTE $60k (base $40k + uncapped commission)".
→ NOT SKIP on compensation — there is an explicit fixed base.

Job: "100% commission role. Unlimited earning potential, no cap on what you can make. This is a 1099 commission-only position."
→ SKIP. "100% commission" and "commission-only" are explicitly stated, with no base.

Job: mentions only "competitive commission structure and bonuses" without the word "base" and without the word "only".
→ Not an automatic SKIP. Add to the Gap Report as requiring clarification:
"Fixed base is not explicitly stated — clarify before applying."

Job: "This is a part-time, commission-based role... Commission-based structure with uncapped earning potential, plus milestone bonuses." Base is not mentioned anywhere in the JD.
→ SKIP. "Commission-based" is the same trigger as "commission-only" when there is no fixed base mentioned nearby. This is NOT the same case as the example above: that example only lacks an explicit formulation despite using the general word "commission" ("competitive commission structure" without the trigger word "-based"/"-only"/"uncapped"), whereas here the trigger clearly fires.

## Important

This is not a filter based on the overall difficulty of the job. SKIP only when the gap physically cannot be closed within a reasonable time before the interview (foreign industry + required network), or when the compensation format directly contradicts the user's requirement (no fixed base), not when preparation and understanding of the topic are simply required or when compensation data is absent from the JD.
