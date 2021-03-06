import re
import db_utils # See bot/__init__.py for a note about this

from discord.ext import commands

from . import bot_utils

class Karma(commands.Cog, name='Karma'):
    """
    Karma module

    Stores "karma" for words or underscore-separated strings. For example, you can say 'something++' to give the word 'something' some karma. Similarly, you can use 'something--' to remove karma. Multiple words should be separated by underscores like 'something_else'. The !karma command can be used to look up the current value.
    """

    karma_add_re = re.compile('(.*)\+\+$', re.IGNORECASE | re.DOTALL)
    karma_subtract_re = re.compile('(.*)--$', re.IGNORECASE | re.DOTALL)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if bot_utils.should_ignore(message, self.bot):
            return

        if (m := re.match(self.karma_add_re, message.content)) is not None:
            text = m.group(1)
            space_pos = text.rfind(' ')
            if space_pos != -1:
                text = text[space_pos:]
            db_utils.set_karma(self.bot.db, text.lower(), message.author.name, True)

        elif (m := re.match(self.karma_subtract_re, message.content)) is not None:
            text = m.group(1)
            space_pos = text.rfind(' ')
            if space_pos != -1:
                text = text[space_pos:]
            db_utils.set_karma(self.bot.db, text.lower(), message.author.name, False)

    @commands.command()
    async def karma(self, ctx, text=None):
        """
        Looks up the karma for a word or underscore-separated string.
        For example, !karma something or !karma something_something
        """
        if not text:
            await ctx.reply(f'Did you mean to put some text to get karma for? Try !help karma')
            return

        res = db_utils.get_karma(self.bot.db, text.lower())
        await ctx.reply(f'{text} has a karma of {res}')
