from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import Field


# 요청 스키마
class UserRegister(BaseModel):
    email: str = Field(..., description="사용자 이메일")
    password: str = Field(..., description="사용자 비밀번호")
    nickname: str = Field(..., description="사용자 닉네임")


class UserLogin(BaseModel):
    email: str = Field(..., description="사용자 이메일")
    password: str = Field(..., description="사용자 비밀번호")


class PasswordUpdate(BaseModel):
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., description="새 비밀번호")


# 응답 스키마
class Token(BaseModel):
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field(..., description="토큰 타입")


class UserResponse(BaseModel):
    user_id: int = Field(..., description="사용자 ID")  
    email: str = Field(..., description="사용자 이메일")
    nickname: str = Field(..., description="사용자 닉네임")
    role: str = Field(..., description="사용자 역할")
    created_at: datetime = Field(..., description="사용자 생성 일시")
    
    class Config:
        from_attributes = True


class AuthCheckResponse(BaseModel):
    authenticated: bool = Field(..., description="인증 상태")
    user: Optional[UserResponse] = Field(..., description="사용자 정보")


class IsAdminResponse(BaseModel):
    is_admin: bool = Field(..., description="관리자 여부")

