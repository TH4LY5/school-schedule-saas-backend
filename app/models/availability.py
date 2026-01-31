from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship  # Adicione este import
from app.models.base import TenantBase

class Availability(TenantBase):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teacher.id"))
    day_of_week = Column(Integer)
    start_time = Column(String)
    end_time = Column(String)
    is_available = Column(Boolean, default=True)

    # ESTA LINHA É A QUE FALTA:
    teacher = relationship("Teacher", back_populates="availabilities")