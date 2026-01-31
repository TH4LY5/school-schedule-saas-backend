from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantBase


class Constraint(TenantBase):
    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    # Nome descritivo (Opcional, só para o humano ler. Ex: "Folga do João")
    name = Column(String, nullable=True)

    # O "Código" que o algoritmo lê. (Ex: "TEACHER_UNAVAILABILITY")
    # Substitui o antigo 'rule_type' e 'type' duplicados
    type = Column(String, nullable=False)

    # O JSON com os detalhes. (Ex: {"teacher_id": 1, "day": 4})
    # Substitui o antigo 'configuration' e 'data' duplicados
    data = Column(JSON, nullable=False)

    # Peso (100 = Obrigatório/Hard, <100 = Desejável/Soft)
    weight = Column(Integer, default=100)

    # Se a regra está valendo ou foi pausada
    active = Column(Boolean, default=True)

    # Relacionamento
    school = relationship("School")