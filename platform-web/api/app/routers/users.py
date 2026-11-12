from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import User
from app.schemas.user import MeResponse

router = APIRouter(tags=["users"])


@router.get("/me", response_model=MeResponse)
async def get_me(user: User = Depends(get_current_user)) -> User:
    return user
