# menu-app
A simple application for displaying lunch restaurant menus. Currently only Amica and Katri Antell restaurants are supported.

## Running
The `menu_scraper.py` script is used fetch the menus. Fetching either means screen scraping or accessing an API, this depends on
the restaurant in question. A sample scraper configuration can be seen in `scraper_config.json`.

The backend is started by running the `menu.py` file. Its configuration is called `menu.cfg`, a sample configuration can
be seen in `menu.cfg_sample`.

Both applications use Python 3. If you experience strange errors when running either application, please check that you
are using the correct Python version.

## License
Release under the MIT license. See LICENSE for the full license.
