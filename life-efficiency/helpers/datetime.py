import datetime

DEFAULT_DATETIME_FORMAT = "%d/%m/%Y, %H:%M:%S"


def get_current_datetime_utc() -> datetime:
    return DatetimeCustom.now()


def datetime_to_string(a_datetime: datetime, string_format: str = DEFAULT_DATETIME_FORMAT) -> str:
    # TODO: This replacement is due to a bug on specific platforms that will not pad year 1 as 0001.
    return (a_datetime.strftime(string_format)
            .replace("/1", "/0001")
            .replace("00010", "10")
            .replace("00011", "11")
            .replace("00012", "12"))


def string_to_datetime(datetime_string: str, string_format: str = DEFAULT_DATETIME_FORMAT) -> datetime:
    return DatetimeCustom.strptime(datetime_string, string_format)


class DatetimeCustom(datetime.datetime):

    def to_json(self):
        return datetime_to_string(self)
