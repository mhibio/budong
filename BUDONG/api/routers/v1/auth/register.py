from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.schemas.schema_auth import UserRegister, UserResponse
from BUDONG.api.core.auth import get_password_hash
from BUDONG.api.models.enums.user_role import UserRole

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    회원가입
    """
    # 이메일 중복 확인
    existing_user = db.query(TUser).filter(TUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 닉네임 중복 확인
    existing_nickname = db.query(TUser).filter(TUser.nickname == user_data.nickname).first()
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 닉네임입니다."
        )
    
    # 새 사용자 생성
    new_user = TUser(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        nickname=user_data.nickname,
        role=UserRole.USER.value
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

