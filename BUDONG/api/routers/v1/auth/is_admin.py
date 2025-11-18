from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.core.auth import get_current_admin_user
from BUDONG.api.schemas.schema_auth import IsAdminResponse

router = APIRouter()


@router.get("/is_admin", response_model=IsAdminResponse)
async def is_admin(
    current_user: TUser = Depends(get_current_admin_user)
):
    """
    관리자 권한 확인
    """
    return {
        "is_admin": True
    }

