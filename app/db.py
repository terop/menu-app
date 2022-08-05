"""Module for handling database operations."""

import logging
from os import environ

import psycopg  # pylint: disable=import-error
from psycopg.types.json import Jsonb  # pylint: disable=import-error


def get_conn_string(config):
    """Returns the database connection string."""
    db_config = {
        'host': environ['DB_HOST'] if 'DB_HOST' in environ else config['DB_HOST'],
        'name': environ['DB_NAME'] if 'DB_NAME' in environ else config['DB_NAME'],
        'username': environ['DB_USERNAME'] if 'DB_USERNAME' in environ else config['DB_USER'],
        'password': environ['DB_PASSWORD'] if 'DB_PASSWORD' in environ else config['DB_PASSWORD']
    }

    return f'host={db_config["host"]} dbname={db_config["name"]} ' \
        f'user={db_config["username"]} password={db_config["password"]}'


def insert_menu(config, menus):
    """Inserts a menu into the database.
    Returns True on success and False on error.
    """
    if not menus or 'menu' not in menus[0]:
        return False

    start_date = min(min(menu['menu'].keys()) for menu in menus)
    end_date = max(max(menu['menu'].keys()) for menu in menus)

    try:
        with psycopg.connect(get_conn_string(config)) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO menus (start_date, end_date, menu) VALUES (%s, %s, %s)',
                            (start_date, end_date, Jsonb(menus)))
    except psycopg.Error as err:
        logging.error('Menu insert failed: %s', err)
        return False

    return True


def get_menu(config, current_date):
    """Returns the last menu for the current date between the start and
    end dates. Return value: menu as a Python object on success, None on failure.
    """
    try:
        with psycopg.connect(get_conn_string(config)) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT menu FROM menus WHERE start_date <= %s AND end_date >= %s '
                            'ORDER BY id DESC',
                            (current_date, current_date))
                rows = cur.fetchall()
                if not rows:
                    return []

                return rows[0][0]
    except psycopg.Error as err:
        logging.error('Menu query failed: %s', err)
        return None
