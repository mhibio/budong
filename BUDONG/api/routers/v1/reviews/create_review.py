from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.core.auth import get_current_active_user
from BUDONG.api.models.models import TBuildingReview, TBuilding
from BUDONG.api.schemas.schema_reviews import ReviewCreate, ReviewResponse

router = APIRouter()

@router.post("/create", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)   
):
    building = db.query(TBuilding).filter(TBuilding.building_id == review.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    new_review = TBuildingReview(
        user_id=current_user.user_id,   
        building_id=review.building_id,
        rating=review.rating,
        content=review.content
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return ReviewResponse(
        success=True,
        review_id=new_review.review_idm,
        message="Review created successfully"
        )
