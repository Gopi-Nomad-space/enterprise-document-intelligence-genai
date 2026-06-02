# Enterprise Document Intelligence with GenAI

A comprehensive system for intelligent document processing, entity extraction, and retrieval-augmented generation (RAG) using Google Gemini AI and Neo4j knowledge graphs.

## 🎯 Overview

This project enables organizations to:
- **Load & Process**: Extract text from PDF documents
- **Understand**: Identify entities (organizations, persons, dates, clauses) and relationships
- **Connect**: Build knowledge graphs linking entities and their relationships
- **Retrieve**: Use semantic search to find relevant document sections
- **Generate**: Answer questions using retrieved context (RAG)

## 🏗️ Architecture

```
Documents → Loading → Chunking → Entity & Relation Extraction
                                 ↓
                            Embeddings
                                 ↓
                        Knowledge Graph (Neo4j)
                                 ↓
                        RAG Pipeline & API
```

### Core Components

| Module | Purpose |
|--------|---------|
| **Document Loader** | Extract text from PDF files |
| **Text Chunking** | Split documents into overlapping segments |
| **Entity Extractor** | Identify organizations, persons, dates, clauses using Gemini |
| **Relation Extractor** | Extract relationships between entities |
| **Embedder** | Create semantic vector embeddings for retrieval |
| **Knowledge Graph Builder** | Build Neo4j graph from entities and relations |
| **RAG Pipeline** | Orchestrate full workflow and handle queries |
| **REST API** | FastAPI endpoints for integration |

## 📋 Features

### Information Extraction
- **Entities**: Organizations, Persons, Dates, Clauses
- **Relations**: Relationships between entities (works_for, owns, contains, etc.)
- **Structured Output**: JSON-formatted, Pydantic-validated

### Semantic Search
- Vector embeddings using Gemini embedding model
- Cosine similarity-based chunk retrieval
- Top-k retrieval for relevant context

### Knowledge Graph
- Neo4j database integration
- Entity nodes and relationship edges
- Path finding and connection analysis
- Graph statistics and queries

### RAG System
- Retrieval-augmented generation with Gemini
- Context-aware question answering
- Document-specific responses

### REST API
- FastAPI with comprehensive endpoints
- Document upload and processing
- Query and retrieval operations
- Entity extraction and embedding endpoints

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd enterprise-document-intelligence-genai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies
pip install fastapi uvicorn neo4j
```

### Environment Setup

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### Basic Usage

```python
from src.rag.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(enable_graph=True)

# Run full pipeline
pipeline.run_full_pipeline("data/raw_docs", enable_graph=True)

# Query documents
result = pipeline.query("What are the key clauses in the contract?")
print(result["response"])
```

### Run Tests

```bash
# Test document loading
python tests/test_document_loader.py

# Test chunking
python tests/test_chunking.py

# Test entity extraction
python tests/test_entity_extraction.py
```

## 🔌 API Usage

### Start API Server

```bash
python -m uvicorn src.api.main:app --reload
```

Access API documentation at `http://localhost:8000/docs`

### Example API Calls

**Initialize Pipeline:**
```bash
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "document_directory": "data/raw_docs",
    "enable_knowledge_graph": true
  }'
```

**Query Documents:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the payment terms?",
    "top_k": 5,
    "use_graph": true
  }'
```

**Extract Entities:**
```bash
curl -X POST "http://localhost:8000/extract-entities" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John works for Microsoft on confidential AI projects."
  }'
