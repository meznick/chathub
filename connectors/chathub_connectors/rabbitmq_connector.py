import asyncio
import logging
from typing import Optional, Callable

import aio_pika
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection, AbstractExchange, \
    HeadersType
from pika import PlainCredentials, ConnectionParameters
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.spec import BasicProperties

from chathub_connectors import setup_logger

LOGGER = setup_logger(__name__)
LOGGER.warning(f'Logger {LOGGER} is active')


class ConnectionFailedException(Exception):
    pass


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
            port: int = 5672,
            virtual_host: str = '',
            exchange: str = '',
            queue: str = '',
            routing_key: str = '',
            username: Optional[str] = None,
            password: Optional[str] = None,
            message_callback: Callable = None,
            caller_service: str = 'standalone',
            loglevel: Optional[int] = logging.DEBUG,
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
                     Default is standalone.
        :param loglevel: The logging level for the RabbitMQ connector.
                     Default is logging.DEBUG (10).
        """
        self.set_log_level(loglevel)
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self._username = username
        self._password = password
        self._exchange = exchange
        self._queue = queue
        self._routing_key = routing_key
        self._message_callback = message_callback
        self._channel = None
        self._connection = None
        self.tag = f'python-rmq-connector-{caller_service}'
        LOGGER.info(f'RabbitMQ connector {self.tag} initialized')

    @staticmethod
    def set_log_level(loglevel):
        LOGGER.setLevel(loglevel)

    def connect(self, custom_loop: asyncio.AbstractEventLoop = None):
        self._connection = self._create_connection(custom_loop)
        if not self._connection.ioloop.is_running:
            self._connection.ioloop.run_forever()
        LOGGER.debug(
            f'Event loop state is running: {self._connection.ioloop.is_running}'
        )

    def _create_connection(self, custom_loop: asyncio.AbstractEventLoop = None):
        LOGGER.debug(f'Connecting to RabbitMQ server {self.host}')
        connection = AsyncioConnection(
            parameters=ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=PlainCredentials(
                    username=self._username,
                    password=self._password,
                ),
                stack_timeout=5,
                connection_attempts=2,
                retry_delay=2,
            ),
            on_open_callback=self._on_connection_open,
            on_close_callback=self._on_connection_closed,
            on_open_error_callback=self._on_connection_open_error,
            custom_ioloop=custom_loop
        )
        LOGGER.info(f'RabbitMQ connection to {self.host} established')
        return connection

    def disconnect(self):
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            if self._channel:
                self._connection.close()

    def publish(
            self,
            message: str,
            routing_key: str,
            exchange: str,
            properties: BasicProperties = None
    ):
        if self._channel.is_open:
            self._channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=properties
            )
            LOGGER.debug(
                f'Message "{message[:100]}..." (RK {routing_key}) published to exchange {exchange}'
            )
        else:
            LOGGER.warning('Cannot publish message because channel is not open')

    def _on_connection_open(self, _):
        LOGGER.debug('RMQ connection opened')
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_closed(self, _, reason):
        LOGGER.debug(f'RMQ connection closed because of {reason}')
        self._connection.ioloop.stop()

    def _on_channel_open(self, channel):
        LOGGER.debug('RMQ channel opened')
        self._channel = channel
        self._channel.basic_consume(
            queue=self._queue,
            on_message_callback=(
                self._message_callback
                if self._message_callback
                else self._default_on_message_callback
            ),
            consumer_tag=self.tag,
            auto_ack=True,
        )
        LOGGER.debug(f'Consuming on queue {self._queue}')

    @staticmethod
    def _on_connection_open_error(_: AsyncioConnection, err: Exception):
        LOGGER.error(f'RabbitMQ connection open error: {err}')
        raise ConnectionFailedException('RabbitMQ connection open error')

    @staticmethod
    def _default_on_message_callback(channel, method, properties, body):
        LOGGER.debug(f'Processed message by default method: {body.decode()}')


class AIORabbitMQConnector:
    def __init__(
            self,
            host: str = 'localhost',
            port: int = 5672,
            virtual_host: str = '',
            exchange: str = '',
            routing_key: str = '',
            username: Optional[str] = None,
            password: Optional[str] = None,
            caller_service: str = 'standalone',
            loglevel: Optional[int] = logging.DEBUG,
    ):
        LOGGER.setLevel(loglevel)
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self._username = username
        self._password = password
        self.exchange = exchange
        self.routing_key = routing_key
        self.connection: AbstractRobustConnection | None = None
        self.tag = f'python-aio-rmq-connector-{caller_service}'
        self.channel: AbstractRobustChannel | None = None

    async def connect(self, custom_loop: Optional[asyncio.AbstractEventLoop] = None):
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            virtualhost=self.virtual_host,
            login=self._username,
            password=self._password,
            loop=custom_loop,
        )
        LOGGER.info(f'RabbitMQ connection to {self.host}/{self.virtual_host} established')

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        LOGGER.debug(f'RabbitMQ channel {self.channel} opened')

    async def listen_queue(self, queue_name: str, callback: Callable):
        queue = await self.channel.get_queue(queue_name)
        LOGGER.info(f'Listening for queue {queue_name}...')
        await queue.consume(callback=callback, consumer_tag=self.tag)

    async def publish(
            self,
            message: str,
            routing_key: str,
            exchange: str,
            headers: Optional[HeadersType] = None
    ):
        exchange: AbstractExchange = await self.channel.get_exchange(exchange)
        await exchange.publish(
            routing_key=routing_key,
            message=aio_pika.Message(
                body=message.encode(),
                headers=headers,
            ),
        )
        LOGGER.debug(
            f'Message "{message[:100]}..." (RK {routing_key}) published to exchange {exchange}'
        )
