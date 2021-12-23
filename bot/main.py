import discord
import sys
import json
import re
from pathlib import Path # if you haven't already done so

# Add the parent path to sys.path so we can search for modules in it
# for utility code, plus get the root path to find the config file.
script_file = Path(__file__).resolve()
root_path = script_file.parents[1]
sys.path.append(str(root_path))

import db_utils

config_file = open(root_path.joinpath('config.json'))
config = json.load(config_file)

if not config:
    print('Failed to load config file')
    sys.exit(1)

db = db_utils.connect(config['database_file'])
if not db:
    sys.exit(1)

# This probably isn't a perfectly ideal regexp, but it'll
# work to start with.
url_re = re.compile('(https?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE | re.DOTALL)

bot = discord.Client()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for url in re.finditer(url_re, message.content):
        print(f'found a url: {url.group(0)}')
        print(f'from: {message.author}')

        # This stores the actual username instead of the nick so then we can
        # look it up again against the current list of users when we report
        # OFN.
        # TODO: implement that lookup
        result = db_utils.store_url(db, url.group(0), message.author.name)

        # If we got back something from the database, that means this URL is
        # OFN and we should say something.
        if result:
            await message.reply(f"OFN (originally pasted by {result['paster']} on {result['when']}).")

bot.run(config.get('discord',{}).get('token',''))
