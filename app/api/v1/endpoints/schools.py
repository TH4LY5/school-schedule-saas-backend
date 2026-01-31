from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import dependencies as deps
from app.models.school import School
from app.schemas.school_schemas import SchoolCreate, SchoolRead

router = APIRouter()

@router.post("/", response_model=SchoolRead)
async def create_school(
    school_in: SchoolCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    school = School(
        name=school_in.name,
        address=school_in.address,
        owner_id=current_user.id
    )
    db.add(school)
    await db.commit()
    await db.refresh(school)
    return school

@router.get("/", response_model=List[SchoolRead])
async def read_schools(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user)
):
    result = await db.execute(
        select(School).filter(School.owner_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()