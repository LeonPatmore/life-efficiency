import click

from configuration import shopping_history_worksheet, repeating_items, shopping_predictor
from shopping.shopping_item_purchase import ShoppingItemPurchase


def todays_items() -> list:
    return [x for x in repeating_items if shopping_predictor.should_buy_today(x)]


@click.group()
def shopping():
    pass


@click.command()
def list_history():
    click.echo(str(shopping_history_worksheet.get_all_purchases()))


@click.command()
def today():
    click.echo(str([x.name for x in todays_items()]))


@click.command()
def complete_today():
    for item in todays_items():
        shopping_history_worksheet.add_purchase(ShoppingItemPurchase(item, 1))


shopping.add_command(list_history)
shopping.add_command(today)
shopping.add_command(complete_today)
