from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    
    azure_subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    reload: bool = True
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "").split(",")
    
    # Agent Configuration
    max_iterations: int = 3
    temperature: float = 0.7
    max_tokens: int = 4000

settings = Settings()