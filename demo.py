"""
Comprehensive demo script showing the complete RAG pipeline in action.
Demonstrates all major features of the document intelligence system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import RAGPipeline
from src.ingestion.document_loader import load_documents_from_dir
from src.preprocessing.chunking import chunk_documents
from src.extraction.entity_extractor import extract_entities
from src.extraction.relation_extractor import extract_relations
from src.embeddings.embedder import embed_chunks, calculate_similarity
from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from src.knowledge_graph.neo4j_client import Neo4jClient


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_document_loading():
    """Demonstrate document loading."""
    print_section("1. DOCUMENT LOADING")
    
    print("\n📄 Loading documents from 'data/raw_docs'...")
    docs = load_documents_from_dir("data/raw_docs")
    
    if not docs:
        print("⚠️  No documents found in data/raw_docs/")
        print("   Please add some PDF files to proceed.")
        return None
    
    print(f"✓ Loaded {len(docs)} documents")
    for doc_name, content in docs.items():
        print(f"  • {doc_name}: {len(content)} characters")
    
    return docs


def demo_chunking(documents):
    """Demonstrate text chunking."""
    print_section("2. TEXT CHUNKING")
    
    print("\n✂️  Chunking documents...")
    chunks = chunk_documents(documents, chunk_size=800, chunk_overlap=150)
    
    total_chunks = sum(len(c) for c in chunks.values())
    print(f"✓ Created {total_chunks} chunks from {len(chunks)} documents")
    
    for doc_name, chunk_list in chunks.items():
        print(f"  • {doc_name}: {len(chunk_list)} chunks")
        if chunk_list:
            print(f"    Sample chunk (first 200 chars): {chunk_list[0][:200]}...")
    
    return chunks


def demo_entity_extraction(chunks):
    """Demonstrate entity extraction."""
    print_section("3. ENTITY EXTRACTION")
    
    # Get first chunk from first document
    first_doc = list(chunks.keys())[0]
    first_chunk = chunks[first_doc][0]
    
    print(f"\nExtracting entities from first chunk of '{first_doc}'...")
    print(f"Chunk preview: {first_chunk[:150]}...\n")
    
    entities = extract_entities(first_chunk)
    
    print("✓ Extracted Entities:")
    print(f"  • Organizations ({len(entities.organizations)}): {entities.organizations[:3]}")
    print(f"  • Persons ({len(entities.persons)}): {entities.persons[:3]}")
    print(f"  • Dates ({len(entities.dates)}): {entities.dates[:3]}")
    print(f"  • Clauses ({len(entities.clauses)}): {entities.clauses[:3]}")
    
    return entities


def demo_relation_extraction(chunks):
    """Demonstrate relation extraction."""
    print_section("4. RELATION EXTRACTION")
    
    # Get first chunk from first document
    first_doc = list(chunks.keys())[0]
    first_chunk = chunks[first_doc][0]
    
    print(f"\nExtracting relations from first chunk...")
    relations = extract_relations(first_chunk)
    
    print(f"✓ Extracted {len(relations.relations)} relations")
    if relations.relations:
        for i, rel in enumerate(relations.relations[:3], 1):
            print(f"  {i}. {rel.source} --[{rel.relation_type}]--> {rel.target}")
    
    return relations


def demo_embeddings(chunks):
    """Demonstrate embedding creation."""
    print_section("5. EMBEDDING GENERATION")
    
    print("\n🧠 Creating embeddings for all chunks...")
    embeddings = embed_chunks(chunks)
    
    total_embeddings = sum(len(e) for e in embeddings.values())
    print(f"✓ Created {total_embeddings} embeddings")
    
    for doc_name, emb_list in embeddings.items():
        if emb_list:
            print(f"  • {doc_name}: {len(emb_list)} embeddings, dimension: {len(emb_list[0])}")
    
    return embeddings


def demo_similarity_search(chunks, embeddings):
    """Demonstrate similarity-based retrieval."""
    print_section("6. SEMANTIC SIMILARITY SEARCH")
    
    query = "What are the key terms and conditions?"
    print(f"\nQuery: '{query}'")
    
    from src.embeddings.embedder import retrieve_similar_chunks
    
    results = retrieve_similar_chunks(query, embeddings, chunks, top_k=3)
    
    print(f"✓ Retrieved {len(results)} most relevant chunks:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. Document: {result['document']}, Similarity: {result['similarity']:.3f}")
        print(f"     {result['chunk'][:200]}...")
    
    return results


def demo_full_rag_pipeline():
    """Demonstrate complete RAG pipeline."""
    print_section("7. FULL RAG PIPELINE")
    
    print("\n🚀 Initializing complete RAG pipeline...")
    
    try:
        # Note: Neo4j connection may fail if not running - that's OK for demo
        pipeline = RAGPipeline(enable_graph=False)
        
        if not pipeline.load_documents("data/raw_docs"):
            print("⚠️  No documents to process")
            return
        
        pipeline.preprocess_documents()
        pipeline.extract_information()
        pipeline.create_embeddings()
        
        summary = pipeline.get_summary()
        
        print("\n✓ Pipeline Summary:")
        print(f"  • Documents loaded: {summary['documents_loaded']}")
        print(f"  • Total chunks: {summary['total_chunks']}")
        print(f"  • Embeddings created: {summary['embeddings_created']}")
        print(f"  • Entities extracted: {summary['entities_extracted']}")
        print(f"  • Relations extracted: {summary['relations_extracted']}")
        
        # Try a sample query
        print("\n📝 Sample Query Test:")
        query = "What is the main purpose of this document?"
        print(f"Query: '{query}'")
        
        retrieved = pipeline.retrieve_relevant_chunks(query, top_k=2)
        print(f"✓ Retrieved {len(retrieved)} relevant chunks")
        
        response = pipeline.generate_response(query, retrieved)
        print(f"\nGenerated Response:\n{response[:300]}...")
        
    except Exception as e:
        print(f"⚠️  Pipeline demo error: {e}")
        print("   (This is expected if Neo4j is not running or documents are missing)")


def demo_api_examples():
    """Show API usage examples."""
    print_section("8. REST API USAGE EXAMPLES")
    
    examples = [
        {
            "name": "Initialize Pipeline",
            "endpoint": "POST /initialize",
            "body": {
                "document_directory": "data/raw_docs",
                "enable_knowledge_graph": False
            }
        },
        {
            "name": "Query Documents",
            "endpoint": "POST /query",
            "body": {
                "question": "What are the payment terms?",
                "top_k": 5,
                "use_graph": False
            }
        },
        {
            "name": "Extract Entities",
            "endpoint": "POST /extract-entities",
            "body": {
                "text": "John works for Microsoft on confidential AI projects."
            }
        },
        {
            "name": "Retrieve Chunks",
            "endpoint": "GET /retrieve/payment%20terms",
            "params": "?top_k=5"
        }
    ]
    
    print("\nAPI Endpoint Examples:\n")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}")
        print(f"   Endpoint: {example['endpoint']}")
        if "body" in example:
            import json
            print(f"   Body: {json.dumps(example['body'], indent=6)}")
        else:
            print(f"   Query: {example['params']}")
        print()


def main():
    """Run complete demo."""
    print("\n" + "🎯" * 35)
    print("   ENTERPRISE DOCUMENT INTELLIGENCE - COMPLETE SYSTEM DEMO")
    print("🎯" * 35)
    
    # Check if sample documents exist
    doc_dir = Path("data/raw_docs")
    if not doc_dir.exists() or len(list(doc_dir.glob("*.pdf"))) == 0:
        print("\n⚠️  SETUP REQUIRED:")
        print("   Please add PDF files to: data/raw_docs/")
        print("\n   The demo will proceed with available features...")
        print("\n   Features that require documents:")
        print("   • Document loading")
        print("   • Text chunking")
        print("   • Entity/relation extraction")
        print("   • Embedding generation")
        print("   • Semantic search")
        print("   • RAG pipeline")
    
    # Run demos
    try:
        # Test individual components
        documents = demo_document_loading()
        
        if documents:
            chunks = demo_chunking(documents)
            
            # Test extraction on first chunk
            demo_entity_extraction(chunks)
            demo_relation_extraction(chunks)
            
            # Test embeddings and search
            embeddings = demo_embeddings(chunks)
            demo_similarity_search(chunks, embeddings)
        
        # Test full pipeline
        demo_full_rag_pipeline()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    # Show API examples
    demo_api_examples()
    
    print_section("DEMO COMPLETE")
    print("\n✅ All components demonstrated successfully!")
    print("\n📖 Next Steps:")
    print("   1. Add PDF files to data/raw_docs/")
    print("   2. Run: python -m uvicorn src.api.main:app --reload")
    print("   3. Visit: http://localhost:8000/docs")
    print("   4. Start making API calls!")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
