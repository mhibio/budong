from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import (
    TBuilding,
    TRealTransactionPrice,
    TBuildingReview,
    TSchool,
    TRegionStats,
    TStation,
    TNoise,
)

from BUDONG.api.schemas.schema_buildings import (
    BuildingRequest,
    BuildingDetailResponse,
    BuildingDetail,
    BuildingTransaction,
    BuildingReview,
    NearbyInfrastructure,
    RegionStat,
    EnvironmentData,
)

from BUDONG.util.geoutil import parse_wkt_point, haversine


router = APIRouter()


@router.post("/detail", response_model=BuildingDetailResponse)
def get_building_detail(
    payload: BuildingRequest, 
    db: Session = Depends(get_db)
):

    building_id = payload.building_id
    if not building_id:
        raise HTTPException(status_code=400, detail="building_id is required")

    # -------------------------
    # 1. 건물 정보
    # -------------------------
    building = (
        db.query(TBuilding)
        .filter(TBuilding.building_id == building_id)
        .first()
    )
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    # building.location → POINT(lon lat)
    b_lat, b_lon = parse_wkt_point(building.location)

    building_schema = BuildingDetail(
        building_id=building.building_id,
        bjd_code=building.bjd_code,
        address=building.address,
        building_name=building.building_name,
        building_type=building.building_type,
        build_year=building.build_year,
        total_units=building.total_units,
        latitude=b_lat,
        longitude=b_lon,
    )

    # -------------------------
    # 2. 거래 정보
    # -------------------------
    tx_list = (
        db.query(TRealTransactionPrice)
        .filter(TRealTransactionPrice.building_id == building_id)
        .all()
    )

    transactions_schema = [
        BuildingTransaction(
            tx_id=tx.tx_id,
            building_id=tx.building_id,
            transaction_date=tx.transaction_date,
            price=tx.price,
            area_sqm=float(tx.area_sqm),
            floor=tx.floor,
        )
        for tx in tx_list
    ]

    # -------------------------
    # 3. 리뷰
    # -------------------------
    review_list = (
        db.query(TBuildingReview)
        .filter(TBuildingReview.building_id == building_id)
        .all()
    )

    reviews_schema = [
        BuildingReview(
            review_id=r.review_id,
            user_id=r.user_id,
            building_id=r.building_id,
            rating=r.rating,
            content=r.content,
            created_at=r.created_at,
        )
        for r in review_list
    ]

    # -------------------------
    # 4. 주변 인프라 (주변 500m)
    # -------------------------
    INFRA_RADIUS_M = 500
    infra_schema = []

    all_infra = db.query(TSchool).all()

    for infra in all_infra:
        i_lat, i_lon = parse_wkt_point(infra.location)
        distance = haversine(b_lat, b_lon, i_lat, i_lon)

        if distance <= INFRA_RADIUS_M:
            infra_schema.append(
                NearbyInfrastructure(
                    infra_id=infra.infra_id,
                    infra_category=infra.infra_category,
                    name=infra.name,
                    address=infra.address,
                    latitude=i_lat,
                    longitude=i_lon,
                )
            )

    # -------------------------
    # 5. 지역 통계 (bjd_code 기준)
    # -------------------------
    stats_list = (
        db.query(TRegionStats)
        .filter(TRegionStats.bjd_code == building.bjd_code)
        .all()
    )

    stats_schema = [
        RegionStat(
            stats_id=s.stats_id,
            bjd_code=s.bjd_code,
            stats_year=s.stats_year,
            stats_type=s.stats_type,
            stats_value=s.stats_value,
        )
        for s in stats_list
    ]

    # -------------------------
    # 6. 환경 데이터 (가장 가까운 측정소 기반)
    # -------------------------
    stations = db.query(TStation).all()

    nearest_station = None
    nearest_distance = float("inf")

    for st in stations:
        st_lat, st_lon = parse_wkt_point(st.location)
        dist = haversine(b_lat, b_lon, st_lat, st_lon)

        if dist < nearest_distance:
            nearest_distance = dist
            nearest_station = st

    if nearest_station is None:
        env_schema = []
    else:
        env_list = (
            db.query(TNoise)
            .filter(TNoise.station_id == nearest_station.station_id)
            .all()
        )

        env_schema = [
            EnvironmentData(
                data_id=e.data_id,
                station_id=e.station_id,
                measurement_time=e.measurement_time,
                pm10_value=e.pm10_value,
                pm2_5_value=e.pm2_5_value,
                noise_db=float(e.noise_db),
            )
            for e in env_list
        ]

    # -------------------------
    # 최종 반환
    # -------------------------
    return BuildingDetailResponse(
        building=building_schema,
        transactions=transactions_schema,
        reviews=reviews_schema,
        nearby_infrastructure=infra_schema,
        region_stats=stats_schema,
        environment_data=env_schema,
    )
