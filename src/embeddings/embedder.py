"""
Embeddings module for creating vector representations of text chunks.
Uses Google Gemini's embedding model for semantic vectorization.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from typing import List, Dict
import numpy as np

from src.config.settings import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def embed_text(text: str) -> List[float]:
    """
    Generates embedding for a single text chunk.
    
    Args:
        text: Text to embed
        
    Returns:
        Vector embedding (list of floats)
    """
    response = genai.embed_content(
        model="models/embedding-001",
        content=text
    )
    return response["embedding"]


def embed_chunks(chunks: Dict[str, List[str]]) -> Dict[str, List[List[float]]]:
    """
    Generates embeddings for all text chunks.
    
    Args:
        chunks: Dictionary mapping doc names to lists of text chunks
        
    Returns:
        Dictionary mapping doc names to lists of embeddings
    """
    embeddings = {}
    
    for doc_name, chunk_list in chunks.items():
        doc_embeddings = []
        
        for i, chunk in enumerate(chunk_list):
            try:
                embedding = embed_text(chunk)
                doc_embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    print(f"  Embedded {i + 1}/{len(chunk_list)} chunks from {doc_name}")
                    
            except Exception as e:
                print(f"  ⚠️ Error embedding chunk {i} in {doc_name}: {e}")
                # Use zero vector as fallback
                doc_embeddings.append([0.0] * 768)
        
        embeddings[doc_name] = doc_embeddings
    
    return embeddings


def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculates cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score (0-1)
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def retrieve_similar_chunks(
    query: str,
    all_embeddings: Dict[str, List[List[float]]],
    all_chunks: Dict[str, List[str]],
    top_k: int = 5
) -> List[Dict]:
    """
    Retrieves top-k most similar chunks to a query using embeddings.
    
    Args:
        query: Query text
        all_embeddings: All chunk embeddings
        all_chunks: All chunks
        top_k: Number of top results to return
        
    Returns:
        List of dicts with chunk, document, and similarity score
    """
    query_embedding = embed_text(query)
    
    results = []
    
    for doc_name, chunk_list in all_chunks.items():
        embeddings = all_embeddings[doc_name]
        
        for idx, chunk in enumerate(chunk_list):
            similarity = calculate_similarity(query_embedding, embeddings[idx])
            results.append({
                "document": doc_name,
                "chunk_index": idx,
                "chunk": chunk,
                "similarity": similarity
            })
    
    # Sort by similarity and return top-k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]
