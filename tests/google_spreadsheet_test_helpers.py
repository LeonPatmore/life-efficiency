from unittest.mock import Mock


def generate_worksheet_mock(all_values: list, get_mock: Mock = None):
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = all_values
    if get_mock:
        worksheet_mock.get.return_value = get_mock
    return worksheet_mock
