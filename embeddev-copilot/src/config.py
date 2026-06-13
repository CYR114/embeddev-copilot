"""全局配置"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    demo_mode: bool = True

    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4

    # 路径
    data_dir: str = "data"
    chroma_dir: str = "data/chroma_db"


settings = Settings()
