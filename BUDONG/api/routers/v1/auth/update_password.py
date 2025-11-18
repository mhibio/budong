from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.core.auth import get_current_active_user, verify_password, get_password_hash
from BUDONG.api.schemas.schema_auth import PasswordUpdate

router = APIRouter()


@router.post("/update_password", status_code=status.HTTP_200_OK)
async def update_password(
    password_data: PasswordUpdate,
    current_user: TUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경
    """
    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다."
        )
    
    # 새 비밀번호 해싱 및 업데이트
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {
        "message": "비밀번호가 성공적으로 변경되었습니다."
    }

