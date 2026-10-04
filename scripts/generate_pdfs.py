#!/usr/bin/env python3
"""Render project Markdown CVs and cover letters to verified one-page A4 PDFs."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
except ImportError as exc:
    print("ERROR: PDF dependencies are missing. Install requirements.txt outside job processing.", file=sys.stderr)
    raise SystemExit(2) from exc

MARGIN = 0.5 * inch

def markup(text: str) -> str:
    links = []
    def stash(match):
        token = f"@@LINK{len(links)}@@"
        links.append((token, match.group(1), match.group(2)))
        return token
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash, text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for token, label, url in links:
        safe_url = url.replace("&", "&amp;").replace('"', "&quot;")
        safe_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace(token, f'<link href="{safe_url}" color="blue">{safe_label}</link>')
    return text

def flowables(text: str):
    base = getSampleStyleSheet()
    name = ParagraphStyle("Name", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=20, alignment=TA_CENTER, spaceAfter=3)
    contact = ParagraphStyle("Contact", parent=base["Normal"], fontSize=9, leading=10.5, alignment=TA_CENTER, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=12.5, spaceBefore=4, spaceAfter=2)
    h3 = ParagraphStyle("H3", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=11, spaceBefore=2, spaceAfter=1)
    body = ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=10, leading=11.5, spaceAfter=1.5)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=10, firstLineIndent=-7)
    out = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            out.append(Spacer(1, 2))
        elif line == "---":
            out.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=3))
        elif line.startswith("# "):
            out.append(Paragraph(markup(line[2:]), name))
        elif line.startswith("## "):
            out.append(Paragraph(markup(line[3:]), h2))
        elif line.startswith("### "):
            out.append(Paragraph(markup(line[4:]), h3))
        elif line.startswith("- "):
            out.append(Paragraph("• " + markup(line[2:]), bullet))
        else:
            out.append(Paragraph(markup(line), contact if len(out) < 2 else body))
    return out

def render(source: Path) -> int:
    if not source.is_file():
        raise FileNotFoundError(source)
    target = source.with_suffix(".pdf")
    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN, title=source.stem, author="LinkedIn CV Maker")
    doc.build(flowables(source.read_text(encoding="utf-8")))
    reader = PdfReader(str(target))
    pages = len(reader.pages)
    links = []
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            obj = annotation.get_object()
            action = obj.get("/A")
            if action and action.get("/URI"):
                links.append(str(action.get("/URI")))
    if not any("linkedin.com/in/daniil-kotelevets-1a470a296" in link for link in links):
        raise RuntimeError(f"{target.name} is missing the clickable LinkedIn profile link.")
    print(f"{target}: {pages} page(s); LinkedIn hyperlink verified")
    if pages != 1:
        raise RuntimeError(f"{target.name} is {pages} page(s); exactly 1 A4 page is required.")
    return pages

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cv", type=Path, required=True)
    parser.add_argument("--cover-letter", type=Path, required=True)
    args = parser.parse_args()
    try:
        render(args.cv)
        render(args.cover_letter)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("Programmatically verified: CV = 1 page, Cover Letter = 1 page.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
