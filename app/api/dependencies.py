from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# Define que o token deve ser enviado no header "Authorization: Bearer <token>"
# e aponta para a rota de login para obter o token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> User:
    """
    Decodifica o token JWT e busca o usuário no banco.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
            )
    except (JWTError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
        )

    # Busca o usuário no banco de forma assíncrona
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica se o usuário está ativo (opcional, se tiver campo is_active)
    """
    # Se você tiver um campo is_active no model, descomente abaixo:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user