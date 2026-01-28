import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List
import json

from src.config.settings import GEMINI_API_KEY, GEMINI_MODEL


# --------- Configure Gemini ---------
genai.configure(api_key=GEMINI_API_KEY)


# --------- Define Structured Output Schema ---------
class EntityExtraction(BaseModel):
    organizations: List[str] = Field(description="Company or organization names")
    persons: List[str] = Field(description="People names")
    dates: List[str] = Field(description="Dates mentioned")
    clauses: List[str] = Field(description="Contract or policy clauses")


# --------- Prompt Builder ---------
def build_prompt(text: str) -> str:
    return f"""
You are an AI system that extracts structured entities from enterprise documents.

Extract ONLY the following entities:
- organizations
- persons
- dates
- clauses

Rules:
- Return VALID JSON ONLY
- Do NOT add explanations
- Use empty lists if none found

Text:
{text}

Output format:
{{
  "organizations": [],
  "persons": [],
  "dates": [],
  "clauses": []
}}
"""


# --------- Gemini Extraction Function ---------
def extract_entities(text: str) -> EntityExtraction:
    model = genai.GenerativeModel(GEMINI_MODEL)

    response = model.generate_content(
        build_prompt(text),
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    parsed_json = json.loads(response.text)
    return EntityExtraction(**parsed_json)