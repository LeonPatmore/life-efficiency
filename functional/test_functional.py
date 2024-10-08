import os
import pathlib

import dotenv
import pytest
import requests
from requests import codes

ENV = os.environ.get("ENV", "local")
dotenv.load_dotenv(f"{pathlib.Path(__file__).parent.resolve()}/{ENV}.env")

URL_ROOT = os.environ.get("URL_ROOT")


def _cleanup_list():
    response = requests.get(f"{URL_ROOT}/shopping/list")
    for item in response.json():
        delete_res = requests.delete(f"{URL_ROOT}/shopping/list", params={
            "quantity": item["quantity"],
            "name": item["name"]
        })
        assert delete_res.status_code == codes["ok"]


@pytest.fixture
def cleanup():
    _cleanup_list()
    yield
    _cleanup_list()


def test_shopping_list(cleanup):
    res = requests.post(f"{URL_ROOT}/shopping/list",
                        json={
                            "name": "Drink",
                            "quantity": 6
                        })
    assert res.status_code == codes["ok"]

    response = requests.get(f"{URL_ROOT}/shopping/list")
    assert codes['ok'] == response.status_code
    response_items = response.json()
    assert 1 == len(response_items)
    assert "drink" == response_items[0]["name"]
    assert 6 == response_items[0]["quantity"]


def test_add_to_shopping_history(cleanup):
    res = requests.post(f"{URL_ROOT}/shopping/history",
                        json={
                            "name": "Drink",
                            "quantity": 6
                        })
    assert res.status_code == codes["ok"]


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


def test_balance_instance():
    create_res = requests.post(f"{URL_ROOT}/finance/instances",
                               json={
                                   "amount": 1000.0,
                                   "date": "21/08/2024, 13:00:00",
                                   "holder": "bank"
                               })
    assert create_res.status_code == codes["ok"]
    instance_id = create_res.json()["id"]

    assert len(list(filter(lambda x: x["id"] == instance_id, requests.get(f"{URL_ROOT}/finance/instances").json()))) > 0


def test_balance_changes():
    create_res = requests.post(f"{URL_ROOT}/finance/changes",
                               json={
                                   "amount": 1000.0,
                                   "reason": "salary",
                                   "desc": "my salary for aug"
                               })
    assert create_res.status_code == codes["ok"]
    change_id = create_res.json()["id"]

    assert len(list(filter(lambda x: x["id"] == change_id, requests.get(f"{URL_ROOT}/finance/changes").json()))) > 0


def test_weekly_difference_graph():
    res = requests.get(f"{URL_ROOT}/finance/graph/weekly-difference", params={"start_date": "19/08/2024, 12:00:00"})
    assert res.status_code == codes["ok"]
    link = res.json()["link"]

    image_res = requests.get(link)
    assert image_res.status_code == codes["ok"]
    assert image_res.headers["content-type"] == "image/png"
