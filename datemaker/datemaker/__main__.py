"""
main file for calling module
"""
import argparse
import os

from service import DateMakerService

if __name__ == "__main__":
    """
    Parsing command line arguments, env variables and running DateMaker service.
    """

    parser = argparse.ArgumentParser(description="Arguments for DateMaker service.")

    parser.add_argument('--debug', action='store_true', help='If debug logging needed')

    args = parser.parse_args()
    # all parameters from GoogleMeetApiController

    # all parameters from RabbitMQConnector (0.0.3)
    message_broker_host = os.getenv('RABBITMQ_HOST', 'localhost')
    message_broker_port = int(os.getenv('RABBITMQ_PORT', '5672'))
    message_broker_virtual_host = os.getenv('RABBITMQ_VIRTUAL_HOST', '/')
    message_broker_exchange = os.getenv('DATEMAKER_RABBITMQ_EXCHANGE', 'default_exchange')
    message_broker_queue = os.getenv('DATEMAKER_RABBITMQ_QUEUE', 'default_queue')
    message_broker_routing_key = os.getenv(
        'DATEMAKER_RABBITMQ_ROUTING_KEY',
        'default_routing_key'
    )
    message_broker_username = os.getenv('RABBITMQ_USERNAME', 'guest')
    message_broker_password = os.getenv('RABBITMQ_PASSWORD', 'guest')

    service = DateMakerService(
        # all parameters from GoogleMeetApiController

        # all parameters from RabbitMQConnector (0.0.3)
        message_broker_host=message_broker_host,
        message_broker_port=message_broker_port,
        message_broker_virtual_host=message_broker_virtual_host,
        message_broker_exchange=message_broker_exchange,
        message_broker_queue=message_broker_queue,
        message_broker_routing_key=message_broker_routing_key,
        message_broker_username=message_broker_username,
        message_broker_password=message_broker_password,
        # other
        debug=getattr(args, 'debug', False)
    )
    service.run()
