from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.schemas.schema_auth import Token, TokenWithRefresh
from BUDONG.api.core.auth import authenticate_user, create_access_token, create_refresh_token
from datetime import timedelta
from BUDONG.config import settings

router = APIRouter()


@router.post("/login", response_model=TokenWithRefresh, summary="OAuth2 로그인", description="OAuth2 표준 형식으로 로그인합니다. form-data 형식으로 username(이메일)과 password를 전송하세요.")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 표준 로그인 엔드포인트
    
    OAuth2 표준에 따라 form-data 형식으로 요청:
    - username: 사용자 이메일
    - password: 사용자 비밀번호
    
    응답:
    - access_token: 액세스 토큰 (짧은 만료 시간)
    - refresh_token: 리프레시 토큰 (긴 만료 시간)
    - token_type: "bearer"
    """
    # OAuth2 표준: form_data.username은 이메일로 사용
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    # 리프레시 토큰 생성
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.user_id), "email": user.email},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

