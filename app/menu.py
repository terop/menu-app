#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

import logging
from collections import OrderedDict
from datetime import date, datetime, timedelta

from flask import Flask, jsonify, render_template, request  # pylint: disable=import-error

import db  # pylint: disable=import-error

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

    show_week = 'mode' in request.args and request.args['mode'] == 'week'
    today = date.today()

    if show_week:
        start_date = today - timedelta(days=today.weekday())
        menus = db.get_menu(app.config, start_date.isoformat())
    else:
        menus = db.get_menu(app.config, today.isoformat())

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
    retval = db.insert_menu(app.config, request.get_json())
    if retval:
        return jsonify(status='success')

    return jsonify(status='error',
                   cause='database insert error')


def format_menu(menus, show_week=False):
    """Format menu data for easier display."""
    def chunks(list_, size):
        """Yield successive size-sized chunks from list_."""
        for i in range(0, len(list_), size):
            yield list_[i:i + size]

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
        # pylint: disable=consider-using-dict-items
        for key in week_menu:
            new_date = datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m.%Y')
            week_menu_format[new_date] = list(chunks(week_menu[key], 3))
        del week_menu

        week_menu_ordered = OrderedDict(sorted(week_menu_format.items()))
        week_menu_days = OrderedDict()
        # Add weekday before the day's date
        for key in week_menu_ordered:
            day_str = datetime.strptime(key, '%d.%m.%Y').strftime('%A')
            week_menu_days[f'{day_str} {key}'] = week_menu_ordered[key]

        return week_menu_days

    menu_data = []
    today = date.today().isoformat()
    for menu in menus:
        if today in list(menu['menu'].keys()):
            menu_data.append([menu['name'], menu['menu'][today]])

    return list(chunks(menu_data, 3))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    logging.info('Starting menu server')
    app.run(host='0.0.0.0')
