from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Cria a engine assíncrona usando a URL definida no config.py
engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)

# Configura a sessão
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Função (dependência) que será usada em todos os endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session