from app.config import Settings
from app.llm.base import AIService
from app.llm.remote import build_ai_service


def get_ai_service(settings: Settings) -> AIService:
    return build_ai_service(settings)
