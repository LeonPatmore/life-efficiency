import gspread

from lambda_splitter.errors import HTTPAwareException
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems


class RepeatingItemsAlreadyPresent(HTTPAwareException):

    def __init__(self, item: str):
        super(RepeatingItemsAlreadyPresent, self)\
            .__init__(status_code=404, error_message="repeating item `{}` already present".format(item))


class RepeatingItemsWorksheet(RepeatingItems):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def get_repeating_items(self) -> list:
        return list(map(lambda x: x[0], self.worksheet.get_all_values()))

    def add_repeating_item(self, item: str) -> bool:
        repeating_items = self.get_repeating_items()
        if item in repeating_items:
            raise RepeatingItemsAlreadyPresent(item)
        self.worksheet.insert_row([item], 1)
