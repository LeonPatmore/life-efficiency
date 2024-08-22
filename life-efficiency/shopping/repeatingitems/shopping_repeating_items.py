from dataclasses import dataclass

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("repeating-items")
@dataclass
class RepeatingItem:
    id: str

    def __post_init__(self):
        self.id = self.id.strip().lower()

    def to_json(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.id
        elif isinstance(other, RepeatingItem):
            return other.id == self.id
        return False


class RepeatingItems(Repository[RepeatingItem]):

    def __init__(self):
        super().__init__(RepeatingItem)
