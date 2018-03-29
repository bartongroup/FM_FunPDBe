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

import glob
from funpdbe_client.logger_config import FunPDBeClientLogger, generic_error

CONTROL_ERRORS = {
    "no_mode": "No running mode was specified (--mode=)",
    "no_path": "No path to JSON file(s) provided"
}

class Control(object):

    def __init__(self, opts, client):
        self.opts = opts
        self.client = client
        self.help = False
        self.logger = FunPDBeClientLogger("control")

    def run(self):
        self.process_options()
        self.configure()
        if self.help:
            print(self.client)
        elif not self.mode:
            generic_error()
            self.logger.log().error(CONTROL_ERRORS["no_mode"])
        else:
            return self.action()

        return None

    def action(self):
        actions = {
            "get": self.get,
            "post": self.post,
            "put": self.put,
            "delete": self.delete
        }
        if self.mode in actions.keys():
            return actions[self.mode]()
        return None

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
            self.logger.log().error(CONTROL_ERRORS["no_path"])
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
            self.logger.log().error(CONTROL_ERRORS["no_path"])
            return None
        return self.client.put(self.path, self.pdb_id, self.resource)

    def delete(self):
        return self.client.delete_one(self.pdb_id, self.resource)

    def loop_options(self, opt1, opt2):
        for option, value in self.opts:
            if option == opt1 or option == opt2:
                return value
        return None

    def process_options(self):
        self.path = self.loop_options("-f", "--path")
        self.pdb_id = self.loop_options("-i", "--pdb_id")
        self.mode = self.loop_options("-m", "--mode")
        self.resource = self.loop_options("-r", "--resource")
        self.user_name = self.loop_options("-u", "--user")
        self.pwd = self.loop_options("-p", "--pwd")
        for option, value in self.opts:
            if option in ["-h", "--help"]:
                self.help = True
