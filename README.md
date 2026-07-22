# menu-app
This is a simple application for displaying lunch restaurant menus.
Several restaurants are supported but each new restaurant usually requires new
code to parse or get the restaurant's menu.

## Running
The `menu_scraper.py` script in the `scraper` directory is used fetch the menus.
Fetching either means screen scraping or accessing an API, this depends on
the restaurant in question. A sample scraper configuration is available in
`config.toml.sample`.

The backend is started by running the `menu.py` file located in the `app`
directory. Its configuration is called `config.toml`, a sample configuration can
be seen in `config.toml.sample`.

### Docker
The backend can be run with Docker or Podman. To build the image run the
`just build` command in the `app` directory. The image will be called `menu-app`.

## License
Released under the MIT license. See LICENSE for the full license.
