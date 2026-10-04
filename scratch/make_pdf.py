import sys
import markdown
from xhtml2pdf import pisa
from pypdf import PdfReader

def convert_md_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    html = markdown.markdown(md_text, extensions=['tables'])
    
    # Simple CSS to style it closely to a resume
    styled_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.2; margin: 0; padding: 0; }}
        h1 {{ font-size: 18pt; margin-bottom: 5px; }}
        h2 {{ font-size: 14pt; border-bottom: 1px solid #000; margin-top: 10px; margin-bottom: 5px; }}
        h3 {{ font-size: 12pt; margin-top: 5px; margin-bottom: 5px; font-weight: bold; }}
        p, li {{ margin: 3px 0; }}
        ul {{ margin-left: 20px; }}
    </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """
    
    with open(pdf_file, 'wb') as f:
        pisa_status = pisa.CreatePDF(styled_html, dest=f)
    
    return not pisa_status.err

def get_page_count(pdf_file):
    reader = PdfReader(pdf_file)
    return len(reader.pages)

cv_md = "output/Knurek_Investigations_Client_Relations_Manager_CV.md"
cv_pdf = "output/Knurek_Investigations_Client_Relations_Manager_CV.pdf"
cl_md = "output/Knurek_Investigations_Client_Relations_Manager_CoverLetter.md"
cl_pdf = "output/Knurek_Investigations_Client_Relations_Manager_CoverLetter.pdf"

# Install markdown if not present
try:
    import markdown
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

convert_md_to_pdf(cv_md, cv_pdf)
convert_md_to_pdf(cl_md, cl_pdf)

cv_pages = get_page_count(cv_pdf)
cl_pages = get_page_count(cl_pdf)

print(f"CV={cv_pages}, Cover Letter={cl_pages}")
