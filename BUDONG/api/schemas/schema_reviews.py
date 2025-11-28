# BUDONG/api/schemas/schema_reviews.py

from pydantic import BaseModel
from typing import List
from datetime import datetime


# --- 요청(Request) ---
class ReviewFetchRequest(BaseModel):
    building_id: int

class ReviewCreate(BaseModel):
    building_id: int
    rating: int
    content: str


# --- 응답(Response) ---

# 개별 리뷰 (SQLAlchemy → Pydantic 변환 허용)
class ReviewItem(BaseModel):
    review_id: int
    user_id: int
    building_id: int
    rating: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


# 리뷰 목록 응답
class ReviewListResponse(BaseModel):
    reviews: List[ReviewItem]
    total_count: int


# 리뷰 생성 응답
class ReviewResponse(BaseModel):
    success: bool
    review_id: int
    message: str
