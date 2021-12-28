import argparse
from pathlib import Path

import bot
import web
import json

script_file = Path(__file__).resolve()
root_path = script_file.parents[1]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='TLM Discord Bot')
    parser.add_argument('--config', type=str,
                        help='A path to a config file')

    args = parser.parse_args()

    config_file = open(args.config)
    config = json.load(config_file)

    if not config:
        print(f'Failed to load config file {args.config_file}')
        sys.exit(1)

    # Start up the flask instance on a separate thread so that both can
    # run at the same time.
    web_thread = web.create_thread(config)
    web_thread.start()

    # Run the bot on the main thread to make dealing with the database
    # a little less effort from within the bot.
    bot.startup(config)
