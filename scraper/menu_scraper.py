#!/usr/bin/env python3
"""A module for accessing and scraping Amica and Katri Antell lunch
restaurant menus. Menus are sent to a backend service for storage and
display."""

import argparse
import json
import re
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


def parse_antell_menu(name, restaurant_id):
    """Extracts the menu for the current week from a Katri Antell menu page."""
    menu_url = 'http://www.antell.fi/lounaslistat/lounaslista.html?owner={0}'. \
               format(restaurant_id)
    resp = requests.get(menu_url)
    # Check for a failed request or a redirect
    if not resp.ok or restaurant_id not in resp.url:
        return {}

    today = date.today()
    first_day = today - timedelta(days=today.weekday())
    last_day = first_day + timedelta(days=5)
    menu = {}
    menu_days = []
    i = 0

    while i < (last_day - first_day).days:
        # pylint: disable=no-member
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


def get_amica_menu(name, restaurant_number, language='en'):
    """Fetches the menu for the current week of Amica restaurants from
    their API."""
    monday = date.today()
    menu = {}

    if monday.weekday() != 0:
        monday -= timedelta(days=monday.weekday())
    day_str = monday.strftime('%Y-%m-%d')

    # pylint: disable=no-member
    url = 'http://www.amica.fi/api/restaurant/menu/week?language={0}' \
          '&restaurantPageId={1}&weekDate={2}'.format(language,
                                                      restaurant_number,
                                                      day_str)
    resp = requests.get(url)
    if not resp.ok:
        return {}

    full_menu = resp.json()
    if not full_menu['LunchMenus']:
        return {}

    for day_menu in full_menu['LunchMenus'][0:5]:
        menu_date = datetime.strptime(day_menu['Date'], '%d.%m.%Y').date().isoformat()
        if day_menu['SetMenus']:
            menu[menu_date] = []

        # Ensure there is at least one menu for the day
        if day_menu['SetMenus']:
            for i in range(len(day_menu['SetMenus'])):
                menu[menu_date].append(day_menu['SetMenus'][i]['Name'])
                meals = day_menu['SetMenus'][i]['Meals']
                for _, meal in enumerate(meals):
                    menu[menu_date].append(meal['Name'])

        try:
            if not menu[menu_date]:
                # Delete empty menu
                del menu[menu_date]
        except KeyError:
            # Date is not found so the error can be ignored
            pass

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
            courses = ['{}: {} {}'.format(course['category'], course['title_fi'],
                                          course['price']) for course in json_menu['courses']]
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
    day_date = datetime.strptime(today_menu.find('p').text.split(' ')[1],
                                 '%d.%m.%Y').date()

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
            day_date = datetime.strptime(child.string.split(' ')[1],
                                         '%d.%m.%Y').date()

            if day_date in days:
                day_menu = []
                for item in child.next_sibling.next_sibling.children:
                    if item and item.string and len(item.string) > 3:
                        # Skip newlines
                        day_menu.append(item.string)
                if len(day_menu) > 1:
                    # Need to have enough courses to ensure that the
                    # restaurant is open
                    menus[day_date.isoformat()] = day_menu

    return {'name': name, 'menu': menus}


def parse_metropol_menu(name, url):
    """Parses the menu for the current week for the Metropol lunch restaurant
    in Innopoli 2 from the restaurant's web page."""
    pattern = re.compile(r'([\w\s:;,-]+) \d+,\d+.+')
    day_ids = ['day-ma', 'day-ti', 'day-ke', 'day-to', 'day-pe']
    menu = {}

    resp = requests.get(url)
    if not resp.ok:
        return {}

    soup = BeautifulSoup(resp.content, 'lxml')
    for day_id in day_ids:
        if not soup.find(id=day_id):
            continue
        day_date = soup.find(id=day_id).find('p').find('strong').text.split(' ')[1]
        menu_list = soup.find(id=day_id).find_all('li')
        day_menu = []

        for item in menu_list:
            match = re.match(pattern, item.text)
            if match:
                day_menu.append(match.groups()[0])

        if len(day_menu) > 1:
            parsed_date = datetime.strptime(day_date, '%d.%m.%Y').date()
            menu[parsed_date.isoformat()] = day_menu

    return {'name': name, 'menu': menu}


def parse_iss_menu(name, url):
    """Parses the menu for the current week for a ISS lunch restaurant
    from the restaurant's web page."""
    day_names = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai']
    pattern = re.compile(r'(\d+\.\d+)\.?')
    menu = {}
    day_menu = []
    current_date = None

    resp = requests.get(url)
    if not resp.ok:
        return {}

    soup = BeautifulSoup(resp.content, 'lxml')
    if len(soup.find_all('table')) < 1:
        return {}

    rows = soup.find_all('table')[0].find_all('tr')
    for idx, row in enumerate(rows):
        if idx == 0:
            continue

        columns = row.find_all('td')
        if columns[0].text in day_names and \
           re.match(pattern, columns[1].text):
            match = re.match(pattern, columns[1].text)
            current_date = datetime.strptime('{}.{}'.format(match.group(1),
                                                            datetime.now().strftime('%Y')),
                                             '%d.%m.%Y').date().isoformat()
        else:
            if len(columns[1].text) > 5:
                day_menu.append('{}: {}'.format(columns[0].text, columns[1].text))
            if (len(columns[0].text) <= 1 and len(columns[1].text) <= 1) or \
               idx == (len(rows) - 1):
                if len(day_menu) > 2:
                    menu[current_date] = day_menu
                day_menu = []

    return {'name': name, 'menu': menu}


def get_menus(restaurants):
    """Returns menus of all restaurants given in the configuration.
    Restaurant types are: amica, antell, sodexo."""
    menus = []
    menu = {}

    for res in restaurants:
        if res['type'] == 'amica':
            if 'language' in res:
                menu = get_amica_menu(res['name'], res['restaurantNumber'],
                                      language=res['language'])
            else:
                menu = get_amica_menu(res['name'], res['restaurantNumber'])
        elif res['type'] == 'antell':
            menu = parse_antell_menu(res['name'], res['id'])
        elif res['type'] == 'sodexo':
            menu = get_sodexo_menu(res['name'], res['id'])
        elif res['type'] == 'taffa':
            menu = parse_taffa_menu(res['name'], res['url'])
        elif res['type'] == 'metropol':
            menu = parse_metropol_menu(res['name'], res['url'])
        elif res['type'] == 'iss':
            menu = parse_iss_menu(res['name'], res['url'])

        if len(menu) >= 1 and len(menu['menu']) >= 1:
            # Ignore empty menus denoting an error
            menus.append(menu)

    return menus


def main():
    """The main function of this module."""
    parser = argparse.ArgumentParser(description='Extract lunch restaurant menus.')
    parser.add_argument('config', type=str, help='restaurant configuration file')

    args = parser.parse_args()

    try:
        with open(args.config, 'r') as conf_file:
            config = json.load(conf_file)
        all_menus = get_menus(config['restaurants'])
    except FileNotFoundError:
        print('Could not find configuration file: {}'.format(args.config))
        exit(1)

    resp = requests.post(config['backendUrl'], json=all_menus, timeout=5)
    timestamp = datetime.now().isoformat()
    if not resp.ok:
        print('{0}: Menu extraction failed'.format(timestamp))
    else:
        status = resp.json()
        if status['status'] == 'success':
            print('{}: Menu extraction succeeded'.format(timestamp))
        else:
            print('{}: Menu extraction failed, error: {}'.
                  format(timestamp, status['cause']))


if __name__ == '__main__':
    main()
