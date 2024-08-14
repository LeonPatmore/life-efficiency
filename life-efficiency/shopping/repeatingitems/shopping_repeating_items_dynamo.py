from shopping.repeatingitems.shopping_repeating_items import RepeatingItems


class RepeatingItemsDynamo(RepeatingItems):

    def __init__(self, table):
        self.table = table

    def get_repeating_items(self) -> list:
        return [x["id"] for x in self.table.scan()["Items"]]

    def add_repeating_item_impl(self, item: str):
        self.table.put_item(Item={"id": item})
