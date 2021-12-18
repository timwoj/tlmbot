import discord
import sys
import ../db_utils

config_file = open('../config.json')
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

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'Logged in as {client.user}')

@bot.event
async def on_message(message):
    if message.author == client.user:
        return

    for url in re.finditer(url_re, message.content):
        result = db_utils.store_url(url_re, message.author.nick)

        # If we got back something from the database, that means this URL is
        # OFN and we should say something.
        if result:
            message.reply(f"OFN (originally pasted by {result['paster']} on {result['when']})."

bot.run(config_file.get('discord',{}).get('token',''))
