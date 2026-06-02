"""
FastAPI REST API for Document Intelligence and RAG System.
Provides endpoints for document processing, entity extraction, and query handling.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from pathlib import Path

from src.rag.rag_pipeline import RAGPipeline
from src.extraction.entity_extractor import extract_entities
from src.extraction.relation_extractor import extract_relations
from src.embeddings.embedder import embed_text

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise Document Intelligence API",
    description="API for document processing, entity extraction, and RAG-based question answering",
    version="1.0.0"
)

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None


# --------- Pydantic Models ---------
class InitializationRequest(BaseModel):
    document_directory: str
    enable_knowledge_graph: bool = False


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    use_graph: bool = False


class ExtractEntitiesRequest(BaseModel):
    text: str


class EmbedTextRequest(BaseModel):
    text: str


class HealthResponse(BaseModel):
    status: str
    pipeline_ready: bool
    message: str


class QueryResponse(BaseModel):
    question: str
    response: str
    retrieved_chunks: List[Dict]
    graph_connections: Optional[List[Dict]] = None


class DocumentProcessingResponse(BaseModel):
    status: str
    documents_count: int
    chunks_created: int
    message: str


# --------- Health Check Endpoints ---------
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health and pipeline status.
    """
    pipeline_ready = rag_pipeline is not None and len(rag_pipeline.documents) > 0
    
    return HealthResponse(
        status="healthy",
        pipeline_ready=pipeline_ready,
        message="API is running" if pipeline_ready else "Pipeline not initialized"
    )


# --------- Initialization Endpoints ---------
@app.post("/initialize", response_model=DocumentProcessingResponse)
async def initialize_pipeline(request: InitializationRequest):
    """
    Initialize the RAG pipeline with documents.
    """
    global rag_pipeline
    
    # Validate directory
    if not os.path.isdir(request.document_directory):
        raise HTTPException(
            status_code=400,
            detail=f"Directory not found: {request.document_directory}"
        )
    
    try:
        # Create pipeline
        rag_pipeline = RAGPipeline(enable_graph=request.enable_knowledge_graph)
        
        # Run full pipeline
        success = rag_pipeline.run_full_pipeline(
            request.document_directory,
            enable_graph=request.enable_knowledge_graph
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize pipeline"
            )
        
        summary = rag_pipeline.get_summary()
        
        return DocumentProcessingResponse(
            status="success",
            documents_count=summary["documents_loaded"],
            chunks_created=summary["total_chunks"],
            message="Pipeline initialized successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline initialization error: {str(e)}"
        )


# --------- Query Endpoints ---------
@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents using RAG (Retrieval-Augmented Generation).
    """
    if rag_pipeline is None or len(rag_pipeline.documents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Pipeline not initialized. Call /initialize first."
        )
    
    try:
        result = rag_pipeline.query(request.question, use_graph=request.use_graph)
        
        return QueryResponse(
            question=result["question"],
            response=result["response"],
            retrieved_chunks=result["retrieved_chunks"],
            graph_connections=result.get("graph_connections", None)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query error: {str(e)}"
        )


@app.get("/retrieve/{query}")
async def retrieve_chunks(query: str, top_k: int = 5):
    """
    Retrieve most relevant chunks for a query.
    """
    if rag_pipeline is None or len(rag_pipeline.embeddings) == 0:
        raise HTTPException(
            status_code=400,
            detail="Pipeline not initialized or embeddings not created"
        )
    
    try:
        chunks = rag_pipeline.retrieve_relevant_chunks(query, top_k)
        return {
            "query": query,
            "top_k": top_k,
            "results": chunks
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval error: {str(e)}"
        )


# --------- Entity Extraction Endpoints ---------
@app.post("/extract-entities")
async def extract_entities_endpoint(request: ExtractEntitiesRequest):
    """
    Extract structured entities from text.
    """
    try:
        entities = extract_entities(request.text)
        
        return {
            "text_length": len(request.text),
            "entities": {
                "organizations": entities.organizations,
                "persons": entities.persons,
                "dates": entities.dates,
                "clauses": entities.clauses
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Entity extraction error: {str(e)}"
        )


# --------- Embedding Endpoints ---------
@app.post("/embed")
async def embed_text_endpoint(request: EmbedTextRequest):
    """
    Generate embedding for text.
    """
    try:
        embedding = embed_text(request.text)
        
        return {
            "text_length": len(request.text),
            "embedding_dimension": len(embedding),
            "embedding": embedding[:10] + ["..."]  # Return first 10 values as preview
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding error: {str(e)}"
        )


# --------- Status Endpoints ---------
@app.get("/status")
async def get_status():
    """
    Get current pipeline status and statistics.
    """
    if rag_pipeline is None:
        return {
            "status": "not_initialized",
            "message": "Pipeline not initialized"
        }
    
    summary = rag_pipeline.get_summary()
    
    return {
        "status": "initialized",
        "summary": summary,
        "message": "Pipeline is ready for queries"
    }


@app.get("/documents")
async def list_documents():
    """
    List all loaded documents.
    """
    if rag_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="Pipeline not initialized"
        )
    
    documents = list(rag_pipeline.documents.keys())
    
    return {
        "count": len(documents),
        "documents": documents
    }


# --------- Document Upload Endpoint ---------
@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a new PDF document.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        upload_dir = "data/raw_docs"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "status": "success",
            "filename": file.filename,
            "path": file_path,
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload error: {str(e)}"
        )


# --------- Info Endpoint ---------
@app.get("/info")
async def get_api_info():
    """
    Get API information and available endpoints.
    """
    return {
        "name": "Enterprise Document Intelligence API",
        "version": "1.0.0",
        "description": "Document processing and RAG system",
        "endpoints": {
            "health": {
                "path": "/health",
                "method": "GET",
                "description": "Check API health and pipeline status"
            },
            "initialize": {
                "path": "/initialize",
                "method": "POST",
                "description": "Initialize pipeline with documents"
            },
            "query": {
                "path": "/query",
                "method": "POST",
                "description": "Query documents using RAG"
            },
            "retrieve": {
                "path": "/retrieve/{query}",
                "method": "GET",
                "description": "Retrieve relevant chunks for a query"
            },
            "extract_entities": {
                "path": "/extract-entities",
                "method": "POST",
                "description": "Extract entities from text"
            },
            "embed": {
                "path": "/embed",
                "method": "POST",
                "description": "Generate text embedding"
            },
            "status": {
                "path": "/status",
                "method": "GET",
                "description": "Get pipeline status"
            },
            "documents": {
                "path": "/documents",
                "method": "GET",
                "description": "List loaded documents"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
