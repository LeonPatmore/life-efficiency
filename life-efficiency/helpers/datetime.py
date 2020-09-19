from datetime import datetime
from enum import Enum

DEFAULT_DATETIME_FORMAT = "%d/%m/%Y, %H:%M:%S"


class Day(Enum):

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def get_current_datetime_utc() -> datetime:
    return datetime.now()


def datetime_to_string(a_datetime: datetime, string_format: str = DEFAULT_DATETIME_FORMAT) -> str:
    return a_datetime.strftime(string_format)


def string_to_datetime(datetime_string: str, string_format: str = DEFAULT_DATETIME_FORMAT) -> datetime:
    return datetime.strptime(datetime_string, string_format)
