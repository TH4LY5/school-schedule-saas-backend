from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.models.class_group import ClassGroup
from app.models.subject import Subject
from app.schemas.school_schemas import ClassGroupCreate, ClassGroupRead, ClassGroupSchema
from app.api import dependencies
router = APIRouter()


@router.post("/", response_model=ClassGroupSchema)
async def create_class_group(
        class_in: ClassGroupCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Verifica o school_id
    school_id_to_use = class_in.school_id
    if not school_id_to_use and hasattr(current_user, 'school_id'):
        school_id_to_use = current_user.school_id

    db_class = ClassGroup(
        name=class_in.name,
        grade=class_in.grade,  # Agora o modelo aceita este campo
        shift=class_in.shift,  # Se você adicionou turno
        school_id=school_id_to_use  # Multi-tenant correto
        # owner_id=current_user.id <-- REMOVA ESTA LINHA se existir
    )

    db.add(db_class)
    await db.commit()
    await db.refresh(db_class)
    return db_class