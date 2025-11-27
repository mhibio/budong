from fastapi import APIRouter
from BUDONG.api.routers.v1.infrastructure import category

router = APIRouter()

# 각 라우터 등록
router.include_router(category.router, tags=["infrastructure"])