from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Dict, List

def chunk_documents(
    documents: Dict[str, str],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> Dict[str, List[str]]:
    """
    Splits documents into overlapping text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )

    chunked_docs = {}

    for doc_name, text in documents.items():
        chunks = splitter.split_text(text)
        chunked_docs[doc_name] = chunks

    return chunked_docs