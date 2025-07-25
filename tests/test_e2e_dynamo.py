import json
import sys
import uuid
from unittest.mock import Mock

import pytest

from helpers.datetime import get_current_datetime_utc
from tests.dynamo_db_mock import DynamoDbMock
from tests.test_helpers import cleanup_modules, lambda_http_event
from todo.weekly.todo_weekly_manager_dynamo import TodoWeeklyManagerDynamo


@pytest.fixture(autouse=True)
def reset_configuration():
    cleanup_modules(["configuration"])
    yield
    cleanup_modules(["configuration"])


@pytest.fixture
def setup_mocks(request, monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "life-efficiency")
    boto3_mock = Mock()
    sys.modules['boto3'] = boto3_mock

    s3_mock = Mock()
    s3_object_body_mock = Mock()
    s3_mock.get_object.return_value = {
        "Body": s3_object_body_mock
    }
    s3_object_body_mock.read.return_value = """{"monthly_salary": 100.0, "monthly_tax": 10.0}""".encode("utf-8")
    boto3_mock.client.return_value = s3_mock
    s3_mock.generate_presigned_url.return_value = "some-url"

    dynamodb_mock = Mock()
    boto3_mock.resource.return_value = dynamodb_mock

    table_init_config = request.param if hasattr(request, "param") else {}
    dynamodb_mock.Table.side_effect = lambda table_name: DynamoDbMock(table_init_config.get(table_name, []))


def test_shopping_purchase_quantity_field_must_be_present(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "history"
        },
        "body": """{"name": "my-item"}"""
    }, {})

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `quantity` is required"


def test_shopping_purchase_quantity_field_must_be_an_integer(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "history"
        },
        "body": """{"name": "my-item", "quantity": "four"}"""
    }, {})

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `quantity` must be of type int"


def test_shopping_list_delete_item_name_must_be_present(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "DELETE",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        'queryStringParameters': {
            'quantity': 1
        }
    }, {})

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "param `name` is required"


def test_shopping_list_adding_items_together(setup_mocks):
    import configuration

    item_name = str(uuid.uuid4())

    res_create_1 = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})
    assert 200 == res_create_1["statusCode"]
    res_create_2 = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})
    assert 200 == res_create_2["statusCode"]

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    item_part = [x for x in body if x["name"] == item_name][0]
    assert item_part["name"] == item_name
    assert item_part["quantity"] == 6


def test_todays_items_with_completion(setup_mocks):
    import configuration

    item_name = str(uuid.uuid4())

    res_create = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})
    assert 200 == res_create["statusCode"]

    first_get = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "today"
        }
    }, {})

    assert 200 == first_get["statusCode"]
    first_get_list = json.loads(first_get["body"])
    assert first_get_list == [item_name, item_name, item_name]

    complete_res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "items"
        },
        "body": f"""{{"items": ["{item_name}", "{item_name}"]}}"""
    }, {})
    assert 200 == complete_res["statusCode"]

    second_get = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "today"
        }
    }, {})

    assert 200 == second_get["statusCode"]
    second_get_list = json.loads(second_get["body"])
    assert second_get_list == [item_name]


def test_repeating_items(setup_mocks):
    import configuration

    item_name = str(uuid.uuid4())

    create_res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        },
        "body": f"""{{"item": "{item_name}"}}"""
    }, {})
    assert 200 == create_res["statusCode"]

    res = configuration.handler(lambda_http_event("shopping", "repeating"))
    assert 200 == res["statusCode"]
    assert item_name in json.loads(res["body"])

    res = configuration.handler(lambda_http_event("shopping",
                                                  "repeating",
                                                  method="DELETE",
                                                  query_params={"item": item_name}))
    assert 200 == res["statusCode"]

    res = configuration.handler(lambda_http_event("shopping", "repeating"))
    assert 200 == res["statusCode"]
    assert item_name not in json.loads(res["body"])


