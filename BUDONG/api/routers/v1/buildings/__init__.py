from fastapi import APIRouter
from BUDONG.api.routers.v1.buildings import detail, get_reviews

router = APIRouter()

# 각 라우터 등록
router.include_router(detail.router, tags=["buildings"])
router.include_router(get_reviews.router, tags=["buildings"])
