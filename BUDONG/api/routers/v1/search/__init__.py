from fastapi import APIRouter
from BUDONG.api.routers.v1.search import point

router = APIRouter()

# 각 라우터 등록
router.include_router(point.router, tags=["search"])
