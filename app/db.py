"""Module for handling database operations."""

import logging

import psycopg2
import psycopg2.extras


def insert_menu(db_creds, menus):
    """Inserts a menu into the database.
    Returns True on success and False on error.
    """
    if not menus or 'menu' not in menus[0]:
        return False

    start_date = min([min(menu['menu'].keys()) for menu in menus])
    end_date = max([max(menu['menu'].keys()) for menu in menus])

    try:
        with psycopg2.connect(dbname=db_creds['database'],
                              user=db_creds['user'],
                              password=db_creds['password'],
                              host=db_creds['host']) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO menus (start_date, end_date, menu) VALUES (%s, %s, %s)',
                            (start_date, end_date, psycopg2.extras.Json(menus)))
    except psycopg2.Error as err:
        logging.error('Error: menu insert failed: %s', err.pgerror)
        return False

    return True


def get_menu(db_creds, current_date):
    """Returns the last menu for the current date between the start and
    end dates. Return value: menu as a Python object on success, None on failure.
    """
    try:
        with psycopg2.connect(dbname=db_creds['database'],
                              user=db_creds['user'],
                              password=db_creds['password'],
                              host=db_creds['host']) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT menu FROM menus WHERE start_date <= %s AND end_date >= %s '
                            'ORDER BY id DESC',
                            (current_date, current_date))
                rows = cur.fetchall()
                if not rows:
                    return []

                return rows[0][0]
    except psycopg2.Error as err:
        logging.error('Error: menu query failed: %s', err.pgerror)
        return None
