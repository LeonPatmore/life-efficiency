from unittest.mock import Mock

import pytest

from shopping.repeatingitems.shopping_repeating_items import RepeatingItems


@pytest.fixture
def repeating_items():
    repeating_items = RepeatingItems()
    repeating_items.add_repeating_item_impl = Mock()
    return repeating_items


def test_add_repeating_item_trims_whitespace(repeating_items):
    repeating_items.add_repeating_item(" some-item ")

    repeating_items.add_repeating_item_impl.assert_called_with("some-item")