def test_repeating_items_removes_whitespace(setup_mocks):
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        },
        "body": f"""{{"item": " {item_name} "}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        }
    }, {})

    assert 200 == res["statusCode"]
    assert item_name in json.loads(res["body"])


@pytest.mark.parametrize('setup_mocks',
                         [{"life-efficiency_local_repeating-items": [{"id": "item-1"}, {"id": "item-2"}],
                           "life-efficiency_local_shopping-history": [
                               {
                                   "id": str(uuid.uuid4()),
                                   "name": "item-1",
                                   "Quantity": 1,
                                   "Date": "01/01/2000, 01:00:00"
                               },
                               {
                                   "id": str(uuid.uuid4()),
                                   "name": "item-1",
                                   "Quantity": 1,
                                   "Date": "03/01/2000, 02:00:00"
                               }
                           ]}],
                         indirect=True)
def test_repeating_items_detail(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating-details"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["item-1"]["avg_gap_days"] == 2
    assert "time_since_last_bought" in body["item-1"]
    assert body["item-1"]["today"]
    assert body["item-2"]["avg_gap_days"] is None
    assert body["item-2"]["time_since_last_bought"] is None
    assert not body["item-2"]["today"]


def test_todo(setup_mocks):
    import configuration

    def _todo_item_exists(todo_id: str) -> bool:
        todos = json.loads(configuration.handler({
            'httpMethod': "GET",
            'pathParameters': {
                "command": "todo",
                "subcommand": "list"
            }
        }, {})["body"])
        return len(list(filter(lambda x: x["id"] == todo_id, todos))) > 0

    res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        'body': json.dumps({
            "desc": "a test todo"
        })
    }, {})
    assert 200 == res["statusCode"]
    todo_id = json.loads(res["body"])["id"]

    res = configuration.handler({
        'httpMethod': "PATCH",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        'body': json.dumps({
            "id": todo_id,
            "status": "done"
        })
    }, {})
    assert 200 == res["statusCode"]

    assert _todo_item_exists(todo_id)

    res = configuration.handler({
        'httpMethod': "DELETE",
        'pathParameters': {
            "command": "todo",
            "subcommand": f"list/{todo_id}"
        },
        'path': f"todo/list/{todo_id}"
    }, {})
    assert 200 == res["statusCode"]

    assert not _todo_item_exists(todo_id)


@pytest.mark.parametrize('setup_mocks',
                         [{"life-efficiency_local_todo-list": [
                             {
                                 "id": str(uuid.uuid4()),
                                 "Desc": "item-1",
                                 "Status": "in_progress",
                                 "DateAdded": "01/01/2000, 01:00:00",
                                 "DateDone": None
                             },
                             {
                                 "id": str(uuid.uuid4()),
                                 "Desc": "item-2",
                                 "Status": "done",
                                 "DateAdded": "01/01/2000, 01:00:00",
                                 "DateDone": None
                             },
                         ]}],
                         indirect=True)
def test_todo_non_completed(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "non_completed"
        }
    }, {})
    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert len(body) == 1
    assert body[0]["desc"] == "item-1"
    assert body[0]["status"] == "in_progress"
    assert body[0]["date_added"] == "01/01/2000, 01:00:00"
    assert body[0]["date_done"] is None


@pytest.mark.parametrize('setup_mocks',
                         [{"life-efficiency_local_todo-sets": [{"id": "abc123", "name": "set_one"}]}],
                         indirect=True)
def test_todo_sets(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "sets"
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == "abc123"
    assert res_json[0]["name"] == "set_one"


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 2, "Desc": "something else", "SetId": "setOne"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_day(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'day': 1
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 1


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne",
                                  f"Week_{TodoWeeklyManagerDynamo._get_time_id(get_current_datetime_utc)}": 1}
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_when_complete(setup_mocks):
    import configuration

    res = configuration.handler(lambda_http_event("todo", "weekly"))

    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 1
    assert res_json[0]["complete"]


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne",
                                  f"Week_{TodoWeeklyManagerDynamo._get_time_id(get_current_datetime_utc)-1}": 1}
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_completed_last_week_still_shows(setup_mocks):
    import configuration

    res = configuration.handler(lambda_http_event("todo", "weekly"))

    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne", "WeekFrequency": 2,
                                  "Week_1": 1, "Week_2": 1, "Week_3": 1, "Week_4": 1, "Week_5": 1, "Week_6": 1,
                                  "Week_7": 1, "Week_8": 1, "Week_9": 1,
                                  f"Week_{TodoWeeklyManagerDynamo._get_time_id(get_current_datetime_utc)-1}": 1}
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_completed_last_week_and_biweekly_does_not_show(setup_mocks):
    import configuration

    res = configuration.handler(lambda_http_event("todo", "weekly"))

    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 0


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne", "WeekFrequency": 2,
                                  f"Week_{TodoWeeklyManagerDynamo._get_time_id(get_current_datetime_utc)-2}": 1}
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_completed_two_weeks_ago_and_biweekly_shows(setup_mocks):
    import configuration

    res = configuration.handler(lambda_http_event("todo", "weekly"))

    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 1, "Desc": "something else", "SetId": "setTwo"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_set_id(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'set_id': "setTwo"
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 2


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 2, "Desc": "something else", "SetId": "setOne"},
                                 {"id": "3", "Day": 1, "Desc": "something else", "SetId": "setTwo"},
                                 {"id": "4", "Day": 2, "Desc": "something else", "SetId": "setTwo"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_set_id_and_day(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'set_id': "setTwo",
            'day': 1
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 3


def test_shopping_history_add_purchase_strips_whitespace(setup_mocks):
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "history"
        },
        "body": f"""{{"name": " {item_name} ","quantity": 3}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "history"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    item_part = [x for x in body if x["name"] == item_name][0]
    assert item_part["name"] == item_name
    assert item_part["quantity"] == 3


@pytest.mark.parametrize('setup_mocks',
                         [{
                             "life-efficiency_local_goals": [
                                 {"id": "do something", "Year": 2024, "Quarter": "q1", "Progress": "in_progress"},
                                 {"id": "do something else", "Year": 2024, "Quarter": "q1", "Progress": "in_progress"},
                                 {"id": "and this", "Year": 2025, "Quarter": "q1", "Progress": "in_progress"},
                             ]
                         }],
                         indirect=True)
def test_goals(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "goals",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert "2024" in body
    assert len(body["2024"]["q1"]) == 2
    assert len(body["2024"]["q2"]) == 0
    assert len(body["2024"]["q3"]) == 0
    assert len(body["2024"]["q4"]) == 0
    assert "2025" in body
    assert len(body["2025"]["q1"]) == 1
    assert len(body["2025"]["q2"]) == 0
    assert len(body["2025"]["q3"]) == 0
    assert len(body["2025"]["q4"]) == 0


def test_finance_balance_instances(setup_mocks):
    import configuration

    create_res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "finance",
            "subcommand": "instances"
        },
        "body": """{"amount": 1000.0, "date": "21/08/2024, 13:00:00", "holder": "bank"}"""
    }, {})

    assert 200 == create_res["statusCode"]
    body = json.loads(create_res["body"])
    assert body["amount"] == 1000.0
    assert body["date"] == "21/08/2024, 13:00:00"
    assert body["holder"] == "bank"
    assert "id" in body and body["id"] is not None

    get_res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "finance",
            "subcommand": "instances"
        }
    }, {})
    assert 200 == get_res["statusCode"]
    body = json.loads(get_res["body"])
    assert len(body) == 1
    assert body[0]["amount"] == 1000.0
    assert body[0]["date"] == "21/08/2024, 13:00:00"
    assert body[0]["holder"] == "bank"
    assert "id" in body[0]


