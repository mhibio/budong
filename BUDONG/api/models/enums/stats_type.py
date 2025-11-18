from enum import Enum


class StatsType(str, Enum):
    CRIME_TOTAL = "crime_total"
    CRIME_THEFT = "crime_theft"
    NOISE_DAY = "noise_day"
    NOISE_NIGHT = "noise_night"

