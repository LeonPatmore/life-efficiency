from datetime import datetime

import requests
from requests import codes

SHOPPING_ROOT = "https://67ylsh3ife.execute-api.eu-west-1.amazonaws.com/Dev"
EXAMPLE_DATETIME = datetime(2023, 5, 29, 11, 9, 16)


def test_shopping_list_get(load_spreadsheet):
    spreadsheet_helper = load_spreadsheet

    spreadsheet_helper.set_list("item", 2, EXAMPLE_DATETIME)

    response = requests.get(f"{SHOPPING_ROOT}/shopping/list")
    assert codes['ok'] == response.status_code
    assert [{'date_added': '2023-05-29 11:09:16', 'name': 'item', 'quantity': 2}] == response.json()['items']


def test_shopping_repeating_items(load_spreadsheet):
    spreadsheet_helper = load_spreadsheet

    spreadsheet_helper.set_repeating_items(["item-1", "item-2"])

    response = requests.get(f"{SHOPPING_ROOT}/shopping/repeating")
    assert codes['ok'] == response.status_code
    assert ["item-2", "item-1"] == response.json()['items']


def test_shopping_repeating_items_already_present_returns_bad(load_spreadsheet):
    spreadsheet_helper = load_spreadsheet

    spreadsheet_helper.set_repeating_items(["item-1", "item-2"])

    response = requests.post(f"{SHOPPING_ROOT}/shopping/repeating",
                             json={"item": "item-1"})
    assert codes['bad'] == response.status_code
    assert "repeating item `item-1` already present" == response.json()["error"]


def test_add_to_shopping_list(load_spreadsheet):
    spreadsheet_helper = load_spreadsheet
    spreadsheet_helper.clear_list()

    response = requests.post(f"{SHOPPING_ROOT}/shopping/list",
                             json={"name": "Drink", "quantity": 3})

    assert response.status_code == 200