def test_finance_balance_instances_with_filter(setup_mocks):
    import configuration

    create_res = configuration.handler(lambda_http_event(
        "finance",
        "instances",
        """{"amount": 1000.0, "date": "21/08/2024, 13:00:00", "holder": "bank"}""", "POST"))
    assert 200 == create_res["statusCode"]
    create_res_not_bank = configuration.handler(lambda_http_event(
        "finance",
        "instances",
        """{"amount": 1000.0, "date": "21/08/2024, 13:00:00", "holder": "not_bank"}""", "POST"))
    assert 200 == create_res_not_bank["statusCode"]

    get_res = configuration.handler(lambda_http_event(
        "finance",
        "instances",
        query_params={
            "holder": "not_bank"
        }))
    assert 200 == get_res["statusCode"]
    body = json.loads(get_res["body"])
    assert body[0]["id"] == json.loads(create_res_not_bank["body"])["id"]


def test_finance_balance_instances_no_date_generates_one(setup_mocks):
    import configuration

    create_res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "finance",
            "subcommand": "instances"
        },
        "body": """{"amount": 1000.0, "holder": "bank"}"""
    }, {})

    assert 200 == create_res["statusCode"]
    body = json.loads(create_res["body"])
    assert body["amount"] == 1000.0
    assert body["date"] is not None
    assert body["holder"] == "bank"
    assert "id" in body and body["id"] is not None


