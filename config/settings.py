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
    
    # AI Configuration - Local LLM (Ollama with CUDA)
    AI_PROVIDER: str = "local"  # local = Ollama (no API keys needed)
    MISTRAL_API_KEY: str = ""  # Not used with local provider
    OPENAI_API_KEY: str = ""  # Not used with local provider
    LOCAL_LLM_URL: str = "http://localhost:11434/v1"  # Ollama default
    LOCAL_LLM_MODEL: str = "tinyllama"  # TinyLlama 1.1B (~4GB VRAM, leaves 4GB free for OS)
    AI_MODEL: str = "tinyllama"  # Model name for display/logging
    AI_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 800  # Conservative for fast response
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
