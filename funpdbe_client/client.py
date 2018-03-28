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
import datetime
from funpdbe_client.constants import PDB_ID_PATTERN, API_URL, RESOURCES


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

    def write_log(self, message, new=False):
        self.log = open("funpdbe_client.log", "a")
        if(new):
            self.log.write("\n")
        self.log.write("[%s] - %s\n" % (datetime.datetime.now(), message))
        self.log.close()

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
        self.write_log(message, new=True)

        if not pdb_id:
            self.write_log("No PDB id provided - please provide a PDB id")
            logging.error("Missing pdb_id argument in get_one()")
            return None
        if not self.check_pdb_id(pdb_id):
            return None

        self.user_info()
        url = self.api_url
        if resource and self.check_resource(resource):
            url += "resource/%s/" % resource
        else:
            url += "pdb/"
        url += "%s/" % pdb_id
        r = requests.get(url, auth=(self.user.user_name, self.user.user_pwd))
        if(r.status_code == 200):
            self.write_log("[200] - OK")
        else:
            self.write_log("[%s] - %s" % (r.status_code, r.text))
        print(r.text)
        return r

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
        self.write_log(message, new=True)

        self.user_info()
        url = self.api_url
        if resource and self.check_resource(resource):
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

    def check_pdb_id(self, pdb_id):
        if not pdb_id:
            self.write_log("No PDB id provided - please provide a PDB id")
            logging.error("PDB id not provided\n")
            return False
        if re.match(PDB_ID_PATTERN, pdb_id):
            return True
        self.write_log("Invalid PDB id format: %s - please check your PDB id" % pdb_id)
        logging.error("PDB id %s is not valid\n" % pdb_id)
        return False

    def check_resource(self, resource):
        if not resource:
            self.write_log("No resource name provided - please provide a resource name")
            logging.error("Missing argument resource in check_resource()")
            return False
        if resource in RESOURCES:
            return True
        self.write_log("Unknown resource name - please check your resource name and register if needed")
        logging.error("Invalid resource name in check_resource()")
        return False

    def parse_json(self, path):
        """
        Parse user JSON file
        :param path: String, path to JSON
        :return: Boolean, True if parse, False if errors
        """
        if not path:
            self.write_log("No file path provided for JSON(s) - please provide a valid path")
            logging.error("Missing path argument in parse_json()")
            return None
        try:
            with open(path) as json_file:
                try:
                    self.json_data = json.load(json_file)
                    logging.debug("JSON parsed")
                    return True
                except ValueError as valerr:
                    self.write_log("Error while parsing JSON: %s" % valerr)
                    logging.error("Value error: %s" % valerr)
                    return False
        except IOError as ioerr:
            self.write_log("Error while trying to open JSON file: %s" % ioerr)
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
            self.write_log("JSON is valid FunPDBe JSON")
            logging.debug("JSON validated in validate_json()")
            self.json_data = self.schema.clean_json(self.json_data)
            return True
        self.write_log("JSON does not comply with FunPDBe schema - Please check your data")
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
        if not self.check_resource(resource):
            return None
        if not self.parse_json(path):
            return None
        if not self.validate_json():
            return None
        url = self.api_url
        url += "resource/%s/" % resource
        r = requests.post(url, json=self.json_data, auth=(self.user.user_name, self.user.user_pwd))
        check = self.put_or_post_check("post", r.status_code, r.text)
        if check:
            self.write_log("%s entry for %s from %s" % (check, resource, path))
            logging.info("%s entry for %s from %s" % (check, resource, path))
        return r

    def put(self, path, pdb_id, resource):
        """
        POST JSON to deposition API
        :param path: String, path to JSON file
        :param pdb_id, String, PDB id
        :param resource: String, resource name
        :return: None
        """
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
        check = self.put_or_post_check("put", r.status_code, r.text)
        if check:
            self.write_log("%s entry for %s from %s" % (check, resource, path))
            logging.info("%s entry for %s from %s" % (check, resource, path))
        return r

    def put_or_post_check(self, mode, status_code, text):
        messages = {
            "post": "201 - created",
            "put": "201 - updated"
        }
        if status_code != 201:
            self.write_log("Error while trying to %s: [%s] - %s" % (mode, status_code, text))
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
        message = "DELETE entry %s from %s" % (pdb_id, resource)
        self.write_log(message, new=True)

        if not self.check_resource(resource):
            return None
        if not self.check_pdb_id(pdb_id):
            return None
        self.user_info()
        url = self.api_url
        url += "resource/%s/%s/" % (resource, pdb_id)
        r = requests.delete(url, auth=(self.user.user_name, self.user.user_pwd))
        if r.status_code == 301:
            self.write_log("SUCCESS")
            logging.info("[%i] - Deleted %s from %s" % (r.status_code, pdb_id, resource))
        else:
            self.write_log("FAILED")
            logging.error("[%i] - Failed to delete" % r.status_code)
        return r
