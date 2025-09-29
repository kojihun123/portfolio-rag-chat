from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Jihun's Chat Bot"

    # DB
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    # Embeddings
    embedding_model_name: str = "intfloat/multilingual-e5-large"
    embedding_dim: int = 1024

    # OpenAI
    openai_api_key: str | None = None
    openai_model_name: str = "gpt-4o-mini"
    openai_temperature: float = 0.3

    # RAG
    top_k: int = 5
    max_tokens: int = 512

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()