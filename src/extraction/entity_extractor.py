from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

from src.config.settings import OPENAI_API_KEY, MODEL_NAME


# --------- Define Structured Output Schema ---------

class EntityExtraction(BaseModel):
    organizations: List[str] = Field(description="Company or organization names")
    persons: List[str] = Field(description="People names")
    dates: List[str] = Field(description="Dates mentioned")
    clauses: List[str] = Field(description="Contract or policy clauses")


# --------- Build Parser ---------

parser = PydanticOutputParser(pydantic_object=EntityExtraction)


# --------- Prompt Template ---------

prompt = PromptTemplate(
    template="""
You are an AI system that extracts structured entities from enterprise documents.

Extract the following entities from the text:
- Organizations
- Persons
- Dates
- Clauses

Text:
{text}

{format_instructions}
""",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


# --------- LLM ---------

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)


# --------- Extraction Function ---------

def extract_entities(text: str) -> EntityExtraction:
    _input = prompt.format_prompt(text=text)
    response = llm(_input.to_messages())
    return parser.parse(response.content)