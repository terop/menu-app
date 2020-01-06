# menu-app
A simple application for displaying lunch restaurant menus. Several restaurants are supported but each
new restaurant usually requires new code to parse or get the restaurant's menu.

## Running
The `menu_scraper.py` script is used fetch the menus. Fetching either means screen scraping or accessing an API, this depends on
the restaurant in question. A sample scraper configuration can be seen in `scraper_config.json_sample`.

The backend is started by running the `menu.py` file. Its configuration is called `menu.cfg`, a sample configuration can
be seen in `menu.cfg_sample`.

Both applications use Python 3. If you experience strange errors when running either application, please check that you
are using the correct Python version.

### Docker
The backend can be run with Docker. To build the image run the `make build` command in the `app` directory.
The image will be called `menu-app`.

The image is run with `docker run -d --restart always -p <target port>:5000 --name <container name> menu-app:latest`, replace `<targe port>` with the port to be exposed and `<container name>` with the desired name.

## License
Released under the MIT license. See LICENSE for the full license.
