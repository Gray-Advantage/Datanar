__all__ = ("Period", "PeriodConverter")

from enum import auto, StrEnum


class Period(StrEnum):
    ALL_TIME = auto()
    YEAR = auto()
    MONTH = auto()
    DAY = auto()


class PeriodConverter:
    regex: str = "|".join(p.value for p in Period)

    def to_python(self, value: str) -> Period:
        return Period(value)

    def to_url(self, value: str | Period) -> str:
        if isinstance(value, Period):
            return value.value
        return value
