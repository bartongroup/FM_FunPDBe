# Copyright 2018 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.

import unittest
from client.funpdbe_client import Schema
from client.funpdbe_client import User
from client.funpdbe_client import Client


class TestSchema(unittest.TestCase):

    def setUp(self):
        self.schema = Schema()

    def test_validate_json_with_missing_schema(self):
        self.schema.json_schema = ""
        self.assertFalse(self.schema.validate_json({"foo": "bar"}))

    def test_validate_json_with_missing_data(self):
        self.schema.json_schema = {"foo": "bar"}
        self.assertFalse(self.schema.validate_json(None))

    def test_validate_json(self):
        self.schema.json_schema = {"foo": "bar"}
        self.assertTrue(self.schema.validate_json({"foo": "bar"}))


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User("foo", "bar")

    def test_setting_user_name(self):
        self.assertIsNotNone(self.user.user_name)

    def test_setting_password(self):
        self.assertIsNotNone(self.user.user_pwd)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client("user", "pwd")

    def test_parse_missing_json(self):
        self.assertFalse(self.client.parse_json(""))
