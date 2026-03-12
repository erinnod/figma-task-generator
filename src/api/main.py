from fastapi import FastAPI
from src.config import settings

app = FastAPI(
    title="Figma Task Generator",
    description="AI system that converts Figma designs into development tasks",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "llm_provider": settings.llm_provider
    }