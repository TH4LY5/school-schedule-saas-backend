from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.constraint import Constraint
from app.schemas.school_schemas import ConstraintSchema, ConstraintCreate

router = APIRouter()


# Schema local para simplificar (ou mova para school_schemas.py)



@router.post("/", response_model=ConstraintSchema, status_code=status.HTTP_201_CREATED)
async def create_constraint(
        constraint_in: ConstraintCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_constraint = Constraint(
        type=constraint_in.type,
        data=constraint_in.data,
        school_id=current_user.school_id
    )
    db.add(new_constraint)
    await db.commit()
    await db.refresh(new_constraint)
    return new_constraint


@router.get("/", response_model=List[ConstraintSchema])
async def read_constraints(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(Constraint).where(Constraint.school_id == current_user.school_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constraint(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(Constraint).where(Constraint.id == id, Constraint.school_id == current_user.school_id)
    result = await db.execute(query)
    constraint = result.scalar_one_or_none()
    if not constraint:
        raise HTTPException(status_code=404, detail="Not found")

    await db.delete(constraint)
    await db.commit()