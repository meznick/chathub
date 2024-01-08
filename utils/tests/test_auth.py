import unittest

from chathub_utils.auth import AuthProcessor


class TestUsernameValidation(unittest.TestCase):
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

    # todo: add tests for auth class methods
