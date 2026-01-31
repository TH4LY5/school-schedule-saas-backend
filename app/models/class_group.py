from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ClassGroup(Base):
    __tablename__ = "class_group"

    # CERTIFIQUE-SE DE QUE ESTA LINHA TEM O primary_key=True
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"))
    grade = Column(String, nullable=True)  # Ex: "9º Ano", "1º EM"
    shift = Column(String, nullable=True)  # Ex: "Matutino" (Opcional, mas recomendado)
    # Relacionamentos
    school = relationship("School", back_populates="class_groups")
    subjects = relationship("Subject", back_populates="class_group")