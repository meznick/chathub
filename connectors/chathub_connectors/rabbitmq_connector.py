import json
import logging
from typing import Optional, Callable

from pika import PlainCredentials, ConnectionParameters
from pika.adapters.asyncio_connection import AsyncioConnection

MATCHMAKER_RK = 'matchmaker'

LOGGER = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)


class RabbitMQConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 8082,
            virtual_host: str = '',
            exchange: str = '',
            queue: str = '',
            routing_key: str = '',
            username: Optional[str] = None,
            password: Optional[str] = None,
            message_callback: Callable = None,
            loglevel: Optional[str] = logging.DEBUG,
    ):
        LOGGER.setLevel(loglevel)
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
                stack_timeout=2,
                connection_attempts=2,
                retry_delay=2
            ),
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error
        )
        self._exchange = exchange
        self._queue = queue
        self._routing_key = routing_key
        self._message_callback = message_callback
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

    def _on_connection_open_error(self, _, err):
        LOGGER.error(f'RabbitMQ connection open error: {err}')
        exit(1)

    def _on_channel_open(self, channel):
        self._channel = channel
        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=(
                self._message_callback
                if self._message_callback
                else self._default_on_message_callback
            ),
            auto_ack=True
        )
        LOGGER.debug('RMQ channel opened')

    @staticmethod
    def _default_on_message_callback(channel, method, properties, body):
        LOGGER.debug(f'Processed message by default method: {body.decode()}')
