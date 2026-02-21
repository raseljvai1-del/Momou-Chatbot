import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = Client(api_key=api_key)

