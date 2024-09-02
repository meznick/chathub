"""
main file for calling module
"""
import argparse
import asyncio

from datemaker import (
    MESSAGE_BROKER_HOST, MESSAGE_BROKER_PORT,
    MESSAGE_BROKER_VIRTUAL_HOST, MESSAGE_BROKER_EXCHANGE, MESSAGE_BROKER_QUEUE,
    MESSAGE_BROKER_ROUTING_KEY, MESSAGE_BROKER_USERNAME, MESSAGE_BROKER_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
)
from .service import DateMakerService

if __name__ == "__main__":
    """
    Parsing command line arguments, env variables and running DateMaker service.
    """

    parser = argparse.ArgumentParser(description="Arguments for DateMaker service.")
    parser.add_argument('--debug', action='store_true', help='If debug logging needed')
    args = parser.parse_args()

    service = DateMakerService(
        # all parameters from GoogleMeetApiController

        # all parameters from RabbitMQConnector (0.0.3)
        message_broker_host=MESSAGE_BROKER_HOST,
        message_broker_port=MESSAGE_BROKER_PORT,
        message_broker_virtual_host=MESSAGE_BROKER_VIRTUAL_HOST,
        message_broker_exchange=MESSAGE_BROKER_EXCHANGE,
        message_broker_queue=MESSAGE_BROKER_QUEUE,
        message_broker_routing_key=MESSAGE_BROKER_ROUTING_KEY,
        message_broker_username=MESSAGE_BROKER_USERNAME,
        message_broker_password=MESSAGE_BROKER_PASSWORD,
        # all parameters for AsyncPgConnector
        postgres_host=POSTGRES_HOST,
        postgres_port=POSTGRES_PORT,
        postgres_db=POSTGRES_DB,
        postgres_user=POSTGRES_USER,
        postgres_password=POSTGRES_PASSWORD,
        # other
        debug=getattr(args, 'debug', False)
    )

    asyncio.run(service.run())
