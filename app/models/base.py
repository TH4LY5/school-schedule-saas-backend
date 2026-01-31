from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func  # <--- A solução mágica


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Gera o nome da tabela automaticamente (ex: User -> user)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TenantBase(Base):
    """
    Classe base para todas as tabelas que pertencem a um 'dono' (SaaS).
    Adiciona ID, Owner, Created_at e Updated_at automaticamente.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    # owner_id = Column(Integer, ForeignKey("user.id")) # Descomente se todos herdarem user
    # Mas cuidado com import circular. Geralmente define-se owner_id na classe filha ou aqui com string.

    # SOLUÇÃO DO ERRO AQUI:
    # Usamos server_default=func.now() para que o Postgres defina a hora
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)