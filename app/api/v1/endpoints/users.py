from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.core import security

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(
        *,
        db: AsyncSession = Depends(get_db),
        user_in: UserCreate
) -> Any:
    """
    Cria um novo usuário.
    """
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este email já existe no sistema.",
        )

    db_obj = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role,
        school_id=user_in.school_id,
        tenant_id=user_in.school_id if user_in.school_id else None
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
