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
import re
from funpdbe_client.constants import PDB_ID_PATTERN, API_URL, RESOURCES
from funpdbe_client.logger_config import FunPDBeClientLogger, generic_error

CLIENT_ERRORS = {
    "no_pdb": "No PDB identifier specified",
    "bad_pdb": "Invalid PDB identifier pattern",
    "no_resource": "No resource name specified",
    "unknown_resource": "Unknown resource name",
    "no_path": "No file path to JSON(s) specified",
    "bad_json": "JSON does not comply with FunPDBe schema"
}


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
        self.logger = FunPDBeClientLogger("client")

    def __str__(self):
        return """
The FunPDBe deposition client allows users to deposit, delete and view  
data in the FunPDBe deposition system                                   

Usage parameters:
-h, --help:       Help (this is what you see now)
-u, --user:       FunPDBe user name
-p, --pwd:        FunPDBe password
-m, --mode:       Running mode (get, post, delete, put)
-i, --pdbid:      PDB id of an entry
-r, --resource:   Name of a resource
-f, --path:       Path to JSON file (.json ending), or files (folder name)
-d, --debug:      Enable debug logging
        """

    def get_one(self, pdb_id, resource=None):
        """
        Get one FunPDBe entry based on PDB id and
        optionally resource name
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: None
        """
        message = "GET entry for %s" % pdb_id
        if resource:
            message += " from %s" % resource
        self.logger.log().info(message)

        if not self.check_pdb_id(pdb_id):
            return None

        self.user_info()
        url = self.construct_get_url(resource, pdb_id)
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))

        if(r.status_code == 200):
            self.logger.log().info("[%i] success" % r.status_code)
        else:
            self.log_api_error(r.status_code, r.text)

        print(r.text)
        return r

    def construct_get_url(self, resource=None, pdb_id=None):
        url = self.api_url
        if resource and self.check_resource(resource):
            url += "resource/%s/" % resource
        else:
            url += "pdb/"
        url += "%s/" % pdb_id
        return url

    def get_all(self, resource=None):
        """
        Get all FunPDBe entries, optionally filtered
        by resource name
        :param resource: String, resource name
        :return: None
        """
        message = "GET all entries"
        if resource:
            message += " from %s" % resource
        self.logger.log().info(message)

        self.user_info()
        url = self.api_url
        if resource and self.check_resource(resource):
            url += "resource/%s/" % resource
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        print(r.text)
        return r

    def post(self, path, resource):
        """
        POST JSON to deposition API
        :param path: String, path to JSON file
        :param resource: String, resource name
        :return: None
        """
        message = "POST %s to %s" % (path, resource)
        self.logger.log().info(message)
        self.user_info()
        if not self.check_resource(resource):
            return None
        if not self.parse_json(path):
            return None
        if not self.validate_json():
            return None
        url = self.api_url
        url += "resource/%s/" % resource
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        self.check_status(r, 201)
        return r

    def put(self, path, pdb_id, resource):
        """
        POST JSON to deposition API
        :param path: String, path to JSON file
        :param pdb_id, String, PDB id
        :param resource: String, resource name
        :return: None
        """
        message = "UPDATE %s in %s from %s" % (pdb_id, resource, path)
        self.logger.log().info(message)
        if not self.check_resource(resource) or not self.check_pdb_id(pdb_id):
            return None
        self.user_info()
        if not self.parse_json(path):
            return None
        if not self.validate_json():
            return None
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        self.check_status(r, 201)
        return r

    def delete_one(self, pdb_id, resource):
        """
        DELETE entry based on PDB id
        :param pdb_id: String, PDB id
        :param resource: String, resource name
        :return: none
        """
        message = "DELETE entry %s from %s" % (pdb_id, resource)
        self.logger.log().info(message)

        if not self.check_resource(resource):
            return None
        if not self.check_pdb_id(pdb_id):
            return None
        self.user_info()
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        self.check_status(r, 301)
        return r

    def check_pdb_id(self, pdb_id):
        """
        Check if PDB id exists and if it matches
        the regular expression pattern of a valid
        PDB identifier
        :param pdb_id: String
        :return: Boolean
        """
        if not self.check_exists(pdb_id, "no_pdb"):
            return False
        if re.match(PDB_ID_PATTERN, pdb_id):
            return True
        generic_error()
        self.logger.log().error(CLIENT_ERRORS["bad_pdb"])
        return False

    def check_resource(self, resource):
        """
        Check if resource name exists and
        if it is a known (registered) resource
        :param resource: String
        :return: Boolean
        """
        if not self.check_exists(resource, "no_resource"):
            return False
        if resource in RESOURCES:
            return True
        self.logger.log().error(CLIENT_ERRORS["unknown_resource"])
        generic_error()
        return False

    def parse_json(self, path):
        """
        Parse user JSON file
        :param path: String, path to JSON
        :return: Boolean
        """
        if not self.check_exists(path, "no_path"):
            return None
        try:
            with open(path) as json_file:
                try:
                    self.json_data = json.load(json_file)
                    self.logger.log().info("JSON parsed")
                    return True
                except ValueError as valerr:
                    self.logger.log().error(valerr)
                    generic_error()
                    return False
        except IOError as ioerr:
            self.logger.log().error(ioerr)
            generic_error()
            return False

    def validate_json(self):
        """
        Validate JSON against schema
        :return: Boolean, True if validated JSON, False if not
        """
        if not self.schema.json_schema:
            self.schema.get_schema()
        if self.schema.validate_json(self.json_data):
            self.logger.log().info("JSON complies with FunPDBe schema")
            self.json_data = self.schema.clean_json(self.json_data)
            return True
        self.logger.log().error(CLIENT_ERRORS["bad_json"])
        return False

    def check_status(self, response, expected):

        if response.status_code == expected:
            self.logger.log().info("[%i] SUCCESS" % response.status_code)
        else:
            self.logger.log().error("[%i] FAIL - %s" % (response.status_code, response.text))

    def log_api_error(self, status_code, text):
        self.logger.log().error("[%s] - %s" % (status_code, text))

    def check_exists(self, value, error):
        if value:
            return True
        self.logger.log().error(CLIENT_ERRORS[error])
        return False

    def user_info(self):
        """
        Prompting user to provide info if missing
        :return: None
        """
        self.user.set_user()
        self.user.set_pwd()
