from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

# IMPORTANTE: Importar o pacote models garante que todos os ficheiros
# (user, school, class_group, subject, etc.) sejam lidos e registados no Base.metadata
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INÍCIO: Criação Automática de Tabelas (Modo Dev) ---
    print(f"INFO:     Iniciando {settings.PROJECT_NAME} e verificando banco de dados...")

    try:
        async with engine.begin() as conn:
            # Isso cria todas as tabelas definidas nos models se elas não existirem
            # O run_sync é necessário porque o create_all do SQLAlchemy não é nativamente assíncrono
            await conn.run_sync(Base.metadata.create_all)
        print("INFO:     Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"ERROR:    Erro ao criar tabelas: {e}")
    # --- FIM ---

    yield

    print(f"INFO:     Finalizando {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o sistema de Gestão de Horários Escolares (SaaS)",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração do CORS
origins = [
    "http://localhost:4200",  # Angular dev
    "http://localhost:3000",  # React dev
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo as rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Bem-vindo à API do {settings.PROJECT_NAME}",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)