import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("shopping_item_ignore")
@dataclass
class ShoppingItemIgnore:
    ttl: int
    item_name: str
    id: str = None

    def __post_init__(self):
        self.item_name = self.item_name.strip().lower()


class ShoppingIgnore(Repository[ShoppingItemIgnore]):

    def __init__(self):
        super().__init__(ShoppingItemIgnore)

    def get_all_within_ttl(self) -> set[ShoppingItemIgnore]:
        return set(map(lambda x: x.item_name, filter(lambda x: int(time.time()) < x.ttl, self.get_all())))

    def add_item(self, item_name: str):
        self.add(ShoppingItemIgnore(self._get_2_days_timestamp(), item_name))
        logging.info(f"Added ignore for item {item_name}")

    @staticmethod
    def _get_2_days_timestamp() -> int:
        now_utc = datetime.now(timezone.utc)
        two_days_later_utc = now_utc + timedelta(days=2)
        return int(two_days_later_utc.timestamp())
