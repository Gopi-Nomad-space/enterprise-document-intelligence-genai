from src.ingestion.document_loader import load_documents_from_dir
from src.preprocessing.chunking import chunk_documents

def test_chunking():
    print("Starting document loading...")
    
    docs = load_documents_from_dir("data/raw_docs")
    print(f"Number of documents loaded: {len(docs)}")

    if not docs:
        print("❌ No documents found. Check data/raw_docs folder.")
        return

    print("Starting chunking...")
    chunked_docs = chunk_documents(docs)

    for doc, chunks in chunked_docs.items():
        print(f"\nDocument: {doc}")
        print(f"Number of chunks: {len(chunks)}")
        print("Sample chunk:\n", chunks[0][:300])

if __name__ == "__main__":
    test_chunking()