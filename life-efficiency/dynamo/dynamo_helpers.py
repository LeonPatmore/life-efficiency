import logging
import os


def get_table_full_name(table_name: str) -> str:
    table_name = f"life-efficiency_{os.environ.get('ENV', 'local')}_{table_name}"
    logging.info(f"Using table name {table_name}")
    return table_name
