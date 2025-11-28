# BUDONG/api/routers/v1/reviews/create_review.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from BUDONG.api.core.database import get_db
from BUDONG.api.schemas.schema_reviews import ReviewCreate, ReviewResponse
from BUDONG.api.models.models import TBuildingReview, TBuilding

router = APIRouter()

@router.post("/create", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    # 1) Check if building exists
    building = db.query(TBuilding).filter(TBuilding.building_id == review.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="건물을 찾을 수 없습니다.")

    # 2) Temporary user_id (No login yet)
    new_review = TBuildingReview(
        user_id=1,  # 👈 Temporary solution (Fix later)
        building_id=review.building_id,
        rating=review.rating,
        content=review.content
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return ReviewResponse(
        success=True,
        review_id=new_review.review_id,
        message="리뷰가 등록되었습니다."
    )
