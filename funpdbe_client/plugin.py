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

from funpdbe_client.client import Client
from funpdbe_client.user import User
from funpdbe_client.schema import Schema


class Plugin(object):

    def __init__(self, user, pwd, data):
        self.user = user
        self.pwd = pwd
        self.data = data
        self.resource = self.set_value("data_resource")
        self.pdb_id = self.set_value("pdb_id")
        self.client = self.initialize_client()

    def set_value(self, key):
        if self.check_if_key_exists(key):
            return self.data[key]
        return None

    def check_if_key_exists(self, key):
        if key in self.data.keys():
            return True
        return False

    def post(self, update=False):
        if not self.check_if_variables_are_set():
            print("POSTing failed due to missing information")
            return False
        self.client.json_data = self.data
        if update:
            self.client.delete_one(self.pdb_id, self.resource)
        self.client.post(path=None, resource=self.resource, plugin=True)
        return True

    def check_if_variables_are_set(self):
        for variable in [self.user, self.pwd, self.data, self.resource, self.pdb_id]:
            if not variable:
                print("Fatal: please check if user name, password and data are all provided!")
                return False
        return True

    def initialize_client(self):
        schema = Schema()
        user = self.initialize_user()
        return Client(schema, user)

    def initialize_user(self):
        return User(user=self.user, pwd=self.pwd)
