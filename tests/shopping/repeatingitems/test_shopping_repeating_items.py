from unittest.mock import Mock

import pytest

from shopping.repeatingitems.shopping_repeating_items import RepeatingItems, RepeatingItem


@pytest.fixture
def repeating_items():
    repeating_items = RepeatingItems()
    repeating_items.add = Mock()
    return repeating_items


def test_add_repeating_item_trims_whitespace(repeating_items):
    repeating_items.add(RepeatingItem(" some-item "))

    # noinspection PyUnresolvedReferences
    repeating_items.add.assert_called_with(RepeatingItem("some-item"))
