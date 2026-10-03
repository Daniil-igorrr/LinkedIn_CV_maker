# .agent/rules/pdf-page-limit.md

## Hard Limit

The final resume PDF (`{company}_{role}_CV.pdf`) MUST be exactly 1 A4 page. The cover letter must also be exactly 1 page.

## How to Check (Mandatory, Programmatically — Not "By Eye")

After generating the PDF, the agent MUST perform an actual page-count check, for example:

```bash
pdfinfo output/{filename}.pdf | grep Pages
```

or using a library (pypdf/PyPDF2/pdfplumber in Python):

```python
from pypdf import PdfReader

print(len(PdfReader("output/{filename}.pdf").pages))
```

A visual "by eye" assessment is prohibited — the agent must explicitly run a command/code and read the actual page count from the output before reporting the result.

## If More Than 1 Page — Order of Actions (Exactly This Order)

1. **First, check formatting, not content.** Open the template/style generation settings (margins, font size, line height, spacing between sections).

   In 90% of cases, overflow is caused by excessive margins or spacing rather than a genuine excess of text. Adjust margins/line-height to compact but professionally readable values (for example, margins ~0.5–0.6", font size no lower than 10pt) and regenerate.

2. If it is still more than 1 page after step 1 — shorten wording (**not facts!**) in the bullets: remove repeated words, make sentences shorter, but do not remove facts or change numbers.

3. If it still does not fit — remove the least relevant bullet from Experience for THIS job as the last resort (the one with the least overlap with the JD's keywords), but no more than one bullet.

4. Font size below 10pt and margins below 0.4" are prohibited, even if that would solve the problem. Readability is more important than fitting everything onto 1 page.

## Maximum 3 Iterations

Maximum 3 iterations of check → edit → regenerate. If it is still more than 1 page after 3 attempts, stop the process and tell me exactly what does not fit instead of silently cutting more facts.

## Report

After a successful check, the agent MUST explicitly write in the response: "Programmatically verified: N page(s)." — using the actual number from the command output, not an assumption.
