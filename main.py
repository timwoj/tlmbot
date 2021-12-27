import threading

import bot
import web

if __name__ == '__main__':

    # Start up the flask instance on a separate thread so that both can
    # run at the same time.
    web_thread = web.create_thread()
    web_thread.start()

    # Run the bot on the main thread to make dealing with the database
    # a little less effort from within the bot.
    bot.startup()
