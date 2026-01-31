from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from app.api import dependencies
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.models.teacher import Teacher
from app.schemas.school_schemas import TeacherCreate, TeacherRead, TeacherSchema

router = APIRouter()


@router.post("/", response_model=TeacherRead)
async def create_teacher(
        teacher_in: TeacherCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Se o school_id não vier no payload, tenta pegar do usuário logado
    school_id_to_use = teacher_in.school_id
    if not school_id_to_use and hasattr(current_user, 'school_id'):
        school_id_to_use = current_user.school_id

    teacher = Teacher(
        name=teacher_in.name,
        code=teacher_in.code,
        email=teacher_in.email,  # Agora vai funcionar (pode ser None)
        importance=teacher_in.importance,  # Certifique-se que o Model Teacher tem esse campo
        school_id=school_id_to_use
    )

    db.add(teacher)
    await db.commit()

    # MUDE AQUI: Use 'options(selectinload(...))' ao fazer o refresh ou select
    # Como refresh não aceita options diretamente de forma simples em versões antigas,
    # o jeito mais seguro no async é fazer um select novo:

    query = select(Teacher).options(selectinload(Teacher.availabilities)).where(Teacher.id == teacher.id)
    result = await db.execute(query)
    teacher_loaded = result.scalar_one()

    return teacher_loaded


@router.get("/", response_model=List[TeacherSchema])
async def read_teachers(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 1. Defina a query usando 'select' (não db.query)
    # 2. Filtre por school_id (não owner_id)
    # 3. Use selectinload para evitar erro de "MissingGreenlet" nas disponibilidades
    query = (
        select(Teacher)
        .where(Teacher.school_id == current_user.school_id)  # Filtra pela escola do usuário logado
        .options(selectinload(Teacher.availabilities))  # Carrega os relacionamentos
        .offset(skip)
        .limit(limit)
    )

    # 4. Execute a query de forma assíncrona
    result = await db.execute(query)

    # 5. Retorne os escalares (os objetos Teacher)
    return result.scalars().all()