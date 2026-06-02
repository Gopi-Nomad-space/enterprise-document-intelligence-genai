# Architecture Overview

## System Design

The Enterprise Document Intelligence system is built on a modular, layered architecture that enables end-to-end document processing, entity extraction, relationship identification, and semantic retrieval with Generative AI.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  (FastAPI REST API, Web Dashboard, Programmatic SDK)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      RAG PIPELINE                               │
│  Orchestrates entire document processing workflow               │
└────────────────┬────────────────────────────────────┬───────────┘
                 │                                    │
        ┌────────▼────────┐              ┌────────────▼──────┐
        │ DATA INGESTION  │              │ KNOWLEDGE GRAPH   │
        │   & PREP LAYER  │              │    & REASONING    │
        ├─────────────────┤              ├───────────────────┤
        │ • Document      │              │ • Entity Nodes    │
        │   Loading       │              │ • Relations       │
        │ • Chunking      │              │ • Path Finding    │
        │ • Preprocessing │              │ • Graph Queries   │
        └────────────────┘               └───────────────────┘
                 │                                    │
        ┌────────▼────────────────────┐    ┌────────▼──────┐
        │ AI/ML EXTRACTION LAYER       │    │  NEO4J DB     │
        ├──────────────────────────────┤    └───────────────┘
        │ • Entity Extraction (Gemini) │
        │ • Relation Extraction        │
        │ • Embeddings Generation      │
        │ • Semantic Similarity        │
        └──────────────────────────────┘
                 │
        ┌────────▼────────────────────┐
        │  EXTERNAL SERVICES          │
        ├──────────────────────────────┤
        │ • Google Gemini LLM          │
        │ • Gemini Embeddings          │
        │ • Neo4j Database             │
        └──────────────────────────────┘
```

## Detailed Component Architecture

### 1. Ingestion Layer

**Purpose**: Load and preprocess raw documents

```
PDF Files → Document Loader → Raw Text
                                   ↓
                             Text Chunker
                                   ↓
                          Chunked Text Segments
```

**Components**:
- **document_loader.py**: 
  - Uses PyMuPDF for PDF parsing
  - Handles multiple PDF files
  - Extracts clean text content
  
- **chunking.py**:
  - Recursive character splitting
  - Configurable chunk size (default: 800 chars)
  - Overlapping chunks for context preservation (default: 150 char overlap)
  - Smart separators: paragraphs → sentences → words

### 2. Extraction Layer

**Purpose**: Extract structured information from text

```
Text Chunks → Entity Extraction → Entities (JSON)
              ↓
         Relation Extraction → Relations (JSON)
```

**Components**:
- **entity_extractor.py**:
  - Gemini-based extraction
  - Entity types: Organizations, Persons, Dates, Clauses
  - Pydantic model validation
  - JSON output format
  
- **relation_extractor.py**:
  - Relationship identification
  - Relation types: works_for, owns, contains, acquired, etc.
  - Source → Type → Target structure
  - Error handling and fallbacks

### 3. Embeddings Layer

**Purpose**: Create semantic vector representations

```
Text Input → Gemini Embedding Model → Vector (768-dim)
                                           ↓
                                    Store in Memory
                                           ↓
                                    Similarity Search
```

**Components**:
- **embedder.py**:
  - Google Gemini embedding model (embedding-001)
  - Single text embedding
  - Batch chunk embeddings
  - Cosine similarity calculation
  - Top-k retrieval for queries

**Retrieval Process**:
1. Embed query using same model
2. Compare query embedding with all chunk embeddings
3. Calculate cosine similarity scores
4. Return top-k most similar chunks

### 4. Knowledge Graph Layer

**Purpose**: Build structured relationship graph

```
Entities & Relations → Graph Builder → Neo4j Database
                                          ↓
                                    (Node & Edge Creation)
                                          ↓
                                    Graph Queries
```

**Components**:
- **neo4j_client.py**:
  - Neo4j connection management
  - CRUD operations for nodes/edges
  - Cypher query execution
  - Path finding algorithms
  - Graph statistics
  
- **graph_builder.py**:
  - Entity-to-node mapping
  - Relationship creation
  - Batch graph construction
  - Deduplication logic
  - Entity type inference

**Neo4j Schema**:
```
Node Labels:
- Organization (properties: name, document)
- Person (properties: name, document)
- Date (properties: name, document)
- Clause (properties: name, document)

Relationship Types:
- WORKS_FOR
- OWNS
- CONTAINS
- MENTIONS
- ACQUIRED
- [Custom relations]
```

### 5. RAG Pipeline Layer

**Purpose**: Orchestrate entire workflow and handle queries

```
RAG Pipeline
├── Load Documents
├── Preprocess (Chunk)
├── Extract Information
├── Create Embeddings
├── Build Knowledge Graph
└── Query Interface
    ├── Retrieve (Semantic Search)
    ├── Augment (Add Context)
    └── Generate (Gemini Response)
```

**Components**:
- **rag_pipeline.py**:
  - End-to-end workflow orchestration
  - Component lifecycle management
  - Query routing
  - Context augmentation
  - Response generation with Gemini
  - Pipeline statistics

**Query Process** (RAG):
1. **Retrieve**: Semantic search for relevant chunks
2. **Augment**: Add retrieved chunks as context
3. **Generate**: Use Gemini to answer based on context

### 6. API Layer

**Purpose**: Expose functionality via REST endpoints

```
HTTP Requests → FastAPI Router → Core Services → Response
```

**Components**:
- **main.py** (FastAPI):
  - `/initialize`: Pipeline setup
  - `/query`: RAG-based queries
  - `/retrieve`: Chunk retrieval
  - `/extract-entities`: Entity extraction
  - `/embed`: Text embedding
  - `/upload-document`: Document ingestion
  - `/status`: System status
  - `/health`: Health check

## Data Flow Diagrams

### Complete Processing Pipeline

```
Raw PDFs
   │
   ▼
