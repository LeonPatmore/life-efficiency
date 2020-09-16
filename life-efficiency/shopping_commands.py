import click

from configuration import shopping_history_worksheet, repeating_items, shopping_predictor


@click.group()
def shopping():
    pass


@click.command()
def list_history():
    click.echo(str(shopping_history_worksheet.get_all_purchases()))


@click.command()
def today():
    todays_items = [x.name for x in repeating_items if shopping_predictor.should_buy_today(x)]
    click.echo(str(todays_items))


shopping.add_command(list_history)
shopping.add_command(today)
