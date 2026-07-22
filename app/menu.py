#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

import logging
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import db
import tomllib
from flask import Flask, jsonify, render_template, request

logger = logging.getLogger('menu')

app = Flask(__name__)

CONFIG_FILE = 'config.toml'

with Path(CONFIG_FILE).open('rb') as conf_file:
    _config = tomllib.load(conf_file)

_db = _config.get('database', {})
app.config.update({
    'DEBUG': _config.get('debug', False),
    'APPLICATION_ROOT': _config.get('application_root', ''),
    'MENU_PAGE_TITLE': _config.get('menu_page_title', 'Change me!'),
    'DB_HOST': _db.get('host'),
    'DB_NAME': _db.get('name'),
    'DB_USER': _db.get('user'),
    'DB_PASSWORD': _db.get('password'),
})


# Routes
@app.route('/')
def index():
    """Index route."""
    title = app.config.get('MENU_PAGE_TITLE', 'Change me!')
    args = {'title': title,
            'root': app.config['APPLICATION_ROOT']}

    show_week = 'mode' in request.args and request.args['mode'] == 'week'
    today = datetime.now(tz=timezone.utc).date()
    start_date = today - timedelta(days=today.weekday())
    menus = db.get_menu(app.config, start_date.isoformat())

    args['date'] = today.strftime('%A %d.%m.%Y')
    args['week'] = show_week

    menu = None
    if menus:
        menu = format_menu(menus, show_week=show_week)
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


def format_menu(menus, *, show_week=False):
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
        for key in week_menu:  # noqa: PLC0206
            new_date = (
                datetime.strptime(key, '%Y-%m-%d')
                .replace(tzinfo=timezone.utc)
                .strftime('%d.%m.%Y')
            )
            week_menu_format[new_date] = list(chunks(week_menu[key], 3))
        del week_menu

        week_menu_ordered = OrderedDict(sorted(week_menu_format.items()))
        week_menu_days = OrderedDict()
        # Add weekday before the day's date
        for key in week_menu_ordered:
            day_str = (
                datetime.strptime(key, '%d.%m.%Y')
                .replace(tzinfo=timezone.utc)
                .strftime('%A')
            )
            week_menu_days[f'{day_str} {key}'] = week_menu_ordered[key]

        return week_menu_days

    today = datetime.now(tz=timezone.utc).date().isoformat()
    menu_data = [[menu['name'], menu['menu'][today]] for menu in menus
                 if today in menu['menu']]

    return list(chunks(menu_data, 3))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    logger.info('Starting menu server')
    app.run(host='0.0.0.0')  # noqa: S104
