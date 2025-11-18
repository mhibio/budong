from fastapi import APIRouter
from BUDONG.api.routers.v1.auth import register, login, logout, auth_check, is_admin, update_password

router = APIRouter()

# 각 라우터 등록
router.include_router(register.router, tags=["auth"])
router.include_router(login.router, tags=["auth"])
router.include_router(logout.router, tags=["auth"])
router.include_router(auth_check.router, tags=["auth"])
router.include_router(is_admin.router, tags=["auth"])
router.include_router(update_password.router, tags=["auth"])

