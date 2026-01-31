from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import TenantBase


class Teacher(TenantBase):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)
    email = Column(String, nullable=True)
    importance = Column(Integer)  # Medida de importância
    availabilities = relationship("Availability", back_populates="teacher")
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    school = relationship("School", back_populates="teachers")