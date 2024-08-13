"""
main file for calling module
"""
import argparse
import asyncio

from bot import TG_TOKEN, LOGGER
from .bot import DatingBot

if __name__ == "__main__":
    """
    Parsing command line arguments, env variables and running DateMaker service.
    """

    parser = argparse.ArgumentParser(description="Arguments for DateMaker service.")

    parser.add_argument('--debug', action='store_true', help='If debug logging needed')
    parser.add_argument(
        '--long-polling',
        action='store_true',
        help='To properly run while developing'
    )

    args = parser.parse_args()

    dating_bot = DatingBot(tg_token=TG_TOKEN, debug=getattr(args, 'debug', False))
    LOGGER.debug('Preparing to run bot...')
    if getattr(args, 'long_polling', False):
        LOGGER.debug('Running in long polling mode...')
        asyncio.run(dating_bot.start_long_polling())
    else:
        LOGGER.debug('Running in webhook mode...')
        asyncio.run(dating_bot.start_webhook())
