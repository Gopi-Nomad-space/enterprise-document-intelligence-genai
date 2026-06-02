"""
Relation extraction module for identifying relationships between entities.
Uses Google Gemini to extract structured relationships from text.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List
import json

from src.config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


# --------- Define Structured Output Schema ---------
class Relation(BaseModel):
    source: str = Field(description="Source entity (subject)")
    relation_type: str = Field(description="Type of relationship")
    target: str = Field(description="Target entity (object)")


class RelationExtraction(BaseModel):
    relations: List[Relation] = Field(description="List of extracted relationships")


# --------- Prompt Builder ---------
def build_relation_prompt(text: str) -> str:
    return f"""
You are an AI system that extracts relationships between entities from enterprise documents.

Extract ONLY direct relationships between entities. Examples:
- "John works for Acme Corp" -> source: "John", relation_type: "works_for", target: "Acme Corp"
- "The contract mentions confidentiality clause" -> source: "contract", relation_type: "contains", target: "confidentiality clause"
- "IBM acquired XYZ on 2023-01-15" -> source: "IBM", relation_type: "acquired", target: "XYZ"

Rules:
- Extract only explicit relationships found in text
- Relation types should be concise (e.g., works_for, located_in, owns, contains, mentions)
- Return VALID JSON ONLY
- Do NOT add explanations
- Use empty list if no relationships found

Text:
{text}

Output format:
{{
  "relations": [
    {{"source": "entity1", "relation_type": "relationship_type", "target": "entity2"}}
  ]
}}
"""


# --------- Gemini Extraction Function ---------
def extract_relations(text: str) -> RelationExtraction:
    """
    Extracts relationships between entities from text.
    
    Args:
        text: Input text to extract relations from
        
    Returns:
        RelationExtraction object with list of relations
    """
    model = genai.GenerativeModel(GEMINI_MODEL)

    response = model.generate_content(
        build_relation_prompt(text),
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    try:
        parsed_json = json.loads(response.text)
        return RelationExtraction(**parsed_json)
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse relation extraction JSON: {e}")
        return RelationExtraction(relations=[])


def extract_relations_from_chunks(chunks: dict) -> dict:
    """
    Extracts relations from all document chunks.
    
    Args:
        chunks: Dictionary mapping doc names to lists of text chunks
        
    Returns:
        Dictionary mapping doc names to lists of relation extractions
    """
    all_relations = {}
    
    for doc_name, chunk_list in chunks.items():
        print(f"\nExtracting relations from {doc_name}...")
        doc_relations = []
        
        for i, chunk in enumerate(chunk_list):
            try:
                relations = extract_relations(chunk)
                doc_relations.append({
                    "chunk_index": i,
                    "relations": relations.relations
                })
                
                if (i + 1) % 5 == 0:
                    print(f"  Processed {i + 1}/{len(chunk_list)} chunks")
                    
            except Exception as e:
                print(f"  ⚠️ Error extracting relations from chunk {i}: {e}")
                doc_relations.append({
                    "chunk_index": i,
                    "relations": []
                })
        
        all_relations[doc_name] = doc_relations
    
    return all_relations
