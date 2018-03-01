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

    def __init__(self, opts, client):
        self.opts = opts
        self.client = client
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
        else:
            return self.action()

        return None

    def action(self):
        if self.mode == "get":
            return self.get()
        elif self.mode == "delete":
            return self.delete()
        elif self.mode == "post":
            return self.post()
        elif self.mode == "put":
            return self.put()

    def configure(self):
        self.client.user.user_name = self.user_name
        self.client.user.user_pwd = self.pwd

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

    def set_path(self):
        self.path = self.loop_options("-f", "--path")

    def set_pdb_id(self):
        self.pdb_id = self.loop_options("-i", "--pdb_id")

    def set_mode(self):
        self.mode = self.loop_options("-m", "--mode")

    def set_resource(self):
        self.resource = self.loop_options("-r", "--resource")

    def set_user(self):
        self.user_name = self.loop_options("-u", "--user")

    def set_pwd(self):
        self.pwd = self.loop_options("-p", "--pwd")

    def loop_options(self, opt1, opt2):
        for option, value in self.opts:
            if option == opt1 or option == opt2:
                return value

    def process_options(self):
        self.set_path()
        self.set_pdb_id()
        self.set_mode()
        self.set_resource()
        self.set_user()
        self.set_pwd()
        for option, value in self.opts:
            if option in ["-h", "--help"]:
                print(self.client)
            elif option in ["-d", "--debug"]:
                logging.basicConfig(level=logging.DEBUG)
