from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str

    ALLOWED_ORIGIN: str = "http://localhost:5173"

    VISION_MODEL: str = "qwen/qwen3.6-27b"
    TEXT_MODEL: str = "openai/gpt-oss-120b"

    POPPLER_PATH: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
