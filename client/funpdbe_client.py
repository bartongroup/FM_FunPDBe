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
import logging
import re

RESOURCES = ("funsites", "3dligandsite", "nod", "popscomp", "14-3-3-pred", "dynamine", "cansar", "credo")


class Schema(object):
    """
    Schema object to retrieve the JSON schema from GitHub
    and to validate user JSON against this schema
    """

    def __init__(self):
        self.url_base = "https://raw.githubusercontent.com/funpdbe-consortium/funpdbe_schema/master"
        self.json_url = "%s/funpdbe_schema.v0.0.1.json" % self.url_base
        self.json_schema = None

    def get_schema(self):
        """
        Getting JSON schema
        :return: JSON, schema or None
        """
        logging.debug("Getting JSON schema")
        response = requests.get(self.json_url)
        try:
            self.json_schema = json.loads(response.text)
        except ValueError as valerr:
            logging.warning(valerr)

    def validate_json(self, json_data):
        """
        Validating JSON data against schema
        :param json_data: JSON, user data
        :return: True if JSON is valid, False is invalid or other problems
        """
        logging.debug("Validating JSON")
        print(self.json_schema)
        print(json_data)
        if not self.json_schema or not json_data:
            return False
        validation = jsonschema.validate(json_data, self.json_schema)
        if not validation:
            return True
        else:
            logging.warning("JSON does not comply with schema")
            logging.warning(validation)
            return False


class User(object):
    """
    User object to handle prompts if no user name
    or password were provided when running the Client()
    """

    def __init__(self, user=None, pwd=None):
        self.user_name = user
        self.user_pwd = pwd

    def set_user(self):
        """
        Get user name from user
        :return: String, user name
        """
        if not self.user_name:
            while not self.user_name:
                self.user_name = input("funpdbe user name: ")

    def set_pwd(self):
        """
        Get user password from user
        :return: String, user password
        """
        if not self.user_pwd:
            while not self.user_pwd:
                self.user_pwd = getpass.getpass("funpdbe password: ")


class Client(object):
    """
    The FunPDBe deposition client allows users to deposit, delete and view
    data in the FunPDBe deposition system
    """

    def __init__(self, user=None, pwd=None):
        self.user = User(user, pwd)
        self.json_data = None
        self.API_URL = "http://127.0.0.1:8000/funpdbe_deposition/entries/"

    def __str__(self):
        return """
#########################################################################
The FunPDBe deposition client allows users to deposit, delete and view  #
data in the FunPDBe deposition system                                   #
#########################################################################

Usage parameters:

-h, --help:       Help (this is what you see now)
-u, --user:       FunPDBe user name
-p, --pwd:        FunPDBe password
-m, --mode:       Running mode (get, post, delete)
-i, --pdbid:      PDB id of an entry
-r, --resource:   Name of a resource
-f, --path:       Path to JSON file (.json ending), or files (folder name)
-d, --debug:      Enable debug logging

Examples:

1.) Listing all entries
./funpdbe_client.py -user=username -pwd=password --mode=get

2.) Listing entries for PDB id 1abc
./funpdbe_client.py -user=username -pwd=password --mode=get --pdbid=1abc

3.) Listing entries from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --resource=funsites

4.) Listing entries for PDB id 1abc from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --pdbid=1abc --resource=funsites

5.) Posting an entry to funsites
./funpdbe_client.py -user=username -pwd=password --mode=post --path=path/to/data.json --resource=funsites

6.) Deleting an entry (1abc) from funsites
./funpdbe_client.py -user=username -pwd=password --mode=delete --pdbid=1abc --resource=funsites

#########################################################################
        """

    def user_info(self):
        """
        Prompting user to provide info if missing
        :return: None
        """
        self.user.set_user()
        self.user.set_pwd()

    @staticmethod
    def welcome():
        print("\n####################################\n")
        print("Welcome to FunPDBe deposition client\n")
        print("####################################\n")

    def get_one(self, pdb_id, resource=None):
        """
        Get one FunPDBe entry based on PDB id and
        optionally resource name
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: None
        """
        url = self.API_URL
        if resource:
            url += "resource/%s/" % resource
        else:
            url += "pdb/"
        url += "%s/" % pdb_id
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r

    def get_all(self, resource=None):
        """
        Get all FunPDBe entries, optionally filtered
        by resource name
        :param resource: String, resource name
        :return: None
        """
        url = self.API_URL
        if resource:
            url += "resource/%s/" % resource
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r

    def parse_json(self, path):
        """
        Parse user JSON file
        :param path: String, path to JSON
        :return: Boolean, True if parse, False if errors
        """
        try:
            with open(path) as json_file:
                try:
                    self.json_data = json.load(json_file)
                    logging.debug("JSON parsed")
                    return True
                except ValueError as valerr:
                    logging.error("Value error: %s" % valerr)
                    return False
        except IOError as ioerr:
            logging.error("File error: %s" % ioerr)
            return False

    def validate_json(self):
        """
        Validate JSON against schema
        :return: Boolean, True if validated JSON, False if not
        """
        schema = Schema()
        schema.get_schema()
        if schema.validate_json(self.json_data):
            logging.debug("JSON validated")
            return True
        logging.warning("JSON invalid")
        return False

    def post(self, resource):
        """
        POST JSON to deposition API
        :param resource: String, resource name
        :return: None
        """
        url = self.API_URL
        url += "resource/%s/" % resource
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r

    def delete_one(self, pdb_id, resource):
        """
        DELETE entry based on PDB id
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: none
        """
        # url = '%spdb/%s' % (self.API_URL, pdb_id)
        url = self.API_URL
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r


def main():
    user = None
    pwd = None
    mode = None
    pdbid = None
    resource = None
    path = None
    debug = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:m:i:r:f:hd", [
            "user=",
            "pwd=",
            "mode=",
            "pdbid=",
            "resource=",
            "path=",
            "help",
            "debug"])
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
            if re.match("[0-9][a-z][a-z0-9]{2}", value):
                pdbid = value
            else:
                logging.warning("Invalid PDB id format")
                while not pdbid:
                    pdbid = input("valid pdb id (lower case): ")
        elif option in ["-r", "--resource"]:
            if value in RESOURCES:
                resource = value
            else:
                logging.warning("Invalid resource name")
                logging.warning("Has to be one of:" + str(RESOURCES))
        elif option in ["-f", "--path"]:
            path = value
        elif option in ["-h", "--help"]:
            c = Client(user=user, pwd=pwd)
            print(c)
            exit(1)
        elif option in ["-d", "--debug"]:
            debug = True
        else:
            assert False, "unhandled option"

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__)

    c = Client(user=user, pwd=pwd)
    c.welcome()
    c.user_info()
    if mode == "get":
        if pdbid:
            c.get_one(pdbid, resource)
        else:
            c.get_all(resource)
    elif mode == "post":
        if not path:
            while not path:
                path = input("path to json: ")
        if not resource:
            while not resource:
                resource = input("resource name: ")
        if path.endswith(".json"):
            if c.parse_json(path):
                if c.validate_json():
                    c.post(resource)
        else:
            # TODO process all .json files in path (use glob)
            pass
    elif mode == "delete":
        if not pdbid:
            while not pdbid:
                pdbid = input("pdb id to delete: ")
        if not resource:
            while not resource:
                resource = input("resource name: ")
        c.delete_one(pdbid, resource)


if __name__ == "__main__":
    main()
