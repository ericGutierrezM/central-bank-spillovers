import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("pip install pymupdf")

def convert(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n\n".join(page.get_text() for page in doc)
    out = Path(pdf_path).with_suffix(".md")
    out.write_text(text, encoding="utf-8")
    print(f"Saved: {out}")

target = Path(sys.argv[1])
if target.is_dir():
    for pdf in target.glob("*.pdf"):
        convert(pdf)
else:
    convert(target)
