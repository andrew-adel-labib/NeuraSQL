from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    LLM_PROVIDER: str = "llama-3.3-70b-versatile"

    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-haiku-4-5"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    LLM_MODEL: str = "claude-haiku-4-5"

    PBI_TENANT_ID: str
    PBI_CLIENT_ID: str
    PBI_CLIENT_SECRET: str
    PBI_WORKSPACE_ID: str
    PBI_DATASET_ID: str
    PBI_REPORT_ID: str
    POWERBI_EMBED_URL: str

    DB_DRIVER: str
    DB_SERVER: str
    DB_NAME: str
    DB_TRUSTED_CONNECTION: str = "yes"

    LOG_LEVEL: str = "INFO"
    ENV: str = "development"
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()