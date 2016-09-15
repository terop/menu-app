#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

import logging
from collections import OrderedDict
from datetime import date, datetime
from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db

app = Flask(__name__)
app.config.from_pyfile('menu.cfg')
engine = create_engine(app.config['DB_CON_STRING'])
Session = sessionmaker(bind=engine)


# Routes
@app.route('/')
def index():
    """Index route."""
    title = app.config['MENU_PAGE_TITLE'] if 'MENU_PAGE_TITLE' in app.config \
        else 'Change me!'
    args = {'title': title,
            'root': app.config['APPLICATION_ROOT']}

    today = date.today().isoformat()
    menus = db.get_menu(Session(), today)
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
    retval = db.insert_menu(Session(), request.get_json())
    if retval:
        return jsonify(status='success')
    else:
        return jsonify(status='error',
                       cause='insert error')


def format_menu(menus, show_week=False):
    """Format menu data for easier display."""
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    if show_week:
        week_menu = {}
        for menu in menus[0]:
            for day in menu['menu']:
                if day not in week_menu:
                    week_menu[day] = []
                week_menu[day].append({'name': menu['name'],
                                       'menu': menu['menu'][day]})
        # Reformat dates
        week_menu_format = {}
        for key in week_menu.keys():
            new_date = datetime.strptime(key, '%Y-%m-%d').strftime('%d.%m.%Y')
            week_menu_format[new_date] = list(chunks(week_menu[key], 3))
        del week_menu
        week_menu_ordered = OrderedDict(sorted(week_menu_format.items()))
        return week_menu_ordered
    else:
        menu_data = []
        today = date.today().isoformat()
        for menu in menus[0]:
            if today in list(menu['menu'].keys()):
                menu_data.append([menu['name'], menu['menu'][today]])
        return list(chunks(menu_data, 3))


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(filename='menu_server.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    logging.info('Starting menu server')
    app.run(host='0.0.0.0')
