from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "School Schedule SaaS"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "sua_chave_secreta_super_segura_aqui"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "default_value")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "default_value")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "default_value")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "default_value")
    DATABASE_URL: Optional[str] = None

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Se existir DATABASE_URL no .env, usamos ela garantindo o driver asyncpg
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        # Caso contrário, monta a URL usando as variáveis individuais
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}?ssl=require"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
