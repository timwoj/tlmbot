import re
import db_utils # See bot/__init__.py for a note about this

from discord.ext import commands
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from . import bot_utils

class URLStorage(commands.Cog, name='URLs'):

    """
    URLStorage module

    This module listens to messages posted in the channel, looking for http and https links, and saves them off into a database for later viewing. You can look at this list at http://madleet.com/tlm, which includes filtering and searching.
    """

    # This probably isn't a perfectly ideal regexp, but it'll
    # work to start with.
    url_re = re.compile(
        '(https?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        re.IGNORECASE | re.DOTALL)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if bot_utils.should_ignore(message, self.bot):
            return

        for url in re.finditer(self.url_re, message.content):
            print(f'found a url: {url.group(0)}')
            print(f'from: {message.author}')

            # This stores the actual username instead of the nick so then we can
            # look it up again against the current list of users when we report
            # OFN.
            # TODO: implement that lookup
            result = db_utils.store_url(self.bot.db, url.group(0), message.author.name)

            # If we got back something from the database, that means this URL is
            # OFN and we should say something.
            if result:
                when = datetime.fromisoformat(f"{result['when']}")
                utc = ZoneInfo('UTC')
                est = ZoneInfo('America/New_York')
                when = when.replace(tzinfo=utc).astimezone(est)
                when_str = when.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                await message.reply(f"OFN (originally pasted by {result['paster']} on {when_str}).")

    @commands.command()
    async def urls(self, ctx):
        """
        Returns the link to the URL page.
        """
        await ctx.reply(f'Were you looking for https://madleet.com/tlm ?')
