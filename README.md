# tlmbot
A simple Discord bot for Threat Level Midnight

## Features

- URL Scraper: the bot records any URL pasted in the public channels
- Lore: The TLM Lore project

## Discord bits (in the `bot` directory)

- Powered by [pycord](https://github.com/Pycord-Development/pycord)
- Stores data in an SQLite3 database

## Web bits (in the `web` directory)

- Powered by [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- Presents two endpoints:
  - `/urls`: Filterable/searchable list of URLs pasted into discord
  - `/lore`: The TLM Lore project