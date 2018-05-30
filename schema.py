import json
import jsonmerge
import jsonschema


from collections import OrderedDict

with open("funpdbe_schema.v0.0.1.json") as schema_file:
    funpdbe_schema = json.load(schema_file, object_pairs_hook=OrderedDict)

FunPDBe_merger = jsonmerge.Merger(funpdbe_schema)


def validate_FunPDBe_entry(entry):
    return jsonschema.validate(entry, funpdbe_schema)


def resource_header(data_resource, resource_version=None, software_version=None, resource_entry_url=None,
                    release_date=None):
    """
    Resource description components of FunPDBe schema.

    :param data_resource: Name of the resource.
    :param resource_version: Version of the resource.
    :param software_version: Software version.
    :param resource_entry_url: URL of resource.
    :param release_date: Date annotation created.
    :return:
    """
    d = {"data_resource": data_resource,
         "resource_version": resource_version,
         "software_version": software_version,
         "resource_entry_url": resource_entry_url,
         "release_date": release_date}
    d = {k: v for k, v in d.items() if v is not None}
    return d
