import asyncio
import logging
import unittest
from time import sleep
from unittest.mock import MagicMock, AsyncMock

from argon2.exceptions import InvalidHashError

from chathub_utils.auth import AuthProcessor


class TestAuthProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_postgres_connector = MagicMock()
        self.mock_password_hasher = MagicMock()
        self.mock_redis_connector = MagicMock()
        self.authenticate = AuthProcessor(
            self.mock_redis_connector,
            self.mock_postgres_connector,
            self.mock_password_hasher,
            'test',
            'HS256',
            logging.ERROR
        )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()
        asyncio.set_event_loop(None)

    def test_validate_username(self):
        validate_function = AuthProcessor._validate_username

        # It should validate a valid username
        self.assertTrue(validate_function('username_09'))
        # Invalid characters are not allowed
        self.assertFalse(validate_function('USERNAME_09!'))
        # username is less than 4 characters
        self.assertFalse(validate_function('US'))
        # username is more than 20 characters
        self.assertFalse(validate_function('username_09123123123123123123123'))

    def test_validate_password(self):
        validate_function = AuthProcessor._validate_password

        # Test case 1: Password fulfilling all requirements
        self.assertTrue(validate_function('Abc123@$'))
        # Test case 2: Password with less than 8 characters
        self.assertFalse(validate_function('Abc7$'))
        # Test case 3: Password with no uppercase letter
        self.assertFalse(validate_function('abc123@$'))
        # Test case 4: Password with no lowercase letter
        self.assertFalse(validate_function('ABC123@$'))
        # Test case 5: Password with no digit
        self.assertFalse(validate_function('ABCabc@$'))
        # Test case 6: Password with no special characters
        self.assertFalse(validate_function('ABCabc123'))

    def test_authenticate_user_does_not_exist(self):
        self.mock_postgres_connector.get_user = AsyncMock(return_value=None)

        res = self.loop.run_until_complete(self.authenticate._authenticate('user1', 'password1'))

        self.assertFalse(res)
        self.mock_postgres_connector.get_user.assert_called_once_with('user1')

    def test_authenticate_password_does_not_match(self):
        user_dict = {'password_hash': 'wrong_hash'}
        self.mock_postgres_connector.get_user = AsyncMock(return_value=user_dict)
        self.mock_password_hasher.verify.side_effect = InvalidHashError('Bad password')

        res = self.loop.run_until_complete(self.authenticate._authenticate('user2', 'password2'))

        self.assertFalse(res)
        self.mock_postgres_connector.get_user.assert_called_once_with('user2')
        self.mock_password_hasher.verify.assert_called_once_with('wrong_hash', 'password2')

    def test_authenticate_successful(self):
        user_dict = {'password_hash': 'good_hash'}
        self.mock_postgres_connector.get_user = AsyncMock(return_value=user_dict)
        self.mock_password_hasher.verify.return_value = True

        res = self.loop.run_until_complete(self.authenticate._authenticate('user3', 'password3'))

        self.assertTrue(res)
        self.mock_postgres_connector.get_user.assert_called_once_with('user3')
        self.mock_password_hasher.verify.assert_called_once_with('good_hash', 'password3')

    def test_validate_token_success(self):
        username = 'test'

        with self.subTest(msg='correct token no need to update'):
            self.mock_redis_connector.client.setex.return_value = None
            valid_token = self.authenticate._generate_token(username, 2)
            self.mock_redis_connector.client.get.return_value = None
            validated = self.authenticate.validate_token(valid_token, username, 0)
            self.assertEqual(valid_token, validated)

        with self.subTest(msg='correct token but expired'):
            sleep(2)
            validated = self.authenticate.validate_token(valid_token, username)
            self.assertIsNone(validated)

        with self.subTest(msg='correct token but time to update'):
            valid_token = self.authenticate._generate_token(username, 10)
            self.mock_redis_connector.client.get.return_value = None
            validated = self.authenticate.validate_token(valid_token, username, 10)
            self.assertNotEqual(valid_token, validated)
            self.assertIsNotNone(validated)

        with self.subTest(msg='correct token in cache'):
            valid_token = self.authenticate._generate_token(username, 10)
            self.mock_redis_connector.client.get.return_value = valid_token
            validated = self.authenticate.validate_token(valid_token, username, 1)
            self.assertEqual(valid_token, validated)

    def test_validate_token_mismatch(self):
        username = 'test'
        hacker_username = 'hacker'

        with self.subTest(msg='token cannot be decoded'):
            invalid_token = 'blablabla'
            self.mock_redis_connector.client.get.return_value = None
            validated = self.authenticate.validate_token(invalid_token, username)
            self.assertIsNone(validated)

        with self.subTest(msg='token is incorrect but correct token in cache'):
            invalid_token = 'blablabla'
            self.mock_redis_connector.client.get.return_value = 'correct_token'
            validated = self.authenticate.validate_token(invalid_token, username)
            self.assertIsNone(validated)

        with self.subTest(msg='token can be decoded but expired'):
            invalid_token = self.authenticate._generate_token(username, 2)
            sleep(2)
            validated = self.authenticate.validate_token(invalid_token, username)
            self.assertIsNone(validated)

        with self.subTest(msg='provided username does not match with one in token'):
            invalid_token = self.authenticate._generate_token(username)
            self.mock_redis_connector.client.get.return_value = None
            validated = self.authenticate.validate_token(invalid_token, hacker_username)
            self.assertIsNone(validated)
