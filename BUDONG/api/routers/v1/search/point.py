from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import TBuilding, TSchool
from BUDONG.api.schemas.schema_search import (
    SearchPointRequest,
    SearchPointResponse,
    SearchPointBuilding,
    SearchPoinTSchool
)
from BUDONG.util.geoutil import parse_wkt_point, haversine

router = APIRouter()


@router.post("/point", response_model=SearchPointResponse)
def search_point(
    payload: SearchPointRequest,
    db: Session = Depends(get_db)
):

    lat = payload.latitude
    lon = payload.longitude
    radius = payload.radius_meters

    buildings = db.query(TBuilding).all()
    infra_list = db.query(TSchool).all()

    result_buildings = []
    result_infra = []

    # 건물 거리 계산
    for b in buildings:
        b_lat, b_lon = parse_wkt_point(b.location)
        dist = haversine(lat, lon, b_lat, b_lon)

        if dist <= radius:
            result_buildings.append(
                SearchPointBuilding(
                    building_id=b.building_id,
                    bjd_code=b.bjd_code,
                    address=b.address,
                    building_name=b.building_name,
                    building_type=b.building_type,
                    build_year=b.build_year,
                    total_units=b.total_units,
                    latitude=b_lat,
                    longitude=b_lon
                )
            )

    # 인프라 거리 계산
    for i in infra_list:
        i_lat, i_lon = parse_wkt_point(i.location)
        dist = haversine(lat, lon, i_lat, i_lon)

        if dist <= radius:
            result_infra.append(
                SearchPoinTSchool(
                    infra_id=i.infra_id,
                    infra_category=i.infra_category,
                    name=i.name,
                    address=i.address,
                    latitude=i_lat,
                    longitude=i_lon,
                )
            )

    return SearchPointResponse(
        buildings=result_buildings,
        infrastructure=result_infra,
        search_radius=radius,
        result_count=len(result_buildings) + len(result_infra)
    )
