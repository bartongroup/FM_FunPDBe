from unittest import TestCase
from unittest.mock import patch
from funpdbe_client.user import User


class TestUser(TestCase):

    def setUp(self):
        self.user = User('foo', 'bar')

    def test_set_user(self):
        self.user.set_user()
        self.assertEqual('foo', self.user.user_name)

    def test_set_pwd(self):
        self.user.set_pwd()
        self.assertEqual('bar', self.user.user_pwd)

    def test_set_attribute(self):
        with patch('builtins.input', side_effect='f'):
            new_value = self.user.set_attribute(None, 'user prompt message')
        self.assertEqual('f', new_value)