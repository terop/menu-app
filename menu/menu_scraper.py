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
        if len(rows) > 3:
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


def get_sodexo_menu(name, restaurant_id):
    """Fetches the current weeks menu for a Sodexo restaurant from its
    JSON formatted menu."""
    base_url = "http://www.sodexo.fi/ruokalistat/output/daily_json/"
    monday = date.today()
    menus = {}

    if monday.weekday() != 0:
        monday -= timedelta(days=monday.weekday())

    for i in range(0, 5):
        day = monday + timedelta(days=i)
        full_url = '{0}{1}/{2}/fi'.format(base_url, restaurant_id,
                                          day.strftime('%Y/%m/%d'))

        resp = requests.get(full_url)
        if not resp.ok:
            return {}

        json_menu = resp.json()
        if len(json_menu['courses']) > 2:
            # No menu for today, the restaurant is probably closed
            courses = [course['title_fi'] for course in json_menu['courses']]
            menus[day.isoformat()] = courses

    return {'name': name, 'menu': menus}


def parse_taffa_menu(name, url):
    """Extracts the menu of Täffä from their web site. Due to the
    'non-continuous' menu structure each day must be checked to ensure
    that they belong to the same week."""
    monday = date.today()
    menus = {}

    if monday.weekday() != 0:
        monday -= timedelta(days=monday.weekday())
    days = [monday + timedelta(days=i) for i in range(0, 5)]

    resp = requests.get(url)
    if not resp.ok:
        return {}

    soup = BeautifulSoup(resp.content, 'lxml')
    # First (or current) day of week
    today_menu = soup.find(class_='todays-menu')
    split_day = today_menu.find('p').text.split(' ')[1].split('.')
    day_date = date(int(split_day[2]), int(split_day[1]),
                    int(split_day[0]))
    if day_date in days:
        day_menu = []
        for course in today_menu.find('ul'):
            if len(course.string) > 3:
                # Skip newlines
                day_menu.append(course.string)
        if len(day_menu) > 2:
            # Need to have enough courses to ensure that the
            # restaurant is open
            menus[day_date.isoformat()] = day_menu

    # Remaining days
    week_menu = soup.find(id='week')
    for child in week_menu.children:
        if child.name == 'p':
            # A day name
            split_day = child.string.split(' ')[1].split('.')
            day_date = date(int(split_day[2]), int(split_day[1]),
                            int(split_day[0]))
            if day_date in days:
                day_menu = []
                for item in child.next_sibling.next_sibling.children:
                    if len(item.string) > 3:
                        # Skip newlines
                        day_menu.append(item.string)
                if len(day_menu) > 2:
                    # Need to have enough courses to ensure that the
                    # restaurant is open
                    menus[day_date.isoformat()] = day_menu

    return {'name': name, 'menu': menus}


def get_menus(restaurants):
    """Returns menus of all restaurants given in the configuration.
    Restaurant types are: amica, antell, sodexo."""
    menus = []
    menu = {}

    for res in restaurants:
        if res['type'] == 'amica':
            menu = get_amica_menu(res['name'], res['costNumber'])
        elif res['type'] == 'antell':
            menu = parse_antell_menu(res['name'], res['id'])
        elif res['type'] == 'sodexo':
            menu = get_sodexo_menu(res['name'], res['id'])
        elif res['type'] == 'taffa':
            menu = parse_taffa_menu(res['name'], res['url'])

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
