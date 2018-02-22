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
import logging
import re
import glob
from funpdbe_client.constants import Constants
from funpdbe_client.schema import Schema
from funpdbe_client.user import User


class Client(object):
    """
    The FunPDBe deposition client allows users to deposit, delete and view
    data in the FunPDBe deposition system
    """

    def __init__(self, user=None, pwd=None, help=False):
        self.user = User(user, pwd)
        self.json_data = None
        self.schema = None
        self.api_url = Constants().get_api_url()
        # Only perform welcome with user and password check, if not running in help mode
        if not help:
            self.welcome()

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
-m, --mode:       Running mode (get, post, delete, put)
-i, --pdbid:      PDB id of an entry
-r, --resource:   Name of a resource
-f, --path:       Path to JSON file (.json ending), or files (folder name)
-d, --debug:      Enable debug logging

1.) Listing all entries
./funpdbe_client.py -user=username -pwd=password --mode=get

2.) Listing entries for PDB id 1abc
./funpdbe_client.py -user=username -pwd=password --mode=get --pdb_id=1abc

3.) Listing entries from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --resource=funsites

4.) Listing entries for PDB id 1abc from funsites
./funpdbe_client.py -user=username -pwd=password --mode=get --pdb_id=1abc --resource=funsites

5.) Posting an entry to funsites
./funpdbe_client.py -user=username -pwd=password --mode=post --path=path/to/data.json --resource=funsites

6.) Deleting an entry (1abc) from funsites
./funpdbe_client.py -user=username -pwd=password --mode=delete --pdb_id=1abc --resource=funsites

7.) Updating an entry (1abc) from funsites
./funpdbe_client.py -user=username -pwd=password --mode=put --path=path/to/data.json --resource=funsites --pdb_id=1abc
        """

    def welcome(self):
        print("\n####################################\n")
        print("Welcome to FunPDBe deposition client\n")
        print("####################################\n")
        self.user_info()

    def user_info(self):
        """
        Prompting user to provide info if missing
        :return: None
        """
        self.user.set_user()
        self.user.set_pwd()

    def set_schema(self):
        self.schema = Schema()
        self.schema.get_schema()

    def set_json_data(self, value):
        self.json_data = value

    def get_one(self, pdb_id, resource=None):
        """
        Get one FunPDBe entry based on PDB id and
        optionally resource name
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: None
        """
        url = self.api_url
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
        url = self.api_url
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
                    self.set_json_data(json.load(json_file))
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
        if not self.schema:
            self.set_schema()
        if self.schema.validate_json(self.json_data):
            logging.debug("JSON validated")
            self.json_data = self.schema.clean_json(self.json_data)
            return True
        logging.warning("JSON invalid")
        return False

    def post(self, path, resource):
        """
        POST JSON to deposition API
        :param path: String, path to JSON file
        :param resource: String, resource name
        :return: None
        """
        if not self.parse_json(path):
            return None
        if not self.validate_json():
            return None
        url = self.api_url
        url += "resource/%s/" % resource
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        check = self.put_or_post_check("put", r.status_code, r.text)
        if check:
            print("%s entry for %s from %s" % (check, resource, path))
        return r

    def put(self, path, pdb_id, resource):
        """
        POST JSON to deposition API
        :param path: String, path to JSON file
        :param pdb_id, String, PDB id
        :param resource: String, resource name
        :return: None
        """
        if not self.parse_json(path):
            return None
        if not self.validate_json():
            return None
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        check = self.put_or_post_check("put", r.status_code, r.text)
        if check:
            print("%s %s from %s" % (check, pdb_id, resource))
        return r

    def put_or_post_check(self, mode, status_code, text):
        messages = {
            "post": "201 - created",
            "put": "201 - updated"
        }
        if status_code != 201:
            logging.error("Error: %i - %s" % (status_code, text))
            return None
        else:
            return messages[mode]

    def delete_one(self, pdb_id, resource):
        """
        DELETE entry based on PDB id
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: none
        """
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        if r.status_code == 301:
            print("%i - deleted %s from %s" % (r.status_code, pdb_id, resource))
        return r


def main():
    user = None
    pwd = None
    mode = None
    pdb_id = None
    resource = None
    path = None
    debug = False
    config = Constants()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:m:i:r:f:hd", [
            "user=",
            "pwd=",
            "mode=",
            "pdb_id=",
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
            if value in ("get", "post", "delete", "put"):
                mode = value
        elif option in ["-i", "--pdb_id"]:
            if re.match(config.get_pdb_id_pattern(), value):
                pdb_id = value
            else:
                logging.warning("Invalid PDB id format")
                while not pdb_id:
                    pdb_id = input("valid pdb id (lower case): ")
        elif option in ["-r", "--resource"]:
            if value in config.get_resources():
                resource = value
            else:
                logging.warning("Invalid resource name")
                logging.warning("Has to be one of:" + str(config.get_resources()))
        elif option in ["-f", "--path"]:
            path = value
        elif option in ["-h", "--help"]:
            client = Client(help=True)
            print(client)
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

    client = Client(user=user, pwd=pwd)

    # Ask user to give running mode if not already done so
    if not mode:
        while not mode:
            mode_input = input("running mode: ")
            if mode_input in ("get", "post", "put", "delete"):
                mode = mode_input

    if mode == "get":
        if pdb_id:
            client.get_one(pdb_id, resource)
        else:
            client.get_all(resource)
    elif mode == "post":
        # Set the JSON schema only once
        client.set_schema()
        if not path:
            while not path:
                path = input("path to json: ")
        if not resource:
            while not resource:
                resource = input("resource name: ")
        if path.endswith(".json"):
            client.post(path, resource)
        else:
            for json_path in glob.glob("%s/*.json" % path):
                client.post(json_path, resource)
                # Reset JSON data to None
                client.set_json_data(None)

    elif mode == "put":
        # Set the JSON schema only once
        client.set_schema()
        if not path:
            while not path:
                path = input("path to json (../file.json): ")
        if not resource:
            while not resource:
                resource = input("resource name: ")
        if not pdb_id:
            while not pdb_id:
                pdb_id = input("pdb id to update: ")
        if not path.endswith(".json"):
            while not path.endswith(".json"):
                path = input("path to json (../file.json): ")
        client.put(path, pdb_id, resource)

    elif mode == "delete":
        if not pdb_id:
            while not pdb_id:
                pdb_id = input("pdb id to delete: ")
        if not resource:
            while not resource:
                resource = input("resource name: ")
        client.delete_one(pdb_id, resource)


if __name__ == "__main__":
    main()
