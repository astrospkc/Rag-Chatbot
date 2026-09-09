from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from internal.core.config import settings
class LLMFactory:
    @staticmethod
    @lru_cache(maxsize=4)
    def get_llm(provider:str ="openrouter",model:str|None=None,temprature:float=0.7,max_tokens:int=512):
        if provider == "openrouter":
            return ChatOpenAI(
                model=model or settings.DEFAULT_ROUTER_MODEL,
                api_key=settings.OPENROUTER_ADMIN_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                },
                temperature=temprature,
                max_tokens=max_tokens
            )
        elif provider =="gemini":
            return ChatGoogleGenerativeAI(
                model=model or settings.DEFAULT_CHAT_MODEL,
                api_key=settings.GEMINI_API_KEY,
                temperature=temprature,
                max_tokens=max_tokens
            )
        raise ValueError(f"Unknown provider:{provider}")
                