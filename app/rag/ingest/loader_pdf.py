from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol

from pypdf import PdfReader

@dataclass
class PDFPage:
    page: int 
    text: str

def load_pdf(path: Path) -> List[PDFPage]:  
    """
    Load a PDF and return list of pages with text.
    """

    reader = PdfReader(str(path))
    pages : List[PDFPage] = []

    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue    
        pages.append(PDFPage(page=i, text=text))
    return pages