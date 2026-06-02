"""
Getting Started Guide - Quick Reference
"""

QUICK_START = """
╔══════════════════════════════════════════════════════════════════╗
║  ENTERPRISE DOCUMENT INTELLIGENCE - QUICK START GUIDE            ║
╚══════════════════════════════════════════════════════════════════╝

1. INSTALLATION
═══════════════════════════════════════════════════════════════════
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate
$ pip install -r requirements.txt

2. ENVIRONMENT SETUP
═══════════════════════════════════════════════════════════════════
Create .env file in project root:

    GEMINI_API_KEY=your_api_key_here
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=password

Get Gemini API Key: https://aistudio.google.com/app/apikey

3. ADD SAMPLE DOCUMENTS
═══════════════════════════════════════════════════════════════════
• Create folder: data/raw_docs/
• Add PDF files to this folder
• System will process all PDFs automatically

4. RUN DEMO
═══════════════════════════════════════════════════════════════════
$ python demo.py

This will demonstrate all system components:
  ✓ Document loading
  ✓ Text chunking
  ✓ Entity extraction
  ✓ Relation extraction
  ✓ Embedding generation
  ✓ Semantic search
  ✓ Full RAG pipeline

5. START REST API
═══════════════════════════════════════════════════════════════════
$ python -m uvicorn src.api.main:app --reload

Access API:
  • Interactive docs: http://localhost:8000/docs
  • OpenAPI spec: http://localhost:8000/openapi.json
  • Health check: http://localhost:8000/health

6. RUN UNIT TESTS
═══════════════════════════════════════════════════════════════════
$ python tests/test_document_loader.py
$ python tests/test_chunking.py
$ python tests/test_entity_extraction.py

7. BASIC USAGE - PROGRAMMATIC
═══════════════════════════════════════════════════════════════════

from src.rag.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline(enable_graph=False)

# Load and process documents
pipeline.run_full_pipeline("data/raw_docs", enable_graph=False)

# Query
result = pipeline.query("What are the key points?")
print(result["response"])

8. BASIC USAGE - REST API
═══════════════════════════════════════════════════════════════════

Initialize:
  POST http://localhost:8000/initialize
  {
    "document_directory": "data/raw_docs",
    "enable_knowledge_graph": false
  }

Query:
  POST http://localhost:8000/query
  {
    "question": "What are the main findings?",
    "top_k": 5,
    "use_graph": false
  }

Extract Entities:
  POST http://localhost:8000/extract-entities
  {
    "text": "John Smith works at Acme Corporation"
  }

9. TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

Issue: "No documents found"
→ Check: Place PDFs in data/raw_docs/

Issue: "Invalid GEMINI_API_KEY"
→ Solution: Get key from https://aistudio.google.com/app/apikey

Issue: "Neo4j connection failed"
→ Optional: Graph features require Neo4j running
→ Start without graphs: enable_knowledge_graph=false

Issue: "API not responding"
→ Check: Python process running
→ Port: Make sure 8000 is available

10. SYSTEM ARCHITECTURE
═══════════════════════════════════════════════════════════════════

Data Flow:
  PDFs → Load → Chunk → Extract → Embed → Query → Generate

Components:
  • Ingestion: document_loader.py, chunking.py
  • Extraction: entity_extractor.py, relation_extractor.py
  • Embeddings: embedder.py
  • Graph: neo4j_client.py, graph_builder.py
  • Pipeline: rag_pipeline.py
  • API: api/main.py

11. KEY FEATURES
═══════════════════════════════════════════════════════════════════

✓ Multi-document processing
✓ Intelligent text chunking with overlap
✓ Entity extraction (organizations, persons, dates, clauses)
✓ Relation extraction between entities
✓ Semantic search using embeddings
✓ Knowledge graph construction (Neo4j)
✓ RAG-based question answering
✓ REST API with full documentation
✓ Batch and streaming processing

12. PERFORMANCE NOTES
═══════════════════════════════════════════════════════════════════

Processing Time (approximate):
  • Document loading: ~1 sec per MB
  • Chunking: ~50ms per doc
  • Entity extraction: ~2-5 sec per chunk (Gemini)
  • Embedding: ~500ms per chunk
  • Query response: ~1-3 sec total

Optimization Tips:
  • Batch process multiple chunks
  • Cache embeddings
  • Limit top_k for faster retrieval
  • Use query filters on entity types

13. NEXT STEPS
═══════════════════════════════════════════════════════════════════

1. Add your PDF documents
2. Run demo.py to test system
3. Start API server
4. Make test API calls
5. Integrate with your application
6. Customize entity types as needed
7. Set up Neo4j for graph features
8. Deploy to production

14. DOCUMENTATION
═══════════════════════════════════════════════════════════════════

Full Documentation Files:
  • README.md - Complete project overview
  • docs/architecture.md - Detailed system architecture
  • src/*/[module].py - Inline documentation

API Documentation:
  • Interactive: http://localhost:8000/docs
  • ReDoc: http://localhost:8000/redoc

15. SUPPORT & DEBUGGING
═══════════════════════════════════════════════════════════════════

Check Logs:
  • Console output during processing
  • API error responses for debugging
  • Test files: tests/*.py

Debug Mode:
  Add to code:
    import logging
    logging.basicConfig(level=logging.DEBUG)

═══════════════════════════════════════════════════════════════════
Happy documenting! 🚀
═══════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(QUICK_START)
    
    # Also save to file
    with open("QUICKSTART.txt", "w") as f:
        f.write(QUICK_START)
    print("\n✓ Quick start guide saved to QUICKSTART.txt")
