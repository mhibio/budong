from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# -------------------------
# 요청 파라미터 
# -------------------------
class BuildingRequest(BaseModel):
    building_id: int = Field(..., description="빌딩id")


# -------------------------
# Building 기본 정보
# -------------------------
class BuildingDetail(BaseModel):
    building_id: int
    bjd_code: Optional[int]
    address: Optional[str]
    building_name: Optional[str]
    building_type: Optional[str]
    build_year: Optional[str]
    total_units: Optional[str]
    latitude: float
    longitude: float


# -------------------------
# 거래 정보
# -------------------------
class BuildingTransaction(BaseModel):
    tx_id: int
    building_id: int
    transaction_date: Optional[str]  # DB가 문자열 날짜를 가짐
    price: int
    area_sqm: Optional[float]
    floor: Optional[float]


# -------------------------
# 리뷰 정보
# -------------------------
class BuildingReview(BaseModel):
    review_id: int
    user_id: int
    building_id: int
    rating: int
    content: Optional[str]
    created_at: datetime


# -------------------------
# 주변 인프라 정보
# (학교/공원/지하철/경찰서 등 모두 합쳐서 반환)
# -------------------------
class NearbyInfrastructure(BaseModel):
    infra_id: str  # 공원 PK(문자열)도 포함해야 해서 str 처리
    infra_category: str  # "school", "park", "subway_station", "public_office", "cctv"
    name: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    extra_data: Optional[dict] = None  # 범죄지표, CCTV수 등 추가정보


# -------------------------
# 지역 통계 (부활 버전)
# - 자치구 단위 범죄/치안
# - 행정동 단위 대중교통 복잡도
# -------------------------
class RegionStat(BaseModel):
    region_name: Optional[str]  # 자치구명 또는 행정동명
    crime_num: Optional[int]
    cctv_num: Optional[int]
    dangerous_rating: Optional[int]
    cctv_security_rating: Optional[int]


# -------------------------
# 환경 데이터 (TNoise 기반)
# -------------------------
class EnvironmentData(BaseModel):
    address: Optional[str]
    noise_max: Optional[int]
    noise_avg: Optional[int]
    noise_min: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]


# -------------------------
# 최종 응답 구조
# -------------------------
class BuildingDetailResponse(BaseModel):
    building: BuildingDetail
    transactions: List[BuildingTransaction]
    reviews: List[BuildingReview]
    nearby_infrastructure: List[NearbyInfrastructure]
    region_stats: List[RegionStat]
    environment_data: List[EnvironmentData]
