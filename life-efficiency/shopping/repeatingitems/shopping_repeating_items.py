class RepeatingItems(object):

    def get_repeating_items(self) -> list:
        raise NotImplementedError()

    def add_repeating_item(self, item: str):
        self.add_repeating_item_impl(item.strip())

    def add_repeating_item_impl(self, item: str):
        raise NotImplementedError()
