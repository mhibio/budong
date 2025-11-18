from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.core.auth import get_current_active_user
from BUDONG.api.schemas.schema_auth import AuthCheckResponse, UserResponse

router = APIRouter()


@router.get("/auth_check", response_model=AuthCheckResponse)
async def auth_check(
    current_user: TUser = Depends(get_current_active_user)
):
    """
    인증 상태 확인
    """
    return {
        "authenticated": True,
        "user": UserResponse(
            user_id=current_user.user_id,
            email=current_user.email,
            nickname=current_user.nickname,
            role=current_user.role,
            created_at=current_user.created_at
        )
    }

