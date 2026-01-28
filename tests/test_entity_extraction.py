from src.ingestion.document_loader import load_documents_from_dir
from src.preprocessing.chunking import chunk_documents
from src.extraction.entity_extractor import extract_entities

def test_entity_extraction():
    docs = load_documents_from_dir("data/raw_docs")
    chunked_docs = chunk_documents(docs)

    first_doc = list(chunked_docs.keys())[0]
    first_chunk = chunked_docs[first_doc][0]

    entities = extract_entities(first_chunk)

    print("\nExtracted Entities:")
    print(entities)

if __name__ == "__main__":
    test_entity_extraction()