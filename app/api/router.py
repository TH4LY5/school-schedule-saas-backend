from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    teachers,
    classes,
    schedules,
    schools,
    subjects,
    constraints
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
# --- 2. Adicione esta linha ---
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(constraints.router, prefix="/constraints", tags=["constraints"])