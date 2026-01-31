from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TenantBase

class School(TenantBase):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    address = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    class_groups = relationship("ClassGroup", back_populates="school")
    teachers = relationship("Teacher", back_populates="school")
    schedules = relationship("Schedule", back_populates="school")
    subjects = relationship("Subject", back_populates="school")