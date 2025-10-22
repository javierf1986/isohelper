"""
Configuration settings using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ISO 9001 AI Documentation Generator"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AI Configuration
    AI_PROVIDER: str = "mistral"  # mistral, openai, or local
    MISTRAL_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LOCAL_LLM_URL: str = "http://localhost:11434/v1"  # Ollama default
    AI_MODEL: str = "mistral-medium"
    AI_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    ENABLE_AI_ENHANCEMENT: bool = True  # Toggle AI features on/off
    
    # Database
    DATABASE_URL: str = "sqlite:///./isohelper.db"  # Default to SQLite for development
    
    # Document Storage
    DOCUMENTS_PATH: str = "./generated_documents"
    TEMPLATES_PATH: str = "./templates/iso9001"
    
    # MarkItDown Configuration
    ENABLE_MARKITDOWN: bool = True
    OUTPUT_FORMATS: List[str] = ["pdf", "docx", "html"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()
