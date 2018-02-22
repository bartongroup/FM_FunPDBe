from unittest import TestCase
from unittest.mock import patch
from funpdbe_client.user import User


class TestUser(TestCase):

    def setUp(self):
        self.user = User("foo", "bar")

    def test_set_user(self):
        self.user.user_name = None
        with patch('builtins.input', side_effect="f"):
            self.user.set_user()
        self.assertEqual("f", self.user.user_name)

    def test_set_pwd(self):
        self.user.user_pwd = None
        with patch('builtins.input', side_effect="f"):
            self.user.set_pwd()
        self.assertEqual("f", self.user.user_pwd)