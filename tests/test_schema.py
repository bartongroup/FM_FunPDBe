import unittest
from funpdbe_client.schema import Schema


class TestSchema(unittest.TestCase):

    def setUp(self):
        self.schema = Schema()

    def test_get_schema(self):
        self.schema.get_schema()
        self.assertIsNotNone(self.schema.json_schema)

    def test_get_schema_bad_data(self):
        self.schema.json_url = "https://www.ebi.ac.uk"
        self.schema.get_schema()
        self.assertIsNone(self.schema.json_schema)

    def test_validate_json_with_missing_schema(self):
        mock_schema = {
            "type": "object",
            "properties": {
                "foo": {
                    "type": "string",
                    "description": "bar"
                }
            }
        }
        self.schema.json_schema = mock_schema
        self.assertFalse(self.schema.validate_json(42))

    def test_validate_json_with_missing_data(self):
        self.schema.json_schema = {"foo": "bar"}
        self.assertFalse(self.schema.validate_json(None))

    def test_validate_json(self):
        self.schema.json_schema = {"foo": "bar"}
        self.assertTrue(self.schema.validate_json({"foo": "bar"}))

    def test_clean_json(self):
        mock_data = {
            "sites": [
                {"source_database": "FOO"},
                {"source_database": "BAR"}
            ],
            "pdb_id": "1ABC"
        }
        expected = {
            "sites": [
                {"source_database": "foo"},
                {"source_database": "bar"}
            ],
            "pdb_id": "1abc"
        }
        self.assertEqual(expected, self.schema.clean_json(mock_data))
