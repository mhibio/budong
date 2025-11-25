from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 1) 요청 (Request Body)
class ReviewFetchRequest(BaseModel):
    building_id: int

# 2) 개별 리뷰 데이터
class ReviewItem(BaseModel):
    review_id: int
    user_id: int
    building_id: int
    rating: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True  # ← SQLAlchemy model → Pydantic 변환 허용


# 3) 응답 (Response Body)
class ReviewListResponse(BaseModel):
    reviews: List[ReviewItem]
    total_count: int
class ReviewCreate(BaseModel):
    building_id: int
    rating: int
    content: str

class ReviewResponse(BaseModel):
    success: bool
    review_id: int
    message: str

