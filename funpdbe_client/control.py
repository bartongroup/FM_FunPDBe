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


class Control(object):

    def __init__(self, opts, client, schema, user):
        self.opts = opts
        self.client = client
        self.user = user
        self.schema = schema
        self.user_name = None
        self.pwd = None
        self.mode = None
        self.pdb_id = None
        self.resource = None
        self.path = None
        self.debug = False
        self.help = False

    def run(self):
        logging.basicConfig(level=logging.INFO)
        self.process_options()
        self.configure()

        if not self.mode:
            logging.error("Running mode not specified")
            return None

        if self.mode == "get":
            return self.get()
        elif self.mode == "post":
            return self.post()
        elif self.mode == "put":
            return self.put()
        elif self.mode == "delete":
            return self.delete()
        else:
            return None

    def configure(self):
        self.user.user_name = self.user_name
        self.user.user_pwd = self.pwd
        self.client.schema = self.schema
        self.client.user = self.user

    def get(self):
        if self.pdb_id:
            return self.client.get_one(self.pdb_id, self.resource)
        else:
            return self.client.get_all(self.resource)

    def post(self):
        if not self.path:
            logging.error("No path to JSON file(s) provided")
            return None
        if self.path.endswith(".json"):
            return self.client.post(self.path, self.resource)
        else:
            for json_path in glob.glob("%s/*.json" % self.path):
                self.client.post(json_path, self.resource)
                self.client.json_data = None
            return True

    def put(self):
        if not self.path:
            logging.error("No path to JSON file(s) provided")
            return None
        return self.client.put(self.path, self.pdb_id, self.resource)

    def delete(self):
        return self.client.delete_one(self.pdb_id, self.resource)

    def process_options(self):
        for option, value in self.opts:
            if option in ["-u", "--user"]:
                self.user_name = value
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
                print(self.client)
                break
            elif option in ["-d", "--debug"]:
                logging.basicConfig(level=logging.DEBUG)
            else:
                logging.info("Unhandled option: %s" % option)
