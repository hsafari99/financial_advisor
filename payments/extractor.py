import os
import tempfile
from pathlib import Path

import pdfplumber


def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def pdf_to_images(pdf_path: str) -> list[str]:
    from pdf2image import convert_from_path

    tmp_dir = tempfile.mkdtemp()
    pages = convert_from_path(pdf_path)
    stem = Path(pdf_path).stem
    paths = []
    for i, page in enumerate(pages):
        out = os.path.join(tmp_dir, f"{stem}_page{i + 1}.png")
        page.save(out, "PNG")
        paths.append(out)
    return paths
