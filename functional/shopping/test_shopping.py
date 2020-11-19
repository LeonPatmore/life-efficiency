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
