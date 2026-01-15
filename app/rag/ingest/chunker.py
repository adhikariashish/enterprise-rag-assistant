from __future__ import annotations
from typing import Any, Dict, List, Optional

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Chunk the input text into smaller pieces.
    Split text into overlapping character chunks.

    Args:
        text: The input text to be chunked.
        chunk_size: The maximum size of each chunk.
        overlap: The number of overlapping characters between chunks.

    Returns:
        A list of text chunks.
    """
    text = (text or "").strip()
    if not text:
        return []
    
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")
    
    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_length:
            break

        start = end - overlap
        
    return chunks