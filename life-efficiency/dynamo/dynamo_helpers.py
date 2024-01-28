import os


def get_table_full_name(table_name: str) -> str:
    return f"life-efficiency_{os.environ.get('ENV', 'local')}_{table_name}"
