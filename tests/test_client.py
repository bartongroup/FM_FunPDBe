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

from unittest import TestCase
from unittest import mock
from funpdbe_client.client import Client


class MockUser(object):

    def __init__(self):
        self.user_name = "foo"
        self.user_pwd = "bar"

    def set_user(self):
        return True

    def set_pwd(self):
        return True


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.text = "foo"
            self.json_data = json_data
            self.status_code = status_code
    if args[0].endswith("resource/funsites/1abc/"):
        return MockResponse({"resource": "ok"}, 200)
    elif args[0].endswith("pdb/1abc/"):
        return MockResponse({"pdb": "ok"}, 200)
    return MockResponse(None, 404)


class TestClient(TestCase):

    def setUp(self):
        self.mock_user = MockUser()
        self.client = Client(None, self.mock_user)


    def test_help_text(self):
        self.assertIsNotNone(self.client.__str__())

    def test_get_one_no_pdb_id(self):
        self.assertIsNone(self.client.get_one(None))

    def test_pattern_mismatch(self):
        self.assertIsNone(self.client.get_one("invalid"))

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_one_with_id(self, mock):
        call = self.client.get_one("1abc")
        self.assertEqual({"pdb": "ok"}, call.json_data)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_one_with_resource(self, mock):
        call = self.client.get_one("1abc", "funsites")
        self.assertEqual({"resource": "ok"}, call.json_data)