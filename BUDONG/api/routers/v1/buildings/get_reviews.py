# BUDONG/api/routers/v1/reviews/get_reviews.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from BUDONG.api.core.database import get_db
from BUDONG.api.schemas.schema_reviews import ReviewFetchRequest, ReviewListResponse
from BUDONG.api.models.models import TBuildingReview

router = APIRouter()  # ← THIS MUST EXIST

@router.post("/reviews", response_model=ReviewListResponse)
def get_reviews_by_building(request: ReviewFetchRequest, db: Session = Depends(get_db)):
    # 1) Fetch reviews
    reviews = db.query(TBuildingReview).filter(
        TBuildingReview.building_id == request.building_id
    ).all()

    if not reviews:
        raise HTTPException(status_code=404, detail="리뷰가 존재하지 않습니다.")

    # 2) Return response format
    return {
        "reviews": reviews,
        "total_count": len(reviews)
    }
