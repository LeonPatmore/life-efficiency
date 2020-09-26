import click

from shopping.shopping_configuration import shopping_manager


@click.group()
def shopping():
    pass


@click.command()
def list_history():
    click.echo(str(shopping_manager.shopping_history.get_all_purchases()))


@click.command()
def today():
    click.echo(str([x.name for x in shopping_manager.todays_items()]))


@click.command()
def complete_today():
    shopping_manager.complete_today()


shopping.add_command(list_history)
shopping.add_command(today)
shopping.add_command(complete_today)
