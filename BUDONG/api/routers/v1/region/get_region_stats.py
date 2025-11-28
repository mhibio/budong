from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from BUDONG.api.core.database import get_db
from BUDONG.api.schemas.schema_region import (
    RegionStatsResponse,
    RegionStatsItem,
    RegionInfo
)

router = APIRouter()


@router.get("/stats", response_model=RegionStatsResponse)
def get_region_stats(
    bjd_code: str = Query(..., description="법정동 코드"),
    db: Session = Depends(get_db)
):

    # 지역 정보 조회
    region = (
        db.query(TRegion)
        .filter(TRegion.bjd_code == bjd_code)
        .first()
    )

    if region is None:
        raise HTTPException(status_code=404, detail="지역 정보를 찾을 수 없습니다.")

    region_schema = RegionInfo(
        bjd_code=region.bjd_code,
        region_name_full=region.region_name_full
    )

    # 통계 데이터 조회
    stats = (
        db.query(TRegionStats)
        .filter(TRegionStats.bjd_code == bjd_code)
        .order_by(TRegionStats.stats_year.desc())
        .all()
    )

    stats_schema = [
        RegionStatsItem(
            stats_id=s.stats_id,
            bjd_code=s.bjd_code,
            stats_year=s.stats_year,
            stats_type=s.stats_type,
            stats_value=float(s.stats_value)
        )
        for s in stats
    ]

    return RegionStatsResponse(
        region_stats=stats_schema,
        region=region_schema
    )
