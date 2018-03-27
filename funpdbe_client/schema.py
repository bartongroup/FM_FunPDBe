import logging
import requests
import json
import jsonschema


class Schema(object):
    """
    Schema object to retrieve the JSON schema from GitHub
    and to validate user JSON against this schema
    """

    def __init__(self):
        self.url_base = "https://raw.githubusercontent.com/funpdbe-consortium/funpdbe_schema/master"
        self.json_url = "%s/funpdbe_schema.json" % self.url_base
        self.json_schema = None

    def get_schema(self):
        """
        Getting JSON schema
        :return: JSON, schema or None
        """
        logging.debug("Getting JSON schema")
        response = requests.get(self.json_url)
        if response.status_code == 404:
            logging.error(response.text)
            return None
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
        if not self.json_schema or not json_data:
            return False
        try:
            jsonschema.validate(json_data, self.json_schema)
            return True
        except jsonschema.exceptions.ValidationError:
            logging.warning("JSON does not comply with schema")
            return False

    @staticmethod
    def clean_json(json_data):
        json_copy = json_data
        for i in range(len(json_data["sites"])):
            json_copy["sites"][i]["source_database"] = json_data["sites"][i]["source_database"].lower()
        json_copy["pdb_id"] = json_data["pdb_id"].lower()
        return json_copy
