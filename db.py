"""Module for handling database operations."""

import json
import sys
import psycopg2


def insert_menu(db_config, menus):
    """Inserts a menu into the database. Returns True on success and False
    on error."""
    start_dates = [min(menu['menu'].keys()) for menu in menus]
    end_dates = [max(menu['menu'].keys()) for menu in menus]

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute('INSERT INTO menus (start_date, end_date, menu)'
                    'VALUES (%s, %s, %s)', (min(start_dates), max(end_dates),
                                            json.dumps(menus)))

        conn.commit()
        return True
    except psycopg2.Error as err:
        print('Error: menu insert failed: {0}'.format(err.pgerror),
              file=sys.stderr)
        return False
    finally:
        cur.close()
        conn.close()


def get_menus(db_config, current_date):
    """Returns menus from the database which """
    query = 'SELECT start_date, end_date, menu FROM menus WHERE %s BETWEEN start_date AND end_date'

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute(query, (current_date,))
        return cur.fetchone()
    except psycopg2.Error as err:
        print('Error: menu query failed: {0}'.format(err.pgerror))
        return None
    finally:
        cur.close()
        conn.close()
