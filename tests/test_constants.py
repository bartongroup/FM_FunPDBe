from unittest import TestCase
from funpdbe_client.constants import Constants


class TestConstants(TestCase):

    def setUp(self):
        self.constants = Constants()

    def test_get_api_url(self):
        self.assertIsNotNone(self.constants.get_api_url())

    def test_get_resources(self):
        self.assertIsNotNone(self.constants.get_resources())

    def test_get_pattern(self):
        self.assertIsNotNone(self.constants.get_pdb_id_pattern())
