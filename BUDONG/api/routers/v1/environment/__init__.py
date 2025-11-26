from fastapi import APIRouter
from BUDONG.api.routers.v1.environment import get_environment_data

router = APIRouter()

# 각 라우터 등록
router.include_router(get_environment_data.router, tags=["environment"])