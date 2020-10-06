from datetime import datetime
from unittest.mock import Mock

import pytest

from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.predictor.shopping_predictor import ShoppingPredictor
from shopping.shopping_items import PESTO

CURRENT_DAY = 10


def _datetime_from_day(day: int) -> datetime:
    return datetime(2012, 5, day, 0, 0, 0, 0)


@pytest.fixture
def setup_shopping_predictor(request):
    history_mock = Mock()
    shopping_predictor = ShoppingPredictor(history_mock, lambda: _datetime_from_day(CURRENT_DAY))
    history_mock.get_purchases_for_item.return_value = request.param
    return shopping_predictor


_setup_shopping_predictor = setup_shopping_predictor


@pytest.mark.parametrize('_setup_shopping_predictor', [[]], indirect=True)
def test_should_buy_today_when_no_items_return_false(_setup_shopping_predictor):
    assert not _setup_shopping_predictor.should_buy_today(PESTO)


@pytest.mark.parametrize('_setup_shopping_predictor', [[ShoppingItemPurchase(PESTO, 1)]], indirect=True)
def test_should_buy_today_when_one_item_return_false(_setup_shopping_predictor):
    assert not _setup_shopping_predictor.should_buy_today(PESTO)


@pytest.mark.parametrize('_setup_shopping_predictor',
                         [[ShoppingItemPurchase(PESTO, 1, _datetime_from_day(9)),
                           ShoppingItemPurchase(PESTO, 1, _datetime_from_day(5))]],
                         indirect=True)
def test_should_buy_today_when_two_item_recent_return_false(_setup_shopping_predictor):
    assert not _setup_shopping_predictor.should_buy_today(PESTO)


@pytest.mark.parametrize('_setup_shopping_predictor',
                         [[ShoppingItemPurchase(PESTO, 1, _datetime_from_day(6)),
                           ShoppingItemPurchase(PESTO, 1, _datetime_from_day(2))]],
                         indirect=True)
def test_should_buy_today_when_two_item_not_recent_return_true(_setup_shopping_predictor):
    assert _setup_shopping_predictor.should_buy_today(PESTO)


@pytest.mark.parametrize('_setup_shopping_predictor',
                         [[ShoppingItemPurchase(PESTO, 1, _datetime_from_day(7)),
                           ShoppingItemPurchase(PESTO, 1, _datetime_from_day(3))]],
                         indirect=True)
def test_should_buy_today_when_two_item_buy_for_tomorrow(_setup_shopping_predictor):
    assert _setup_shopping_predictor.should_buy_today(PESTO)
