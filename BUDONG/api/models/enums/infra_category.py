from enum import Enum


class InfraCategory(str, Enum):
    SCHOOL = "school"
    PARK = "park"
    SUBWAY_STATION = "subway_station"
    BUS_STOP = "bus_stop"
    HOSPITAL = "hospital"
    MART = "mart"
    BANK = "bank"
    PUBLIC_OFFICE = "public_office"
    CCTV = "cctv"

