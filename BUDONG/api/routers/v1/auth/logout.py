from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.core.auth import get_current_active_user
from BUDONG.api.schemas.schema_auth import UserResponse

router = APIRouter()


@router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout(
    current_user: TUser = Depends(get_current_active_user)
):
    """
    로그아웃
    주의: JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없습니다.
    클라이언트에서 토큰을 삭제해야 합니다.
    향후 Redis 등을 사용하여 토큰 블랙리스트를 관리할 수 있습니다.
    """
    # 현재는 단순히 성공 응답만 반환
    # 향후 Redis 등을 사용하여 토큰 블랙리스트 관리 가능
    return {
        "message": "로그아웃되었습니다.",
        "user_id": current_user.user_id
    }

