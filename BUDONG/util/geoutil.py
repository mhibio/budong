import math


def parse_wkt_point(wkt: str) -> tuple[float, float]:
    """
    WKT POINT 형식의 문자열을 파싱하여 (latitude, longitude)를 반환한다.
    예: "POINT(127.030 37.502)" → (37.502, 127.030)
    """
    if not wkt:
        raise ValueError("WKT 문자열이 비어 있습니다.")

    wkt = wkt.strip()

    if not wkt.upper().startswith("POINT("):
        raise ValueError(f"유효하지 않은 WKT POINT 형식입니다: {wkt}")

    # POINT(lon lat)
    inner = wkt[wkt.find("(") + 1 : wkt.find(")")]
    lon_str, lat_str = inner.split()

    lon = float(lon_str)
    lat = float(lat_str)

    return lat, lon


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 좌표(lat, lon) 사이의 거리를 미터 단위로 계산하는 Haversine 공식
    """
    R = 6371000  # 지구 반지름 (미터)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
