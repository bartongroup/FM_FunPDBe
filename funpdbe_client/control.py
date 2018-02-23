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

import logging
import glob
from funpdbe_client.client import Client
from funpdbe_client.schema import Schema
from funpdbe_client.user import User


class Control(object):

    def __init__(self, opts):
        self.opts = opts
        self.user = None
        self.pwd = None
        self.mode = None
        self.pdb_id = None
        self.resource = None
        self.path = None
        self.debug = False
        self.help = False

    def run(self):
        self.process_options()
        if self.help:
            print(Client(schema=None, user=None))
            return None

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        if not self.mode:
            logging.error("Running mode not specified")
            return None

        user = User(self.user, self.pwd)
        schema = Schema()
        client = Client(schema=schema, user=user)

        if self.mode == "get":
            if self.pdb_id:
                client.get_one(self.pdb_id, self.resource)
            else:
                client.get_all(self.resource)
        elif self.mode == "post":
            if self.path.endswith(".json"):
                client.post(self.path, self.resource)
            else:
                for json_path in glob.glob("%s/*.json" % self.path):
                    client.post(json_path, self.resource)
                    client.json_data(None)
        elif self.mode == "put":
            client.put(self.path, self.pdb_id, self.resource)
        elif self.mode == "delete":
                client.delete_one(self.pdb_id, self.resource)

    def process_options(self):
        for option, value in self.opts:
            if option in ["-u", "--user"]:
                self.user = value
            elif option in ["-p", "--pwd"]:
                self.pwd = value
            elif option in ["-m", "--mode"]:
                self.mode = value
            elif option in ["-i", "--pdb_id"]:
                self.pdb_id = value
            elif option in ["-r", "--resource"]:
                self.resource = value
            elif option in ["-f", "--path"]:
                self.path = value
            elif option in ["-h", "--help"]:
                self.help = True
            elif option in ["-d", "--debug"]:
                self.debug = True
            else:
                assert False, "unhandled option"
