import requests
from requests import codes

from functional.conftest import load_spreadsheet

_load_spreadsheet = load_spreadsheet

SHOPPING_ROOT = "https://67ylsh3ife.execute-api.eu-west-1.amazonaws.com/Dev"


def test_shopping_list_get(_load_spreadsheet):
    spreadsheet_helper = _load_spreadsheet

    spreadsheet_helper.set_list("item", 2)

    response = requests.get("{}/shopping/list".format(SHOPPING_ROOT))
    assert codes['ok'] == response.status_code
    assert ['item', 'item'] == response.json()['items']


def test_shopping_repeating_items(_load_spreadsheet):
    spreadsheet_helper = _load_spreadsheet

    spreadsheet_helper.set_repeating_items(["item-1", "item-2"])

    response = requests.get("{}/shopping/repeating".format(SHOPPING_ROOT))
    assert codes['ok'] == response.status_code
    assert ["item-2", "item-1"] == response.json()['items']


def test_shopping_repeating_items_already_present_returns_bad(_load_spreadsheet):
    spreadsheet_helper = _load_spreadsheet

    spreadsheet_helper.set_repeating_items(["item-1", "item-2"])

    response = requests.post("{}/shopping/repeating".format(SHOPPING_ROOT))
    assert codes['bad'] == response.status_code
