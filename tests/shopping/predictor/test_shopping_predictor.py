from datetime import datetime

import pytest

from shopping.history.shopping_history import ShoppingItemPurchase
from shopping.predictor.shopping_predictor import ShoppingPredictor

CURRENT_DAY = 10
PESTO = "pesto"


def _datetime_from_day(day: int) -> datetime:
    return datetime(2012, 5, day, 0, 0, 0, 0)


@pytest.fixture
def setup_shopping_predictor(request):
    shopping_predictor = ShoppingPredictor(request.param, _datetime_from_day(CURRENT_DAY))
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
