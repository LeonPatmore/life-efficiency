import pytest
import requests
from requests import codes

SHOPPING_ROOT = "https://67ylsh3ife.execute-api.eu-west-1.amazonaws.com/Dev"


@pytest.fixture
def cleanup():
    response = requests.get(f"{SHOPPING_ROOT}/shopping/list")
    for item in response.json()["items"]:
        delete_res = requests.delete(f"{SHOPPING_ROOT}/shopping/list", params={
            "quantity": item["quantity"],
            "name": item["name"]
        })
        assert delete_res.status_code == codes["ok"]


def test_shopping_list(cleanup):
    res = requests.post(f"{SHOPPING_ROOT}/shopping/list",
                        json={
                            "name": "Drink",
                            "quantity": 6
                        })
    assert res.status_code == codes["ok"]

    response = requests.get(f"{SHOPPING_ROOT}/shopping/list")
    assert codes['ok'] == response.status_code
    response_items = response.json()['items']
    assert 1 == len(response_items)
    assert "Drink" == response_items[0]["name"]
    assert 6 == response_items[0]["quantity"]
