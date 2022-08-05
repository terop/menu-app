#!/usr/bin/env python3
"""A module for accessing and scraping various lunch restaurant menus.
Menus are sent to a backend service for storage and display."""

import argparse
import json
import logging
import sys
from datetime import date, datetime, timedelta

import requests


def get_foodco_menu(name, restaurant_number, language='en'):
    """Fetches the menu for the current week of Food & Co restaurants from
    their API."""
    # NOTE! Currently untested, does not work
    menu = {}

    # pylint: disable=no-member
    url = 'https://www.foodandco.fi/modules/json/json/Index?costNumber=' \
        f'{restaurant_number}&language={language}'
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

                if day_menu['SetMenus'][i]['Price']:
                    menu[menu_date].append(day_menu['SetMenus'][i]['Price'])
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

    def get_weekday_mapping():
        """Returns a mapping between weekday name and the date matching
        the weekday."""
        days = {}
        monday = date.today()

        if monday.weekday() != 0:
            monday -= timedelta(days=monday.weekday())

        current_day = monday
        for _ in range(0, 5):
            days[current_day.strftime('%A')] = current_day.isoformat()
            current_day += timedelta(days=1)

        return days

    base_url = "https://www.sodexo.fi/en/ruokalistat/output/weekly_json/"
    day_mapping = get_weekday_mapping()
    menus = {}

    resp = requests.get(f'{base_url}{restaurant_id}')
    if not resp.ok:
        return {}

    json_menu = resp.json()
    for meal_date in json_menu['mealdates']:
        courses = []

        if len(meal_date['courses']) < 2:
            continue
        for course in meal_date['courses'].values():
            course_text = ''
            if 'category' in course:
                course_text += f'{course["category"]}: '

            course_text += course['title_fi']

            if 'price' in course:
                course_text += f' {course["price"]}'

            courses.append(course_text)

        menus[day_mapping[meal_date['date']]] = courses

    return {'name': name, 'menu': menus}


def get_menus(restaurants):
    """Returns menus of all restaurants given in the configuration.
    Restaurant types are: amica, antell, sodexo."""
    menus = []
    menu = {}

    for res in restaurants:
        if res['type'] == 'foodco':
            if 'language' in res:
                menu = get_foodco_menu(res['name'], res['restaurantNumber'],
                                       language=res['language'])
            else:
                menu = get_foodco_menu(res['name'], res['restaurantNumber'])
        elif res['type'] == 'sodexo':
            menu = get_sodexo_menu(res['name'], res['id'])

        if len(menu) >= 1 and len(menu['menu']) >= 1:
            # Ignore empty menus denoting an error
            menus.append(menu)

    return menus


def main():
    """The main function of this module."""
    logging.basicConfig(filename='menu_scraper.log',
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    config_file = 'menu_scraper_config.json'

    parser = argparse.ArgumentParser(description='Extract lunch restaurant menus.')
    parser.add_argument('--config', dest='config',
                        help=f'config file to use, default is {config_file}')

    args = parser.parse_args()
    if args.config:
        config_file = args.config

    try:
        with open(config_file, 'r', encoding='utf-8') as conf_file:
            config = json.load(conf_file)
            all_menus = get_menus(config['restaurants'])
    except FileNotFoundError:
        logging.error('Could not find configuration file: %s', config_file)
        sys.exit(1)

    resp = requests.post(f'{config["backendUrl"]}/add', json=all_menus, timeout=5)
    if not resp.ok:
        logging.error('Menu extraction failed, HTTP status code: %s',
                      str(resp.status_code))
    else:
        status = resp.json()
        if status['status'] == 'success':
            logging.info('Menu extraction succeeded')
        else:
            logging.error('Menu extraction failed, error: %s. Check server log.',
                          status['cause'])


if __name__ == '__main__':
    main()
