"""LLM 工厂：统一创建 Chat 模型，支持 Demo 模式"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from src.config import settings


def create_chat_model(temperature: float = 0.2) -> BaseChatModel | None:
    """创建 LLM；Demo 模式下返回 None，由规则引擎接管"""
    if settings.demo_mode or not settings.openai_api_key:
        return None

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=temperature,
    )
