# Importing Required Libraries
from unittest.mock import patch, MagicMock

from pika import ConnectionParameters, PlainCredentials


# Defining Test Class
class TestRabbitMQConnector:
    default_init_parameters = {
        'host': 'localhost', 'virtual_host': 'chathub', 'port': 8082,
        'username': None, 'password': None, 'loglevel': 10
    }

    @patch('pika.adapters.asyncio_connection.AsyncioConnection', new_callable=MagicMock)
    def test_init(self, mock_asyncio_connection):
        test_parameters = {
            'host': 'test host', 'virtual_host': 'test host', 'port': 123,
            'username': 'test username', 'password': 'test password',
            'loglevel': 20, 'exchange': 'test_exchange', 'routing_key': 'test_routing_key',
            'queue': 'test_queue'
        }
        mock_connection = mock_asyncio_connection.return_value
        mock_connection.connect.return_value = mock_connection
        mock_connection.ioloop = MagicMock()
        from chathub_connectors.rabbitmq_connector import RabbitMQConnector
        connector = RabbitMQConnector(**test_parameters)
        assert connector._exchange == 'test_exchange'
        mock_asyncio_connection.assert_called_once_with(
            parameters=ConnectionParameters(
                host='test host', port=123, virtual_host='test host',
                credentials=PlainCredentials('test username', 'test password')),
            on_open_callback=connector._on_connection_open,
            on_open_error_callback=connector._on_connection_open_error
        )
