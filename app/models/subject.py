from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantBase

class Subject(TenantBase):
    __tablename__ = "subject"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String)
    class_group_id = Column(Integer, ForeignKey("class_group.id"))
    teacher_id = Column(Integer, ForeignKey("teacher.id"))
    weekly_hours = Column(Integer)
    weekly_lessons = Column(Integer, nullable=False)  # Ex: 4 aulas por semana
    allow_consecutive = Column(Boolean, default=True)  # Permite dobradinha?
    max_daily_lessons = Column(Integer, default=2)  # No máximo 2 por dia
    requires_special_room = Column(Boolean, default=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    school = relationship("School", back_populates="subjects")
    class_group = relationship("ClassGroup", back_populates="subjects")