import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

# Forçamos o caminho para a raiz do projeto (um nível acima de onde este arquivo config.py está)
# Isso garante que ele ignore qualquer .env dentro da pasta 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))  # app/core
base_dir = os.path.dirname(os.path.dirname(current_dir))  # raiz do projeto
env_path = os.path.join(base_dir, ".env")


class Settings(BaseSettings):
    PROJECT_NAME: str = "School Schedule SaaS"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secret"

    # Valores padrão (serão substituídos pelo .env se ele for lido)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "school_schedule"

    # Configuração do Pydantic para ler o .env na raiz
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Importante: Bancos na nuvem (Aiven) EXIGEM SSL.
        # Adicionei o parâmetro ssl=require automaticamente.
        url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        if "localhost" not in self.POSTGRES_SERVER:
            url += "?ssl=require"
        return url


@lru_cache()
def get_settings():
    conf = Settings()
    print("=" * 60)
    print("CONFIGURAÇÕES CARREGADAS:")
    print("=" * 60)
    print(f"Buscando arquivo em: {env_path}")
    print(f"Arquivo existe? {'SIM' if os.path.exists(env_path) else 'NÃO'}")
    print(f"POSTGRES_SERVER: {conf.POSTGRES_SERVER}")
    print(f"DATABASE_URL:    {conf.ASYNC_DATABASE_URL.split('@')[-1]}")
    print("=" * 60)
    return conf


settings = get_settings()