import fitz  # PyMuPDF
from pathlib import Path

def load_pdf(file_path: str) -> str:
    """
    Extracts clean text from a PDF file.
    """
    doc = fitz.open(file_path)
    text = []

    for page in doc:
        text.append(page.get_text())

    doc.close()
    return "\n".join(text)


def load_documents_from_dir(directory: str):
    """
    Loads all PDFs from a directory.
    """
    docs = {}
    for file in Path(directory).glob("*.pdf"):
        docs[file.name] = load_pdf(str(file))
    return docs