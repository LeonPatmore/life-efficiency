from unittest.mock import Mock


def generate_worksheet_mock(all_values: list, get_first=None):
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = all_values
    if get_first:
        get_mock = Mock()
        get_mock.first.return_value = get_first
        worksheet_mock.get.return_value = get_mock
    return worksheet_mock
