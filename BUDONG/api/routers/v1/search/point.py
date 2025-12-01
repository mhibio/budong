from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import (
    TBuilding, TSchool, TStation, TPark
)
from BUDONG.api.schemas.schema_search import (
    SearchPointRequest,
    SearchPointResponse,
    SearchPointBuilding,
    SearchPointInfra
)
from BUDONG.util.geoutil import haversine

router = APIRouter()


@router.post("/point", response_model=SearchPointResponse)
def search_point(
    payload: SearchPointRequest,
    db: Session = Depends(get_db)
):

    lat = payload.latitude
    lon = payload.longitude
    radius = payload.radius_meters

    distance_expression = func.ST_Distance_Sphere(
        func.Point(TBuilding.lon, TBuilding.lat),  
        func.Point(lon, lat)
    )

    # 3. 쿼리 작성: 거리가 radius_m 이하인 항목의 cnt 합계를 구합니다.
    building_list = db.query(TBuilding).filter(distance_expression <= radius).all()

    result_buildings = [
        SearchPointBuilding(
            building_id=b.building_id,
            bjd_code=b.bjd_code,
            address=b.address,
            building_name=b.building_name,
            building_type=b.building_type,
            build_year=b.build_year,
            total_units=b.total_units,
            latitude=b.lat,
            longitude=b.lon
        )
        for b in building_list
    ]

    return SearchPointResponse(
        buildings=result_buildings,
        result_count=len(result_buildings)
    )
