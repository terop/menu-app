"""Module for handling database operations."""

import logging
from os import environ
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


def get_conn_string(config):
    """Return the database connection string."""
    db_config = {
        'host': environ['DB_HOST'] if 'DB_HOST' in environ else config['DB_HOST'],
        'name': environ['DB_NAME'] if 'DB_NAME' in environ else config['DB_NAME'],
        'username': environ['DB_USERNAME'] if 'DB_USERNAME' in environ \
        else config['DB_USER'],
        'password': config.get('DB_PASSWORD', None)
    }
    if not db_config['password']:
        password_file = environ.get('DB_PASSWORD_FILE', None)
        if password_file:
            with Path.open(password_file, 'r') as pw_file:
                db_config['password'] = pw_file.readline().strip()
        else:
            logging.error('No database server password provided')

    return f'host={db_config["host"]} dbname={db_config["name"]} ' \
        f'user={db_config["username"]} password={db_config["password"]}'


def insert_menu(config, menus):
    """Insert a menu into the database.

    Return value: True on success and False on error.
    """
    if not menus or 'menu' not in menus[0]:
        return False

    start_date = min(min(menu['menu'].keys()) for menu in menus)
    end_date = max(max(menu['menu'].keys()) for menu in menus)

    try:
        with psycopg.connect(get_conn_string(config)) as conn, conn.cursor() as cur:
            cur.execute('INSERT INTO menus (start_date, end_date, menu) '
                        'VALUES (%s, %s, %s)',
                        (start_date, end_date, Jsonb(menus)))
    except psycopg.Error:
        logging.exception('Menu insert failed')
        return False

    return True


def get_menu(config, start_date):
    """Return the last menu >= the start date.

    Return value: menu as a Python object on success or None on failure.
    """
    try:
        with psycopg.connect(get_conn_string(config)) as conn, conn.cursor() as cur:
            cur.execute('SELECT menu FROM menus WHERE start_date >= %s '
                        'ORDER BY id DESC',
                        (start_date,))
            rows = cur.fetchone()
            if not rows:
                return []

            return rows[0]
    except psycopg.Error:
        logging.exception('Menu query failed')
        return None
