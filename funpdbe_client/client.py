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

import requests
import json
import logging
import re
from funpdbe_client.constants import PDB_ID_PATTERN, API_URL


# API_URL = "http://127.0.0.1:8000/funpdbe_deposition/entries/"
# PDB_ID_PATTERN = "[0-9][a-z][a-z0-9]{2}"
# RESOURCES = (
#     "funsites",
#     "3dligandsite",
#     "nod",
#     "popscomp",
#     "14-3-3-pred",
#     "dynamine",
#     "cansar",
#     "credo"
# )


class Client(object):
    """
    The FunPDBe deposition client allows users to deposit, delete and view
    data in the FunPDBe deposition system
    """

    def __init__(self, schema, user):
        self.user = user
        self.schema = schema
        self.api_url = API_URL
        self.json_data = None

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
./client.py -user=username -pwd=password --mode=get

2.) Listing entries for PDB id 1abc
./client.py -user=username -pwd=password --mode=get --pdb_id=1abc

3.) Listing entries from funsites
./client.py -user=username -pwd=password --mode=get --resource=funsites

4.) Listing entries for PDB id 1abc from funsites
./client.py -user=username -pwd=password --mode=get --pdb_id=1abc --resource=funsites

5.) Posting an entry to funsites
./client.py -user=username -pwd=password --mode=post --path=path/to/data.json --resource=funsites

6.) Deleting an entry (1abc) from funsites
./client.py -user=username -pwd=password --mode=delete --pdb_id=1abc --resource=funsites

7.) Updating an entry (1abc) from funsites
./client.py -user=username -pwd=password --mode=put --path=path/to/data.json --resource=funsites --pdb_id=1abc
        """

    def get_one(self, pdb_id, resource=None):
        """
        Get one FunPDBe entry based on PDB id and
        optionally resource name
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: None
        """
        if not pdb_id:
            logging.error("No PDB id provided")
            return None
        if not re.match(PDB_ID_PATTERN, pdb_id):
            logging.error("PDB id is invalid")
            return None

        self.user_info()
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
        self.user_info()
        url = self.api_url
        if resource:
            url += "resource/%s/" % resource
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r

    def user_info(self):
        """
        Prompting user to provide info if missing
        :return: None
        """
        self.user.set_user()
        self.user.set_pwd()

    def set_json_data(self, value):
        self.json_data = value

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
        if not self.schema.json_schema:
            self.schema.get_schema()
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
        self.user_info()
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
        self.user_info()
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
        self.user_info()
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        if r.status_code == 301:
            print("%i - deleted %s from %s" % (r.status_code, pdb_id, resource))
        return r
