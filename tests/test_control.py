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

from unittest import TestCase
from funpdbe_client.control import Control

class TestControl(TestCase):

    def setUp(self):
        mock_opts = [("--user", "test"), ("--pwd", "test")]
        self.control = Control(mock_opts)

    def test_run_no_mode(self):
        self.assertIsNone(self.control.run())

    def test_run_get(self):
        self.control.mode = "get"
        self.control.run()

    def test_get(self):
        self.control.user = "test"
        self.control.pwd = "test"
        self.assertIsNotNone(self.control.get())

    def test_get_with_pdb_id(self):
        self.control.user = "test"
        self.control.pwd = "test"
        self.pdb_id = "1abc"
        self.assertIsNotNone(self.control.get())
