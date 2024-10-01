from datetime import datetime

import pytest

from helpers.datetime import datetime_to_string, string_to_datetime


def test_datetime_to_string():
    some_datetime = datetime(2012, 3, 2, 5, 1, 2)
    string = datetime_to_string(some_datetime)

    assert string == "02/03/2012, 05:01:02"


@pytest.mark.parametrize("month", [10, 11, 12])
def test_datetime_to_string_with_double_digit_months(month: int):
    some_datetime = datetime(2012, month, 2, 5, 1, 2)
    string = datetime_to_string(some_datetime)

    assert string == f"02/{month}/2012, 05:01:02"


def test_string_to_datetime():
    test_string = "02/03/0001, 05:01:02"

    calculated_datetime = string_to_datetime(test_string)

    assert calculated_datetime.day == 2
    assert calculated_datetime.month == 3
    assert calculated_datetime.year == 1
    assert calculated_datetime.hour == 5
    assert calculated_datetime.minute == 1
    assert calculated_datetime.second == 2

    assert calculated_datetime.microsecond == 0
