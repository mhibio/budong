from fastapi import APIRouter
from BUDONG.api.routers.v1.reviews import create_review

router = APIRouter()

# 각 라우터 등록
router.include_router(create_review.router, tags=["reviews"])