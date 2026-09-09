from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_ADMIN_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_ROUTER_MODEL: str = "inclusionai/ling-3.0-flash-sante:free"
    DEFAULT_CHAT_MODEL: str = "inclusionai/ling-3.0-flash-sante:free"
    class Config:
        env_file = ".env"
        extra = "ignore"
settings = Settings()
