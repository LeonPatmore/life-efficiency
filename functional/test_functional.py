import os
import pathlib

import dotenv
import pytest
import requests
from requests import codes

ENV = os.environ.get("ENV", "local")
dotenv.load_dotenv(f"{pathlib.Path(__file__).parent.resolve()}/{ENV}.env")

URL_ROOT = os.environ.get("URL_ROOT")


@pytest.fixture
def cleanup():
    response = requests.get(f"{URL_ROOT}/shopping/list")
    for item in response.json()["items"]:
        delete_res = requests.delete(f"{URL_ROOT}/shopping/list", params={
            "quantity": item["quantity"],
            "name": item["name"]
        })
        assert delete_res.status_code == codes["ok"]


def test_shopping_list(cleanup):
    res = requests.post(f"{URL_ROOT}/shopping/list",
                        json={
                            "name": "Drink",
                            "quantity": 6
                        })
    assert res.status_code == codes["ok"]

    response = requests.get(f"{URL_ROOT}/shopping/list")
    assert codes['ok'] == response.status_code
    response_items = response.json()['items']
    assert 1 == len(response_items)
    assert "Drink" == response_items[0]["name"]
    assert 6 == response_items[0]["quantity"]


def _todo_item_exists(item_id: str) -> bool:
    return len(list(filter(lambda x: x["id"] == item_id, requests.get(f"{URL_ROOT}/todo/list").json()))) > 0


def test_todo_list():
    create_res = requests.post(f"{URL_ROOT}/todo/list",
                               json={
                                   "desc": "some cool todo"
                               })
    assert create_res.status_code == codes["ok"]
    todo_id = create_res.json()["id"]

    assert _todo_item_exists(todo_id)

    delete_res = requests.delete(f"{URL_ROOT}/todo/list/{todo_id}")
    assert delete_res.status_code == codes["ok"]

    assert not _todo_item_exists(todo_id)