def test_finance_changes(setup_mocks):
    import configuration

    create_res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "finance",
            "subcommand": "changes"
        },
        "body": """{"amount": 1000.0, "reason": "salary", "desc": "some reason"}"""
    }, {})

    assert 200 == create_res["statusCode"]
    body = json.loads(create_res["body"])
    assert body["amount"] == 1000.0
    assert "date" in body
    assert body["reason"] == "salary"
    assert body["desc"] == "some reason"
    assert "id" in body and body["id"] is not None

    get_res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "finance",
            "subcommand": "changes"
        }
    }, {})
    assert 200 == get_res["statusCode"]
    body = json.loads(get_res["body"])
    assert len(body) == 1
    assert body[0]["amount"] == 1000.0
    assert "date" in body[0]
    assert body[0]["reason"] == "salary"
    assert body[0]["desc"] == "some reason"
    assert "id" in body[0]


def test_finance_range(setup_mocks):
    import configuration

    create_res = configuration.handler(lambda_http_event("finance", "range",
                                                         query_params={"start_date": "01/01/2000, 12:00:00",
                                                                       "end_date": "22/01/2000, 12:00:00"}))

    assert 200 == create_res["statusCode"]
    body = json.loads(create_res["body"])
    assert body == {
        "step": "7 days, 0:00:00",
        "all_holders": [],
        "balances": {
            "01/01/2000, 12:00:00": {
                "holders": [],
                "balance_changes": [],
                "total": 0,
                "total_increase": None,
                "total_increase_normalised": None
            },
            "08/01/2000, 12:00:00": {
                "holders": [],
                "balance_changes": [],
                "total": 0,
                "total_increase": 0,
                "total_increase_normalised": 0
            },
            "15/01/2000, 12:00:00": {
                "holders": [],
                "balance_changes": [],
                "total": 0,
                "total_increase": 0,
                "total_increase_normalised": 0
            },
            "22/01/2000, 12:00:00": {
                "holders": [],
                "balance_changes": [],
                "total": 0,
                "total_increase": 0,
                "total_increase_normalised": 0
            }
        }
    }


@pytest.mark.parametrize('setup_mocks',
                         [{"life-efficiency_local_shopping-history": [
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-2",
                                 "Quantity": 1,
                                 "Date": "03/01/1999, 02:00:00"
                             },
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-1",
                                 "Quantity": 1,
                                 "Date": "01/01/2000, 01:00:00"
                             }
                         ]}],
                         indirect=True)
def test_shopping_history_is_ordered(setup_mocks):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "history"
        }
    }, {})

    assert 200 == res["statusCode"]
    items = json.loads(res["body"])
    assert items[0]["name"] == "item-1"


def test_finance_graph_weekly_difference(setup_mocks):
    import configuration

    create_res = configuration.handler(lambda_http_event("finance", "graph/weekly-difference",
                                                         query_params={"start_date": "01/01/2000, 12:00:00",
                                                                       "end_date": "22/01/2000, 12:00:00"}))

    assert 200 == create_res["statusCode"]
    body = json.loads(create_res["body"])
    assert body == {
        "link": "some-url"
    }


def test_get_finance_metadata(setup_mocks):
    import configuration

    res = configuration.handler(lambda_http_event("finance", "metadata"))

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["yearly_salary"] == 1200.0
    assert body["monthly_salary"] == 100.0


@pytest.mark.parametrize('setup_mocks',
                         [{"life-efficiency_local_shopping-history": [
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-1",
                                 "Quantity": 1,
                                 "Date": "01/01/1999, 01:00:00"
                             },
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-1",
                                 "Quantity": 1,
                                 "Date": "02/01/2000, 01:00:00"
                             },
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-2",
                                 "Quantity": 1,
                                 "Date": "01/01/2000, 01:00:00"
                             },
                             {
                                 "id": str(uuid.uuid4()),
                                 "name": "item-2",
                                 "Quantity": 1,
                                 "Date": "02/01/2000, 01:00:00"
                             }
                         ],
                             "life-efficiency_local_repeating-items": [{"id": "item-1"}, {"id": "item-2"}]}],
                         indirect=True)
def test_todays_items_with_ignored(setup_mocks):
    import configuration

    get_today_no_ignore = configuration.handler(lambda_http_event("shopping", "today"))
    assert 200 == get_today_no_ignore["statusCode"]
    today_no_ignore = json.loads(get_today_no_ignore["body"])
    assert today_no_ignore == ["item-1", "item-2"]

    configuration.handler(lambda_http_event("shopping", "ignore", {
        "item_name": "item-1"
    }, "POST"))

    get_today_with_ignore = configuration.handler(lambda_http_event("shopping", "today"))
    assert 200 == get_today_with_ignore["statusCode"]
    today_with_ignore = json.loads(get_today_with_ignore["body"])
    assert today_with_ignore == ["item-2"]
