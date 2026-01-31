from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Bases Comuns ---
class AvailabilityBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True

class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    weekly_hours: int
    teacher_id: Optional[int] = None

class TeacherBase(BaseModel):
    name: str
    code: Optional[str] = None
    importance: int = 1

class ClassGroupBase(BaseModel):
    name: str
    grade: str
    shift: str

# --- Creates & Updates ---
class AvailabilityCreate(AvailabilityBase):
    pass

class SubjectCreate(SubjectBase):
    pass

class TeacherCreate(TeacherBase):
    availabilities: List[AvailabilityCreate] = []

class ClassGroupCreate(ClassGroupBase):
    subjects: List[SubjectCreate] = []

# --- Reads (Retorno da API) ---
class TeacherRead(TeacherBase):
    id: int
    availabilities: List[AvailabilityBase] = []
    class Config:
        from_attributes = True

class ClassGroupRead(ClassGroupBase):
    id: int
    subjects: List[SubjectBase] = []
    class Config:
        from_attributes = True

class ScheduleRead(BaseModel):
    id: int
    status: str
    generated_at: Optional[datetime]
    conflicts: Optional[Any]
    result: Optional[Any]
    class Config:
        from_attributes = True


class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None


class SchoolCreate(SchoolBase):
    pass


class SchoolRead(SchoolBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TeacherCreate(BaseModel):
    name: str
    code: str
    email: Optional[str] = None  # Adicione este campo
    importance: int = 1          # Adicione este campo (veio no seu payload)
    school_id: Optional[int] = None # Necessário para o multi-tenant
    availabilities: List[Any] = []  # Para receber a lista do seu payload

class AvailabilitySchema(BaseModel):
    id: int
    day_of_week: int
    period: int
    is_available: bool

    class Config:
        from_attributes = True # Antigo orm_mode = True

# Schema de Resposta do Professor
class TeacherSchema(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    code: Optional[str] = None
    importance: int
    school_id: int
    # Aqui usamos o schema de disponibilidade para retornar a lista detalhada
    availabilities: List[AvailabilitySchema] = []

    class Config:
        from_attributes = True # Permite ler direto do banco de dados

class ClassGroupCreate(BaseModel):
    name: str
    grade: Optional[str] = None
    shift: Optional[str] = None
    school_id: Optional[int] = None


class ClassGroupSchema(BaseModel):
    id: int
    name: str
    grade: Optional[str] = None
    shift: Optional[str] = None
    school_id: int

    class Config:
        from_attributes = True

class ScheduleSchema(BaseModel):
    id: int
    status: str
    generated_at: Optional[datetime]
    school_id: int
    result_data: Optional[Any] = None

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str
    weekly_lessons: int = 4
    max_daily_lessons: int = 2
    allow_consecutive: bool = True
    teacher_id: Optional[int] = None
    class_group_id: Optional[int] = None


class SubjectSchema(SubjectCreate):
    id: int
    school_id: int

    class Config:
        from_attributes = True

class ConstraintCreate(BaseModel):
    type: str
    data: Dict[str, Any]


class ConstraintSchema(ConstraintCreate):
    id: int
    school_id: int

    class Config:
        from_attributes = True