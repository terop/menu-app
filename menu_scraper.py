#!/usr/bin/env python3
"""A module for accessing and scraping Amica and Katri Antell lunch
restaurant menus. Menus are sent to a backend service for storage and
display."""

import argparse
import itertools
import json
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


def parse_antell_menu(name, restaurant_id):
    """Extracts the menu for the current week from a Katri Antell menu page."""
    menu_url = 'http://www.antell.fi/lounaslistat/lounaslista.html?owner={0}'. \
               format(restaurant_id)
    resp = requests.get(menu_url)
    if not resp.ok:
        return {}

    today = date.today()
    first_day = today - timedelta(days=today.weekday())
    last_day = first_day + timedelta(days=5)
    menu = {}
    menu_days = []
    i = 0

    while i < (last_day - first_day).days:
        menu_days.append((first_day + timedelta(days=i)).isoformat())
        i += 1

    soup = BeautifulSoup(resp.text, 'lxml')
    days = soup.find_all(id='lunch-content-table')[0].find_all('table')

    def content_filter(tag):
        """Filters away empty and too short tags."""
        return tag.name == 'td' and len(tag.text) > 6

    for i in range(5):
        rows = days[i].find_all(content_filter)
        if len(rows) > 2:
            day = menu_days[i]
            courses = [rows[j].text.split('\r')[0].strip() for j
                       in range(1, len(rows))]
            menu[day] = courses

    return {'name': name, 'menu': menu}


def get_amica_menu(name, cost_number):
    """Fetches the menu for the current week of Amica restaurants from
    their API."""
    today = date.today()
    first_day = today - timedelta(days=today.weekday())
    last_day = first_day + timedelta(days=5)
    menu = {}

    raw_url = 'http://www.amica.fi/modules/json/json/Index?costNumber={0}' \
              '&firstDay={1}&lastDay={2}&language=fi'. \
              format(cost_number, first_day.isoformat(), last_day.isoformat())
    resp = requests.get(raw_url)
    if not resp.ok:
        return {}

    full_menu = resp.json()
    for i in range(len(full_menu['MenusForDays'])):
        day_menu = full_menu['MenusForDays'][i]
        if len(day_menu['SetMenus']) > 1:
            menu_date = day_menu['Date'].split('T')[0]
            menu[menu_date] = []

            for j in range(len(day_menu['SetMenus'])):
                menu[menu_date].append(day_menu['SetMenus'][j]['Components'])
            # Flatten nested lists
            menu[menu_date] = list(itertools.chain(*menu[menu_date]))

    return {'name': name, 'menu': menu}


def get_menus(restaurants):
    """Returns menus of all restaurants given in the configuration."""
    menus = []
    menu = {}

    for res in restaurants:
        if res['type'] == 'amica':
            menu = get_amica_menu(res['name'], res['costNumber'])
        elif res['type'] == 'antell':
            menu = parse_antell_menu(res['name'], res['id'])

        if len(menu) >= 1:
            # Ignore empty menus denoting an error
            menus.append(menu)

    return menus


def main():
    """The main function of this module."""
    parser = argparse.ArgumentParser(description='Extract lunch restaurant menus.')
    parser.add_argument('config', type=str, help='restaurant configuration file')

    args = parser.parse_args()

    config = json.load(open(args.config, 'r'))
    all_menus = get_menus(config['restaurants'])

    resp = requests.post(config['backendUrl'], json=all_menus, timeout=5)
    timestamp = datetime.now().isoformat()
    if not resp.ok:
        print('{0}: Menu extraction failed'.format(timestamp))
    else:
        status = resp.json()
        if status['status'] == 'success':
            print('{0}: Menu extraction succeeded'.format(timestamp))
        else:
            print('{0}: Menu extraction failed, error: {1}'.
                  format(timestamp, status['cause']))


if __name__ == '__main__':
    main()
