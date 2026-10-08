from app.config import settings
from app.ai.provider import AIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider

def get_ai_provider() -> AIProvider:
    if settings.LLM_PROVIDER.lower() == "ollama":
        return OllamaProvider()
    return OpenAIProvider()
