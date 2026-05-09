from pydantic_settings import BaseSettings


class Settings(BaseSettings):


    LLM_PROVIDER: str = "claude"

    LLM_MODEL: str = "claude-haiku-4-5"


    CLAUDE_API_KEY: str = ""

    CLAUDE_MODEL: str = "claude-haiku-4-5"


    OPENAI_API_KEY: str = ""

    OPENAI_MODEL: str = "gpt-4o-mini"


    GROQ_API_KEY: str = ""

    GROQ_MODEL: str = "llama-3.1-8b-instant"


    REALTIME_ENABLED: bool = True

    WEBSOCKET_URL: str = (
        "ws://localhost:8000/realtime/ws"
    )

    OPENAI_WHISPER_MODEL: str = (
        "whisper-1"
    )

    GROQ_WHISPER_MODEL: str = (
        "whisper-large-v3"
    )


    DB_DRIVER: str

    DB_SERVER: str

    DB_NAME: str

    DB_TRUSTED_CONNECTION: str = "yes"


    LOG_LEVEL: str = "INFO"

    ENV: str = "development"

    BACKEND_URL: str = (
        "http://localhost:8000"
    )

    FRONTEND_URL: str = (
        "http://localhost:3000"
    )


    class Config:

        env_file = ".env"

        extra = "ignore"


settings = Settings()