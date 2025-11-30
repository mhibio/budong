from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TUser
from BUDONG.api.schemas.schema_auth import TokenWithRefresh, RefreshTokenRequest
from BUDONG.api.core.auth import verify_token, create_access_token, create_refresh_token
from datetime import timedelta
from BUDONG.config import settings

router = APIRouter()


@router.post("/refresh", response_model=TokenWithRefresh, summary="토큰 갱신", description="리프레시 토큰을 사용하여 새로운 액세스 토큰과 리프레시 토큰을 발급받습니다.")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    OAuth2 리프레시 토큰을 사용하여 새로운 토큰 발급
    
    요청:
    {
        "refresh_token": "your_refresh_token_here"
    }
    
    응답:
    - access_token: 새로운 액세스 토큰
    - refresh_token: 새로운 리프레시 토큰
    - token_type: "bearer"
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="리프레시 토큰이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 리프레시 토큰 검증
    payload = verify_token(refresh_data.refresh_token)
    if payload is None:
        raise credentials_exception
    
    # 토큰 타입 확인 (refresh token만 허용)
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 정보 추출
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 사용자 확인
    user = db.query(TUser).filter(TUser.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # 새로운 액세스 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        #data={"sub": user.user_id, "email": user.email, "role": user.role},
        data={"sub": str(user.user_id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    # 새로운 리프레시 토큰 생성
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

