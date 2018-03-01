#!/usr/bin/env python3

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

import os
from unittest import TestCase
from funpdbe_client.control import Control


class MockUser(object):

    def __init__(self):
        self.user_name = None
        self.user_pwd = None


class MockObject(object):

    def __init__(self, mock_user):
        self.user = mock_user
        self.schema = None
        self.pwd = None


class MockClient(object):

    def __init__(self):
        pass

    @staticmethod
    def get_one(arg1, arg2):
        return True

    @staticmethod
    def get_all(arg1):
        return True

    @staticmethod
    def post(arg1, arg2):
        return True

    @staticmethod
    def put(arg1, arg2, arg3):
        return True

    @staticmethod
    def delete_one(arg1, arg2):
        return True


class TestControl(TestCase):

    def setUp(self):
        mock_opts = [("--user", "test"), ("--pwd", "test")]
        self.control = Control(mock_opts, MockObject(MockUser()))

    def test_run_no_mode(self):
        self.assertIsNone(self.control.run())

    def test_run_no_mode(self):
        self.control.debug = True
        self.assertIsNone(self.control.run())
        self.control.debug = False
        self.assertIsNone(self.control.run())

    def test_run_help(self):
        mock_opts = [("--help", "help"), ("--debug", "debug")]
        self.control = Control(mock_opts, MockObject(MockUser()))
        self.control.process_options()
        self.assertIsNone(self.control.run())

    def mock_function(self):
        return True

    def test_run(self):
        self.control.get = self.mock_function
        self.control.mode = "get"
        self.assertTrue(self.control.run())
        self.control.put = self.mock_function
        self.control.mode = "put"
        self.assertTrue(self.control.run())
        self.control.post = self.mock_function
        self.control.mode = "post"
        self.assertTrue(self.control.run())
        self.control.delete = self.mock_function
        self.control.mode = "delete"
        self.assertTrue(self.control.run())
        self.control.mode = "foo"
        self.assertIsNone(self.control.run())

    def test_get(self):
        self.control.client = MockClient()
        self.assertIsNotNone(self.control.get())
        self.control.pdb_id = "foo"
        self.assertIsNotNone(self.control.get())

    def test_post(self):
        self.control.client = MockClient()
        self.assertIsNone(self.control.post())
        self.control.path = ".json"
        self.assertIsNotNone(self.control.post())
        os.system("touch foo.json")
        self.control.path = "./"
        self.assertIsNotNone(self.control.post())
        os.system("rm foo.json")

    def test_put(self):
        self.control.client = MockClient()
        self.assertIsNone(self.control.put())
        self.control.path = ".json"
        self.assertIsNotNone(self.control.put())

    def test_delete(self):
        self.control.client = MockClient()
        self.assertIsNotNone(self.control.delete())

    def test_process_options(self):
        mock_opts = [("--user", "test"),
                     ("--pwd", "test"),
                     ("--mode", "test"),
                     ("--pdb_id", "test"),
                     ("--resource", "test"),
                     ("--path", "test"),
                     ("--debug", "debug"),
                     ("--foo", "bar")]
        self.control = Control(mock_opts, MockClient())
        self.control.process_options()
        self.assertIsNotNone(self.control.user_name)
        self.assertIsNotNone(self.control.pwd)
        self.assertIsNotNone(self.control.mode)
        self.assertIsNotNone(self.control.pdb_id)
        self.assertIsNotNone(self.control.path)
        self.assertIsNotNone(self.control.resource)


