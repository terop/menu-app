#!/usr/bin/env python3
"""Module for running Flask in the menu application."""

from datetime import date
from flask import Flask, render_template, request
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

    menu = db.get_menus(DB_SETTINGS, date.today().isoformat())
    if menu:
        args['menu'] = menu

    return render_template('index.tmpl', **args)


@app.route('/add', methods=['POST'])
def add():
    """Add menus route."""
    return str(db.insert_menu(DB_SETTINGS, request.get_json()))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
