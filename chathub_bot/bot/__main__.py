"""
main file for calling module
"""
import argparse

from bot import TG_TOKEN
from .bot import main

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

    main(TG_TOKEN, getattr(args, 'long_polling', False), getattr(args, 'debug', False))
