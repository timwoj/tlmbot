import discord

from datetime import datetime
from discord.ext import commands

from . import karma, bot_utils, urls

# Importing this requires adding the top-level repo path the PYTHONPATH. Currently
# I'm doing this by creating a tlmbot.pth file in venv/lib/<python_version>/site-packages
# which contains just the path to the directory. I've tried doing
# 'from .. import db_utils' but python complains and I don't feel like figuring
# out the correct pythonic way to do it.
import db_utils

class TLMBot(commands.Bot):

    def __init__(self, config, *args, **kwargs):

        super().__init__(command_prefix='!',
                         help_command=commands.MinimalHelpCommand(dm_help=True),
                         *args, **kwargs)

        self.config = config
        self.db = db_utils.connect(self.config.get('database_file',''), False)
        if not self.db:
            # TODO: this doesn't actually exit, for some reason. It probably needs
            # to nuke the other thread somehow.
            sys.exit(1)

        self.start_time = datetime.now()

        self.add_cog(karma.Karma(self))
        self.add_cog(urls.URLStorage(self))

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        # Run this first so that commands get processed correctly. Everything else
        # can be processed after. Also, this should only ever be run in the main
        # bot class. Otherwise you get duplicate responses to commands.
        await self.process_commands(message)

        if bot_utils.should_ignore(message, self):
            return

def startup(config):
    bot = TLMBot(config=config)
    bot.run(config.get('discord',{}).get('token',''))

if __name__ == '__main__':
    startup()
