# menu-app
This is a simple application for displaying lunch restaurant menus.
Several restaurants are supported but each new restaurant usually requires new
code to parse or get the restaurant's menu.

## Running
The `menu_scraper.py` script in the `scraper` directory is used fetch the menus.
Fetching either means screen scraping or accessing an API, this depends on
the restaurant in question. A sample scraper configuration is available in
`scraper_config.json_sample`.

The backend is started by running the `menu.py` file located in the `app`
directory. Its configuration is called `menu.cfg`, a sample configuration can
be seen in `menu.cfg_sample`.

### Docker
The backend can be run with Docker or Podman. To build the image run the
`make build` command in the `app` directory. The image will be called `menu-app`.

## License
Released under the MIT license. See LICENSE for the full license.
