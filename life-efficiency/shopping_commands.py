import click

from configuration import shopping_history_worksheet


@click.group()
def shopping():
    pass


@click.command()
def list_history():
    click.echo(str(shopping_history_worksheet.get_all_purchases()))

@click.command()
def get_todays_items():



shopping.add_command(list_history)
