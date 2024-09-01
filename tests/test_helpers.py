import sys
import uuid

from repository.repository import RepositoryImplementation


def cleanup_modules(modules):
    for module in modules:
        if module in sys.modules:
            del sys.modules[module]


def lambda_http_event(command: str, subcommand: str, body: str = None, method: str = "GET") -> dict:
    return {
        'httpMethod': method,
        'pathParameters': {
            "command": command,
            "subcommand": subcommand
        },
        "body": body
    }


class InMemoryRepository(RepositoryImplementation):
    def __init__(self, object_type: type):
        super().__init__(object_type)
        self.item_list = {}

    def get_all(self) -> list:
        return list(self.item_list.values())

    def add(self, item):
        if getattr(item, "id") is None:
            setattr(item, "id", str(uuid.uuid4()))
        self.item_list[item.id] = item
        return item

    def remove(self, item_id: str):
        self.item_list.pop(item_id)

    def get(self, item_id: str):
        return self.item_list[item_id] if item_id in self.item_list else None
