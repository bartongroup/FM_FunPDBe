import jsonschema
import json

with open("funpdbe_schema.json") as schema_file:
    funpdbe_schema = json.load(schema_file)

with open("funpdbe_example.json") as example_file:
    funpdbe_example = json.load(example_file)

try:
    if not (jsonschema.validate(funpdbe_example, funpdbe_schema)):
        print("\nJSON validated - has all the required fields and with the expected data types")
except jsonschema.exceptions.ValidationError as valerr:
    print(valerr)