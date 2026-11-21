from app.config import Settings
from app.llm.base import AIService, AIServiceNotConfigured
from app.llm.remote import build_ai_service


def get_ai_service(settings: Settings) -> AIService:
    return build_ai_service(settings)


__all__ = ["AIService", "AIServiceNotConfigured", "get_ai_service"]
