from src.ingestion.document_loader import load_documents_from_dir

def test_load_documents():
    docs = load_documents_from_dir("data/raw_docs")
    
    assert isinstance(docs, dict)
    assert len(docs) > 0
    
    print("Loaded documents:")
    for doc_name in docs.keys():
        print(doc_name)

if __name__ == "__main__":
    test_load_documents()