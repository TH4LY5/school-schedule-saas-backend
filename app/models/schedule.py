from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import TenantBase


class Schedule(TenantBase):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    generated_at = Column(DateTime)
    result_data = Column(JSON, nullable=True)  # Para salvar o JSON da grade gerada

    # Adicione ou Verifique:
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    # Relacionamento
    school = relationship("School", back_populates="schedules")