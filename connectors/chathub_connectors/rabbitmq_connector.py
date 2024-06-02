import json
import logging
from typing import Optional
from pika import PlainCredentials, ConnectionParameters

from pika.adapters.asyncio_connection import AsyncioConnection

MATCHMAKER_RK = 'matchmaker'
EXCHANGE_PROD = 'direct_main_prod'
EXCHANGE_DEV = 'direct_main_dev'

LOGGER = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)


class RabbitMQConnector:
    def __init__(
            self,
            host: str = 'localhost',
            virtual_host: str = 'chathub',
            port: int = 8082,
            username: Optional[str] = None,
            password: Optional[str] = None,
            loglevel: Optional[str] = logging.DEBUG,
    ):
        LOGGER.setLevel(loglevel)
        self._exchange = EXCHANGE_DEV if loglevel == logging.DEBUG else EXCHANGE_PROD
        creds = PlainCredentials(
            username=username,
            password=password
        )
        self._connection = AsyncioConnection(
            parameters=ConnectionParameters(
                host=host,
                port=port,
                virtual_host=virtual_host,
                credentials=creds,
            ),
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_oper_error
        )
        self._channel = None
        LOGGER.info('RabbitMQ connector initialized')
        try:
            if not self._connection.ioloop.is_running():
                LOGGER.debug('Starting ioloop')
                self._connection.ioloop.run_forever()
            else:
                LOGGER.debug('Ioloop is already running')
        except KeyboardInterrupt:
            if self._channel:
                self._channel.close()
                LOGGER.info('Channel closed')
            self._connection.close()
            LOGGER.info('Connection closed')

    def add_user_to_matchmaking_queue(self, username: str):
        self._publish(
            message=json.dumps({'command': 'add_user_to_matchmaking_queue', 'data': username}),
            routing_key=MATCHMAKER_RK,
            exchange=self._exchange
        )

    def _publish(self, message: str, routing_key: str, exchange: str):
        if self._channel.is_open:
            self._channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
            LOGGER.debug(
                f'Message {message[:10]} (RK {routing_key}) published to exchange {exchange}'
            )
        else:
            LOGGER.warning('Cannot publish message because channel is not open')

    def _on_connection_open(self, _):
        LOGGER.debug('RMQ connection opened')
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_oper_error(self, _, err):
        LOGGER.error(f'RabbitMQ connection open error: {err}')

    def _on_channel_open(self, channel):
        self._channel = channel
        LOGGER.debug('RMQ channel opened')
