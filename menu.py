#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

from datetime import date
from flask import Flask, jsonify, render_template, request
import db

app = Flask(__name__)
app.config.from_pyfile('menu.cfg')

DB_SETTINGS = {'database': app.config['DB_NAME'],
               'user': app.config['DB_USER'],
               'password': app.config['DB_PASSWORD'],
               'host': app.config['DB_HOST']}


# Routes
@app.route('/')
def index():
    """Index route."""
    args = {}

    today = date.today().isoformat()
    args['date'] = date.today().strftime('%d.%m.%Y')
    menus = db.get_menus(DB_SETTINGS, today)
    if menus:
        menu_data = []
        for menu in menus[2]:
            if today in list(menu['menu'].keys()):
                menu_data.append([menu['name'], menu['menu'][today]])
        args['menu'] = menu_data

    return render_template('index.tmpl', **args)


@app.route('/add', methods=['POST'])
def add():
    """Add menus route."""
    if not request.get_json():
        return jsonify(status='error',
                       cause='invalid json')
    retval = db.insert_menu(DB_SETTINGS, request.get_json())
    if retval:
        return jsonify(status='success')
    else:
        return jsonify(status='error',
                       cause='database error')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
