import subprocess
import humanize
import random

from datetime import datetime
from discord.ext import commands

class Others(commands.Cog, name='Others'):

    """
    Others module

    Other random commands that don't fit neatly into one of the other modules
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cookies(self, ctx):
        """
        Info on Girl Scout cookies!
        """
        choices = [
            'You know you want some cookies!',
            'COOOKIIEEES OM NOM NOM NOM',
            'Get some!']
        await ctx.reply(content=f'{random.choice(choices)}\n'
                        'https://digitalcookie.girlscouts.org/scout/julia229799')

    @commands.command()
    async def uptime(self, ctx):
        """
        Reports uptime and some statistics about the bot's runtime.
        """
        uptime = datetime.now() - self.bot.start_time
        uptime_str = humanize.precisedelta(uptime, minimum_unit='seconds')

        result = subprocess.run(['git','log','--format="%C(auto) %h %s"','-1'],
                                capture_output=True)
        git_str = result.stdout.decode('ascii')

        response = f'TLMBot has been up for {uptime_str}. It is currently running from commit {git_str}'
        await ctx.reply(content=response)
