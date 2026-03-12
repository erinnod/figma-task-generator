from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # Figma
    figma_api_token: str = ""
    
    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    llm_model: str = "claude-opus-4-5"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Single instance imported everywhere
settings = Settings()