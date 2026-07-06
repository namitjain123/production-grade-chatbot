import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Load environment variables from .env file
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")
    JUDGE_GROQ = os.getenv("JUDGE_GROQ")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION="enterprise_rag"
    GROQ_MODEL= "llama-3.3-70b-versatile"
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")

settings = Settings()