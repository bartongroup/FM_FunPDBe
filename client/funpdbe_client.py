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

import getpass
import requests
import getopt
import sys
import json
import jsonschema


class Schema(object):

    def __init__(self):
        self.url_base = "https://raw.githubusercontent.com/funpdbe-consortium/funpdbe_schema/master"
        self.json_url = "%s/funpdbe_schema.v0.0.1.json" % self.url_base
        self.json_schema = self.get_schema()

    def get_schema(self):
        response = requests.get(self.json_url)
        return json.loads(response.text)

    def validate_json(self, json_data):
        validation = jsonschema.validate(json_data, self.json_schema)
        if not validation:
            return True
        else:
            print(validation)
            return False


class User(object):
    """
    User object to handle prompts if no user name
    or password were provided when running the Client()
    """

    def __init__(self, user=None, pwd=None):
        self.user_name = user
        self.user_pwd = pwd
        if not self.user_name:
            while not self.user_name:
                self.set_user()
        if not self.user_pwd:
            while not self.user_pwd:
                self.set_pwd()

    def set_user(self):
        self.user_name = input("funpdbe user name: ")

    def set_pwd(self):
        self.user_pwd = getpass.getpass("funpdbe password: ")


class Api(object):

    def __init__(self):
        # TODO
        self.url_base = "http://127.0.0.1:8000/funpdbe_deposition"
        self.entries_url = "%s/entries/" % self.url_base


class Client(object):

    def __init__(self, user=None, pwd=None):
        self.welcome()
        self.user = User(user, pwd)
        self.api = Api()
        self.json_data = None

    @staticmethod
    def welcome():
        print("\n####################################\n")
        print("Welcome to FunPDBe deposition client\n")
        print("####################################\n")

    def get_one(self, pdb_id, resource=None):
        url = self.api.entries_url
        if resource:
            url += "resource/%s/" % resource
        else:
            url += "pdb/"
        url += "%s/" % pdb_id
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)

    def get_all(self, resource=None):
        url = self.api.entries_url
        if resource:
            url += "resource/%s/" % resource
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)

    def parse_json(self, path):
        try:
            with open(path) as json_file:
                try:
                    self.json_data = json.load(json_file)
                    print("JSON parsed")
                    return True
                except ValueError as valerr:
                    print("Value error: %s" % valerr)
                    return False
        except IOError as ioerr:
            print("File error: %s" % ioerr)
            return False

    def validate_json(self):
        schema = Schema()
        if schema.validate_json(self.json_data):
            print("JSON validated")
            return True
        return False

    def post(self):
        url = self.api.entries_url
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)

    def delete_one(self, pdb_id):
        url = '%spdb/%s' % (self.api.entries_url, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)


def main():
    # TODO Add verbose ARG
    user = None
    pwd = None
    mode = None
    pdbid = None
    resource = None
    path = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:m:i:r:f:h", [
            "user=",
            "pwd=",
            "mode=",
            "pdbid=",
            "resource=",
            "path=",
            "help"])
    except getopt.GetoptError as err:
        print("Error: %s" % err)
        sys.exit(2)
    for option, value in opts:
        if option in ["-u", "--user"]:
            user = value
        elif option in ["-p", "--pwd"]:
            pwd = value
        elif option in ["-m", "--mode"]:
            if value in ("get", "post", "delete"):
                mode = value
        elif option in ["-i", "--pdbid"]:
            pdbid = value
        elif option in ["-r", "--resource"]:
            resource = value
        elif option in ["-f", "--path"]:
            path = value
        elif option in ["-h", "--help"]:
            # TODO add help texts
            pass
        else:
            assert False, "unhandled option"

    c = Client(user=user, pwd=pwd)
    if mode == "get":
        if pdbid:
            c.get_one(pdbid, resource)
        else:
            c.get_all(resource)
    elif mode == "post":
        if not path:
            while not path:
                path = input("path to json: ")
        if path.endswith(".json"):
            if c.parse_json(path):
                if c.validate_json():
                    c.post()
        else:
            # TODO process all .json files in path (use glob)
            pass
    elif mode == "delete":
        if not pdbid:
            while not pdbid:
                pdbid = input("pdb id to delete: ")
        c.delete_one(pdbid)


if __name__ == "__main__":
    main()
