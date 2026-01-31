from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.subject import Subject
from app.schemas.school_schemas import SubjectCreate, SubjectSchema

router = APIRouter()


@router.post("/", response_model=SubjectSchema, status_code=status.HTTP_201_CREATED)
async def create_subject(
        subject_in: SubjectCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova disciplina vinculada à escola do usuário.
    """
    new_subject = Subject(
        name=subject_in.name,
        school_id=current_user.school_id,  # Vínculo automático com a escola
        # Copia os outros campos do schema (weekly_lessons, etc)
        weekly_lessons=subject_in.weekly_lessons,
        max_daily_lessons=subject_in.max_daily_lessons,
        allow_consecutive=subject_in.allow_consecutive,
        teacher_id=subject_in.teacher_id,
        class_group_id=subject_in.class_group_id
    )

    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)
    return new_subject


@router.get("/", response_model=List[SubjectSchema])
async def read_subjects(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lista todas as disciplinas da escola.
    """
    query = select(Subject).where(Subject.school_id == current_user.school_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
        subject_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Remove uma disciplina.
    """
    query = select(Subject).where(Subject.id == subject_id, Subject.school_id == current_user.school_id)
    result = await db.execute(query)
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    await db.delete(subject)
    await db.commit()