[Document Loader] ──► Raw Text
   │
   ▼
[Text Chunker] ──► Chunks with Metadata
   │
   ├─► [Entity Extractor] ──► Entities (Org, Person, Date, Clause)
   │                                     │
   │                                     ▼
   │                            [Graph Builder] ──┐
   │                                              │
   ├─► [Relation Extractor] ──► Relations ──────┤
   │                                              │
   └─► [Embedder] ──► Vectors                    ▼
                                            [Neo4j Database]
```

### Query Processing Pipeline

```
User Query
   │
   ▼
[Embedder] ──► Query Vector
   │
   ▼
[Similarity Search] ──► Top-k Similar Chunks
   │
   ▼
[Context Augmentation] ──► Query + Context
   │
   ▼
[Gemini LLM] ──► Generated Response
   │
   ▼
Response to User
```

## Technology Stack

### Core Services
| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | Google Gemini | Entity extraction, response generation |
| Embeddings | Gemini Embedding | Semantic vectors |
| Knowledge Graph | Neo4j | Relationship storage and querying |
| PDF Processing | PyMuPDF | Text extraction |
| Text Splitting | LangChain | Intelligent chunking |
| Web Framework | FastAPI | REST API |
| Validation | Pydantic | Data schema validation |

### Libraries & Dependencies
- **NLP**: langchain, google-generativeai
- **Database**: neo4j
- **Web**: fastapi, uvicorn
- **Utilities**: python-dotenv, pydantic
- **Data**: numpy
- **PDF**: pymupdf

## Scalability Considerations

### Horizontal Scaling
- Stateless API design enables load balancing
- Database: Neo4j can be clustered
- Embeddings: Batch processing for throughput

### Optimization Strategies
- Cache embeddings for repeated chunks
- Batch Gemini API calls
- Implement result caching (Redis)
- Pagination for large result sets
- Connection pooling for Neo4j

### Performance Metrics
- Document loading: ~1 second per MB
- Chunking: ~50ms per document
- Entity extraction: ~2-5 seconds per chunk (Gemini latency)
- Embedding generation: ~500ms per chunk
- Query response: ~1-3 seconds (retrieval + generation)

## Security Architecture

### Data Protection
- API keys in environment variables
- HTTPS enforced in production
- Input validation on all endpoints
- File size limits on uploads

### Access Control
- Authentication middleware (to implement)
- Rate limiting per API key (to implement)
- Role-based access (to implement)

### Audit Trail
- Log all API requests (to implement)
- Track data access (to implement)
- Version control for graphs (to implement)

## Error Handling & Resilience

### Fault Tolerance
- Fallback vectors for failed embeddings
- Empty relations list for extraction failures
- Graceful degradation without Neo4j
- Connection retry logic

### Error Categories
| Category | Handling |
|----------|----------|
| API Failures | Retry with exponential backoff |
| Invalid Input | Validation errors with guidance |
| Extraction Failures | Fallback to empty results |
| DB Failures | Continue with in-memory operations |
| Network Issues | Timeout and retry mechanisms |

## Deployment Architecture

### Development
```
Local Machine
└── Workspace
    └── Virtual Environment
        ├── Source Code
        ├── Local Neo4j (Docker)
        └── .env Configuration
```

### Production
```
Cloud Environment
├── Compute: FastAPI Service (Kubernetes/VM)
├── Database: Managed Neo4j
├── Cache: Redis
├── Storage: Document Bucket
├── Monitoring: Logging & Metrics
└── Load Balancer: API Distribution
```

## Integration Points

### External APIs
- **Gemini API**: Entity/relation extraction, embeddings, response generation
- **Neo4j API**: Graph database operations

### Future Integrations
- Document management systems
- Enterprise search engines
- Analytics platforms
- Business intelligence tools

## Performance Optimization

### Current Optimizations
- Batch processing for chunks
- Deduplication in graph building
- Streaming responses from API
- Efficient similarity calculation with NumPy

### Recommended Enhancements
- Implement caching layer (Redis)
- Add connection pooling
- Batch Gemini API calls
- Implement async operations throughout
- Add query result pagination

## Monitoring & Observability

### Metrics to Track
- API response times
- Chunk processing times
- Entity extraction accuracy
- Graph node/edge counts
- Query latency
- Cache hit rates

### Logging Strategy
- Application logs: Processing pipeline events
- API logs: Request/response logging
- Database logs: Neo4j query performance
- Error logs: Exceptions and failures

## Future Architecture Enhancements

1. **Advanced LLMs**: Integration with GPT-4, Claude
2. **Multi-modal**: Support for images, tables in documents
3. **Graph ML**: GNN-based entity linking and relation extraction
4. **Federated Learning**: Privacy-preserving model training
5. **Real-time Streaming**: Process documents as they arrive
6. **Advanced Caching**: Smart cache invalidation
7. **Distributed Processing**: Spark integration for large-scale processing

---

**This architecture is designed for scalability, maintainability, and extensibility while leveraging state-of-the-art AI technologies.**
