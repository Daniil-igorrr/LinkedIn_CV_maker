# PDF Page Limit

## Hard Limit

The final resume PDF (`{company}_{role}_CV.pdf`) MUST be exactly 1 A4 page. The cover letter must also be exactly 1 A4 page.

## Official Generation and Verification

For PROCEED jobs, use only the repository's official PDF generator:

```bash
.venv\\Scripts\\python.exe scripts/generate_pdfs.py \
  --cv "output/{Company}_{Role}_CV.md" \
  --cover-letter "output/{Company}_{Role}_CoverLetter.md"
```

The generator uses the Python dependencies declared in `requirements.txt`, renders A4 PDFs, and verifies the actual page count with `pypdf`.

Do not generate PDFs by eye, with ad-hoc scripts, or through an alternative conversion pipeline.

## If More Than 1 Page

If the generator reports more than 1 page:

1. First check formatting, not content. Adjust the Markdown/content only through the existing project workflow; do not modify the generator.
2. If still more than 1 page, shorten wording (not facts) in bullets.
3. If still more than 1 page, remove the least relevant Experience bullet for this job, but no more than one bullet.
4. Font size below 10pt and margins below 0.4" are prohibited.

Maximum 3 iterations of check → edit → regenerate. If the document is still more than 1 page after 3 attempts, STOP and report exactly which document does not fit.

## Report

After successful generation, the agent MUST explicitly report the actual result printed by the generator, for example:

`Programmatically verified: CV = 1 page, Cover Letter = 1 page.`
