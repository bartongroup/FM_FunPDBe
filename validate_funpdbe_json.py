import jsonschema
import json

with open("funpdbe_schema.v0.0.1.json") as schema_file:
    funpdbe_schema = json.load(schema_file)

with open("funpdbe_example.json") as example_file:
    funpdbe_example = json.load(example_file)

# print(funpdbe_schema)
# print(funpdbe_example)


jsonschema.validate(funpdbe_schema, funpdbe_example)