```

## 📁 Project Structure

```
enterprise-document-intelligence-genai/
├── data/
│   ├── raw_docs/              # Input PDF files
│   └── processed_docs/        # Processed outputs
├── src/
│   ├── api/
│   │   └── main.py           # FastAPI REST endpoints
│   ├── config/
│   │   └── settings.py       # Configuration and API keys
│   ├── embeddings/
│   │   └── embedder.py       # Vector embedding generation
│   ├── extraction/
│   │   ├── entity_extractor.py      # Entity extraction
│   │   └── relation_extractor.py    # Relation extraction
│   ├── ingestion/
│   │   └── document_loader.py       # PDF loading
│   ├── knowledge_graph/
│   │   ├── graph_builder.py         # Graph construction
│   │   └── neo4j_client.py          # Neo4j operations
│   ├── preprocessing/
│   │   └── chunking.py              # Text chunking
│   └── rag/
│       └── rag_pipeline.py          # RAG orchestration
├── tests/
│   ├── test_chunking.py
│   ├── test_document_loader.py
│   └── test_entity_extraction.py
├── docs/
│   └── architecture.md         # Detailed architecture
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Chunk Settings
```python
chunk_size = 800          # Characters per chunk
chunk_overlap = 150       # Overlapping characters
```

### Model Settings
- **LLM**: Google Gemini (gemini-3-flash-preview)
- **Embedding**: Gemini embedding model
- **Temperature**: 0 (deterministic extraction)

### Neo4j
Configure in `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

## 📊 Extracted Information

### Entity Types
- **Organizations**: Company and organization names
- **Persons**: Individual people names
- **Dates**: Temporal references and dates
- **Clauses**: Contract and policy sections

### Relation Types
- `works_for`: Person employed by organization
- `owns`: Entity ownership relationships
- `contains`: Document contains clause/section
- `mentions`: Reference to entity
- `acquired`: Acquisition events
- Custom relations as identified by Gemini

## 🔍 Knowledge Graph Queries

### Find Entity Connections
```python
connections = graph_builder.find_entity_connections("Microsoft")
```

### Query Graph Statistics
```python
stats = graph_builder.query_graph_stats()
# Returns: organizations, persons, dates, clauses counts
```

### Find Paths
```python
paths = neo4j_client.find_paths("Person", "John", "Organization", "Microsoft")
```

## 🎯 RAG Pipeline Workflow

1. **Load Documents** → Extract text from PDFs
2. **Chunk Documents** → Split into overlapping segments
3. **Extract Entities** → Identify key entities using Gemini
4. **Extract Relations** → Find relationships between entities
5. **Create Embeddings** → Generate semantic vectors
6. **Build Graph** → Create Neo4j knowledge graph
7. **Query Processing** → Retrieve similar chunks and generate responses

## ⚙️ Technologies Used

- **Python 3.8+**
- **Google Gemini**: LLM and embeddings
- **Neo4j**: Knowledge graph database
- **FastAPI**: REST API framework
- **LangChain**: Text splitting and utilities
- **PyMuPDF**: PDF text extraction
- **Pydantic**: Data validation
- **NumPy**: Numerical operations

## 📝 Requirements

```
pymupdf
langchain
openai
python-dotenv
pydantic
fastapi
uvicorn
neo4j
google-generativeai
numpy
```

## 🔐 Security Considerations

- Store API keys in `.env` file (never commit to git)
- Use environment variables for sensitive configuration
- Validate all file uploads
- Implement rate limiting for API endpoints
- Use HTTPS in production

## 🐛 Troubleshooting

### Neo4j Connection Failed
- Ensure Neo4j is running: `docker run -p 7687:7687 neo4j`
- Check `.env` credentials
- Verify network connectivity

### No Documents Loaded
- Place PDF files in `data/raw_docs/`
- Check file permissions
- Verify PDF file integrity

### API Errors
- Check API key in `.env`
- Review server logs
- Validate request format
- Check input file sizes

## 📈 Performance Optimization

- Batch process chunks to reduce API calls
- Use caching for frequently accessed embeddings
- Implement pagination for large result sets
- Monitor Neo4j query performance

## 🚦 Future Enhancements

- [ ] Multi-language support
- [ ] Custom entity type recognition
- [ ] Fine-tuned extraction models
- [ ] Advanced graph algorithms
- [ ] Caching layer (Redis)
- [ ] Document versioning
- [ ] Web UI dashboard
- [ ] Analytics and monitoring

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please submit pull requests or issues.

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ for Enterprise Document Intelligence**
