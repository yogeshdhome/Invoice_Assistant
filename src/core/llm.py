from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.core.config import settings

def get_llm():
    """
    Returns the configured LLM.
    """
    if settings.llm_provider == "openai":
        return ChatOpenAI(api_key=settings.llm_api_key, model=settings.llm_model_name)
    elif settings.llm_provider == "ollama":
        # For local testing with Ollama
        return ChatOllama(model=settings.llm_model_name)
    else:
        # Default to a local model for safety, or raise an error
        # For now, let's raise an error if not configured
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

llm = get_llm()
