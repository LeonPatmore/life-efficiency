import click

from shopping.shopping_commands import shopping


@click.group()
def main_group():
    pass


main_group.add_command(shopping)


if __name__ == '__main__':
    main_group()
