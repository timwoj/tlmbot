# tlmbot
A simple Discord bot for Threat Level Midnight

## Features

- URL Scraper: the bot records any http/https/ftp URL pasted in the public channels
- Karma: `++` and `--` on words will give those words karma. For example:

![2021-12-28 15_35_24-general - Discord](https://user-images.githubusercontent.com/2653616/147612165-181ac404-f5fd-4a42-9ff1-d345c7a375da.png)

## Discord bits (in the `bot` directory)

- Powered by [pycord](https://github.com/Pycord-Development/pycord)
- Stores data in an SQLite3 database

## Web bits (in the `web` directory)

- Powered by [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- Loads data from the same SQLite3 database for display in a browser
- Presents the following endpoints:
  - `/urls`: Filterable/searchable list of URLs pasted into discord

## Future projects

- TLM Lore repository
