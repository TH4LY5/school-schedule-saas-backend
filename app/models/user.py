from sqlalchemy import Column, String, Integer, ForeignKey

from app.models.base import TenantBase


class User(TenantBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String)  # master, admin_school, teacher, etc.
    school_id = Column(Integer, ForeignKey("schools.id"))
    tenant_id = Column(Integer, ForeignKey("schools.id"), nullable=True)