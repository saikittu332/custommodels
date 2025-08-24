import os
import glob
import fitz  # PyMuPDF for PDFs
from typing import List

DATA_DIR = "backend/data"

def load_text_from_pdf(path: str) -> str:
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return ""

def load_text_from_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return ""

def load_client_documents(client_id: str) -> str:
    folder = os.path.join(DATA_DIR, client_id)
    texts = []
    for file_path in glob.glob(os.path.join(folder, "*")):
        if file_path.endswith(".pdf"):
            txt = load_text_from_pdf(file_path)
        elif file_path.endswith(".txt"):
            txt = load_text_from_txt(file_path)
        else:
            txt = ""
        if txt.strip():
            texts.append(txt)
    return "\n\n".join(texts)

def split_text_to_chunks(text: str, chunk_size: int=500, chunk_overlap: int=50) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks
