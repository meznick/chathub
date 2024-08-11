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
    """
    This class provides a connector to the RabbitMQ server for asynchronous messaging.

    Each instance of the `RabbitMQConnector` can connect to a RabbitMQ server,
    bind to specified exchanges and queues, send and receive messages.

    Class attributes include connection details like `host`, `port`, `virtual_host`,
    `exchange`, `queue`, `routing_key`, `username`, `password` and `message_callback`.
    The class also has a `call_service` attribute that indicates the name of the service
    using the RabbitMQ connector.

    Messages are published using the `publish` method, and received messages are
    handled by the `message_callback` function if provided, or the default_on_message_callback
    method if not.

    Example:
    init_params = {
        'host': 'localhost',
        'port': 5672,
        'virtual_host': 'test',
        'callback_method': lambda x: print(x),
    }
    connector = RabbitMQConnector(**init_params)
    connector.run() # it's async
    connector.publish('message', 'some_key', 'exchange_name')
    """

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
            caller_service: str = '',
            loglevel: Optional[str] = logging.DEBUG,
    ):
        """
        Initialize the RabbitMQ connector.

        :param host: The host name or IP address of the RabbitMQ server.
                     Default is 'localhost'.
        :param port: The port number of the RabbitMQ server. Default is 8082.
        :param virtual_host: The virtual host name to connect to. Default is an empty string.
        :param exchange: The exchange name to bind to. Default is an empty string.
        :param queue: The queue name to bind to. Default is an empty string.
        :param routing_key: The routing key used for message routing. Default is an empty string.
        :param username: The username for authentication. Default is None.
        :param password: The password for authentication. Default is None.
        :param message_callback: A callback function to handle received messages. Default is None.
        :param caller_service: The name of the service using the RabbitMQ connector.
                     Default is an empty string.
        :param loglevel: The logging level for the RabbitMQ connector. Default is logging.DEBUG.
        """
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
        self.tag = f'python-rmq-connector-{caller_service}'
        LOGGER.info(f'RabbitMQ connector {self.tag} initialized')

    def run(self):
        LOGGER.info(f'Running RabbitMQ connector {self.tag}')
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

    def publish(self, message: str, routing_key: str, exchange: str):
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
            consumer_tag=self.tag,
            auto_ack=True
        )
        LOGGER.debug(f'Consuming on queue {self._queue}')

    @staticmethod
    def _default_on_message_callback(channel, method, properties, body):
        LOGGER.debug(f'Processed message by default method: {body.decode()}')
