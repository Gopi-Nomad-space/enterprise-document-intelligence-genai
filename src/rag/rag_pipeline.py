"""
RAG (Retrieval-Augmented Generation) Pipeline
Orchestrates the complete document intelligence workflow:
1. Load documents
2. Chunk text
3. Extract entities and relations
4. Create embeddings
5. Build knowledge graph
6. Enable retrieval-based generation
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from typing import List, Dict, Optional
import google.generativeai as genai

from src.ingestion.document_loader import load_documents_from_dir, load_pdf
from src.preprocessing.chunking import chunk_documents
from src.extraction.entity_extractor import extract_entities
from src.extraction.relation_extractor import extract_relations
from src.embeddings.embedder import embed_chunks, retrieve_similar_chunks
from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from src.knowledge_graph.neo4j_client import Neo4jClient
from src.config.settings import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)


class RAGPipeline:
    """
    Complete RAG pipeline for document intelligence and retrieval-augmented generation.
    """
    
    def __init__(self, enable_graph: bool = False):
        """
        Initialize RAG pipeline.
        
        Args:
            enable_graph: Whether to build Neo4j knowledge graph
        """
        self.documents = {}
        self.chunks = {}
        self.embeddings = {}
        self.entities = {}
        self.relations = {}
        
        self.enable_graph = enable_graph
        self.graph_builder = None
        
        if enable_graph:
            try:
                neo4j_client = Neo4jClient()
                if neo4j_client.connect():
                    self.graph_builder = KnowledgeGraphBuilder(neo4j_client)
            except Exception as e:
                print(f"⚠️ Neo4j not available: {e}")
    
    def load_documents(self, directory: str) -> bool:
        """
        Load all PDF documents from a directory.
        
        Args:
            directory: Path to directory with PDF files
            
        Returns:
            True if documents loaded successfully
        """
        try:
            print(f"\n📄 Loading documents from {directory}...")
            self.documents = load_documents_from_dir(directory)
            print(f"✓ Loaded {len(self.documents)} documents")
            return len(self.documents) > 0
        except Exception as e:
            print(f"✗ Failed to load documents: {e}")
            return False
    
    def preprocess_documents(self, chunk_size: int = 800, chunk_overlap: int = 150) -> bool:
        """
        Chunk documents into overlapping segments.
        
        Args:
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            True if preprocessing successful
        """
        try:
            print(f"\n✂️  Chunking documents...")
            self.chunks = chunk_documents(self.documents, chunk_size, chunk_overlap)
            
            total_chunks = sum(len(chunks) for chunks in self.chunks.values())
            print(f"✓ Created {total_chunks} chunks from {len(self.chunks)} documents")
            return True
        except Exception as e:
            print(f"✗ Failed to preprocess documents: {e}")
            return False
    
    def extract_information(self) -> bool:
        """
        Extract entities and relations from all chunks.
        
        Returns:
            True if extraction successful
        """
        try:
            print(f"\n🔍 Extracting entities and relations...")
            
            # Extract entities from all chunks
            for doc_name, chunk_list in self.chunks.items():
                print(f"\n  Processing {doc_name}...")
                doc_entities = []
                doc_relations = []
                
                for i, chunk in enumerate(chunk_list):
                    # Extract entities
                    entities = extract_entities(chunk)
                    doc_entities.append(entities)
                    
                    # Extract relations
                    relations = extract_relations(chunk)
                    doc_relations.append(relations)
                    
                    if (i + 1) % 5 == 0:
                        print(f"    Processed {i + 1}/{len(chunk_list)} chunks")
                
                self.entities[doc_name] = doc_entities
                self.relations[doc_name] = doc_relations
            
            print(f"\n✓ Extraction complete")
            return True
        except Exception as e:
            print(f"✗ Failed to extract information: {e}")
            return False
    
    def create_embeddings(self) -> bool:
        """
        Create semantic embeddings for all chunks.
        
        Returns:
            True if embedding creation successful
        """
        try:
            print(f"\n🧠 Creating embeddings...")
            self.embeddings = embed_chunks(self.chunks)
            print(f"✓ Created embeddings for all chunks")
            return True
        except Exception as e:
            print(f"✗ Failed to create embeddings: {e}")
            return False
    
    def build_knowledge_graph(self) -> bool:
        """
        Build Neo4j knowledge graph from entities and relations.
        
        Returns:
            True if graph building successful
        """
        if not self.enable_graph or not self.graph_builder:
            print("⚠️ Knowledge graph disabled")
            return False
        
        try:
            self.graph_builder.build_from_all_extractions(
                self.entities,
                self.relations
            )
            
            stats = self.graph_builder.query_graph_stats()
            print(f"✓ Knowledge graph stats: {stats}")
            return True
        except Exception as e:
            print(f"✗ Failed to build knowledge graph: {e}")
            return False
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query using semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        if not self.embeddings:
            print("✗ Embeddings not created. Call create_embeddings() first.")
            return []
        
        return retrieve_similar_chunks(query, self.embeddings, self.chunks, top_k)
    
    def generate_response(
        self,
        query: str,
        retrieved_chunks: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate response using retrieved context (RAG).
        
        Args:
            query: User query
            retrieved_chunks: Retrieved context chunks (retrieves if None)
            
        Returns:
            Generated response from Gemini
        """
        if retrieved_chunks is None:
            retrieved_chunks = self.retrieve_relevant_chunks(query)
        
        if not retrieved_chunks:
            return "No relevant information found in documents."
        
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[{chunk['document']} - Chunk {chunk['chunk_index']}] (Relevance: {chunk['similarity']:.2f})\n{chunk['chunk']}"
            for chunk in retrieved_chunks
        ])
        
        # Generate response using Gemini
        prompt = f"""Based on the following document excerpts, answer the user's question.

Context:
{context}

Question: {query}

Please provide a concise, accurate answer based on the provided context. If the information is not in the context, say so."""
        
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"
    
    def run_full_pipeline(self, document_dir: str, enable_graph: bool = False) -> bool:
        """
        Execute the complete RAG pipeline.
        
        Args:
            document_dir: Directory containing PDF documents
            enable_graph: Whether to build knowledge graph
            
        Returns:
            True if pipeline successful
        """
        self.enable_graph = enable_graph
        
        print("=" * 60)
        print("🚀 STARTING DOCUMENT INTELLIGENCE RAG PIPELINE")
        print("=" * 60)
        
        # Execute pipeline steps
        if not self.load_documents(document_dir):
            return False
        
        if not self.preprocess_documents():
            return False
        
        if not self.extract_information():
            return False
        
        if not self.create_embeddings():
            return False
        
        if enable_graph and not self.build_knowledge_graph():
            print("⚠️ Graph building failed, continuing without graph")
        
        print("\n" + "=" * 60)
        print("✓ PIPELINE COMPLETE - Ready for queries")
        print("=" * 60)
        
        return True
    
    def query(self, question: str, use_graph: bool = False) -> Dict:
        """
        Query the pipeline with a question.
        
        Args:
            question: User question
            use_graph: Whether to include graph context
            
        Returns:
            Dict with retrieved chunks and generated response
        """
        print(f"\n❓ Query: {question}")
        
        # Retrieve relevant chunks
        retrieved_chunks = self.retrieve_relevant_chunks(question)
        
        # Generate response
        response = self.generate_response(question, retrieved_chunks)
        
        result = {
            "question": question,
            "retrieved_chunks": retrieved_chunks,
            "response": response
        }
        
        # Add graph context if available
        if use_graph and self.graph_builder:
            # Try to find entities in graph related to query
            for entity in question.split():
                connections = self.graph_builder.find_entity_connections(entity)
                if connections:
                    result["graph_connections"] = connections
                    break
        
        return result
    
    def get_summary(self) -> Dict:
        """
        Get summary of loaded data and processing state.
        
        Returns:
            Dictionary with summary information
        """
        return {
            "documents_loaded": len(self.documents),
            "total_chunks": sum(len(chunks) for chunks in self.chunks.values()),
            "embeddings_created": len(self.embeddings) > 0,
            "entities_extracted": len(self.entities) > 0,
            "relations_extracted": len(self.relations) > 0,
            "knowledge_graph_enabled": self.graph_builder is not None
        }
