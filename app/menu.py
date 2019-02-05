#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

# pylint: disable=c0103
import logging
from collections import OrderedDict
from datetime import date, datetime
from flask import Flask, jsonify, render_template, request
import db

app = Flask(__name__)
app.config.from_pyfile('menu.cfg')


# Routes
@app.route('/')
def index():
    """Index route."""
    title = app.config['MENU_PAGE_TITLE'] if 'MENU_PAGE_TITLE' in app.config \
        else 'Change me!'
    args = {'title': title,
            'root': app.config['APPLICATION_ROOT']}

    today = date.today().isoformat()
    menus = db.get_menu(get_db_creds(), today)
    show_week = 'week' in request.args and request.args['week'] == 'true'
    args['date'] = date.today().strftime('%A %d.%m.%Y')
    args['week'] = show_week

    menu = None
    if menus:
        menu = format_menu(menus, show_week)
        args['menu'] = menu
    return render_template('index.tmpl', **args)


@app.route('/add', methods=['POST'])
def add():
    """Add menus route."""
    if not request.get_json():
        return jsonify(status='error',
                       cause='invalid json')
    retval = db.insert_menu(get_db_creds(), request.get_json())
    if retval:
        return jsonify(status='success')

    return jsonify(status='error',
                   cause='database insert error')


def format_menu(menus, show_week=False):
    """Format menu data for easier display."""
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if show_week:
        week_menu = {}
        for menu in menus:
            for day in menu['menu']:
                if day not in week_menu:
                    week_menu[day] = []
                week_menu[day].append({'name': menu['name'],
                                       'menu': menu['menu'][day]})
        # Reformat dates
        week_menu_format = {}
        for key in week_menu:
            new_date = datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m.%Y')
            week_menu_format[new_date] = list(chunks(week_menu[key], 3))
        del week_menu
        week_menu_ordered = OrderedDict(sorted(week_menu_format.items()))

        return week_menu_ordered

    menu_data = []
    today = date.today().isoformat()
    for menu in menus:
        if today in list(menu['menu'].keys()):
            menu_data.append([menu['name'], menu['menu'][today]])

    return list(chunks(menu_data, 3))


def get_db_creds():
    """Returns the database credentials as dictionary."""
    return {'database': app.config['DB_DATABASE'],
            'user': app.config['DB_USER'],
            'password': app.config['DB_PASSWORD'],
            'host': app.config['DB_HOST']}


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Starting menu server')
    app.run(host='0.0.0.0')
