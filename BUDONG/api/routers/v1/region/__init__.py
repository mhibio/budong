from fastapi import APIRouter
from BUDONG.api.routers.v1.region import get_region_stats

router = APIRouter()

# 각 라우터 등록
router.include_router(get_region_stats.router, tags=["environment"])