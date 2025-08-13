from __future__ import annotations
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_token, is_access
from app.db.session import get_session
from app.repositories.user_repo import get_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # для Swagger

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
):
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not is_access(payload):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")

    user_id = int(payload["sub"])
    user = await get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    request.state.user = user
    return user

def require_admin(current_user = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "admin":
        # у нас role — Enum в моделях, но в объекте будет .role.value == 'admin'
        if getattr(current_user.role, "value", None) != "admin":
            raise HTTPException(status_code=403, detail="Admin only")
    return current_user

def require_roles(*roles: str):
    """
    Зависимость FastAPI: пропускает только пользователей с одной из указанных ролей.
    Пример использования:
      @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
    """
    async def _checker(current_user = Depends(get_current_user)):
        role_val = getattr(current_user.role, "value", current_user.role)
        if role_val not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return _checker