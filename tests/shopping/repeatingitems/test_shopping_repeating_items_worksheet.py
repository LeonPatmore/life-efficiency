from unittest.mock import Mock

import pytest

from shopping.repeatingitems.shopping_repeating_items_worksheet import RepeatingItemsWorksheet, \
    RepeatingItemsAlreadyPresent

ALL_VALUES = ["item-1", "item-2", "item-3"]


@pytest.fixture
def generate_repeating_items_worksheet():
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = list(map(lambda x: [x], ALL_VALUES))
    repeating_items_worksheet = RepeatingItemsWorksheet(worksheet_mock)
    return worksheet_mock, repeating_items_worksheet


def test_get_repeating_items(generate_repeating_items_worksheet):
    _, repeating_items_worksheet = generate_repeating_items_worksheet
    items = repeating_items_worksheet.get_repeating_items()
    assert items == ALL_VALUES


def test_add_repeating_item(generate_repeating_items_worksheet):
    worksheet_mock, repeating_items_worksheet = generate_repeating_items_worksheet
    repeating_items_worksheet.add_repeating_item("item-4")
    worksheet_mock.insert_row.assert_called_once_with(["item-4"], 1)


def test_add_repeating_item_already_present_raises_exception(generate_repeating_items_worksheet):
    worksheet_mock, repeating_items_worksheet = generate_repeating_items_worksheet

    with pytest.raises(RepeatingItemsAlreadyPresent):
        repeating_items_worksheet.add_repeating_item("item-3")
    worksheet_mock.insert_row.assert_not_called()
