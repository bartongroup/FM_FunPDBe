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

import getopt
import sys
import logging
import glob
from funpdbe_client.client import Client
from funpdbe_client.schema import Schema
from funpdbe_client.user import User


def control(opts):

    user = None
    pwd = None
    mode = None
    pdb_id = None
    resource = None
    path = None
    debug = False
    help = False

    for option, value in opts:
        if option in ["-u", "--user"]:
            user = value
        elif option in ["-p", "--pwd"]:
            pwd = value
        elif option in ["-m", "--mode"] and value in ("get", "post", "delete", "put"):
            mode = value
        elif option in ["-i", "--pdb_id"]:
            pdb_id = value
        elif option in ["-r", "--resource"]:
            resource = value
        elif option in ["-f", "--path"]:
            path = value
        elif option in ["-h", "--help"]:
            help = True
            # client = Client(api_url=None, schema=None, user=None)
            # print(client)
            # exit(1)
        elif option in ["-d", "--debug"]:
            debug = True
        else:
            assert False, "unhandled option"

    if help:
        # Print help text and exit
        print(Client(schema=None, user=None))
        exit(1)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    # logging.getLogger(__name__)

    user = User(user, pwd)
    schema = Schema()
    client = Client(schema=schema, user=user)

    # Ask user to give running mode if not already done so
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


def main():

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

    control(opts)


if __name__ == '__main__':
    main()
