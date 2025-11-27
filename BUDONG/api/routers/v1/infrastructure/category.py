from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from BUDONG.api.core.database import get_db
from BUDONG.api.exception.global_exception_handler import APIError
from BUDONG.api.models.models import TInfrastructure
from BUDONG.api.schemas.schema_infrastructure import (
    InfrastructureCategoryRequest,
    InfrastructureItem,
    InfrastructureResponse,
)
from BUDONG.util.geoutil import parse_wkt_point, haversine

router = APIRouter()

# 허용된 카테고리 목록
VALID_CATEGORIES = {
    "school",
    "park",
    "subway_station",
    "bus_stop",
    "hospital",
    "mart",
    "bank",
    "public_office",
    "cctv",
}


@router.post("/category", response_model=InfrastructureResponse)
def search_infrastructure_by_category(
    payload: InfrastructureCategoryRequest,
    db: Session = Depends(get_db)
):
    category = payload.category
    lat = payload.latitude
    lon = payload.longitude
    radius = payload.radius_meters

    # 1) 카테고리 검증
    if category not in VALID_CATEGORIES:
        raise APIError(
            code="INVALID_CATEGORY",
            message=f"'{category}'는 지원하지 않는 카테고리입니다.",
            status_code=400,
        )

    # 2) DB에서 해당 카테고리 인프라 SELECT
    infra_list = (
        db.query(TInfrastructure)
        .filter(TInfrastructure.infra_category == category)
        .all()
    )

    if not infra_list:
        return InfrastructureResponse(infrastructure=[])

    # 3) 거리 기반 필터링 (haversine)
    result = []
    for infra in infra_list:
        i_lat, i_lon = parse_wkt_point(infra.location)
        distance = haversine(lat, lon, i_lat, i_lon)

        if distance <= radius:
            result.append(
                InfrastructureItem(
                    infra_id=infra.infra_id,
                    infra_category=infra.infra_category,
                    name=infra.name,
                    address=infra.address,
                    latitude=i_lat,
                    longitude=i_lon,
                )
            )

    return InfrastructureResponse(infrastructure=result)
