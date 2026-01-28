import os
from dotenv import load_dotenv

load_dotenv()

#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#MODEL_NAME = "gpt-4o-mini"  # or gpt-3.5-turbo

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-flash-preview"