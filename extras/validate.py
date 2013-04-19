# validate.py
# Copyright (c) 2013 Aptomar AS, All Rights Reserved
#
# Author: Matt Long <matthew.long@aptomar.com>
# Date:   2013-03-04
#
# This is a simple tool to validate a json manifest file against a json schema.

from jsonschema import validate, Draft4Validator, SchemaError
import argparse
import json


parser = argparse.ArgumentParser(description='Validate a JSON file against a schema.')
parser.add_argument('json', type=file, help='The JSON file to validate')
parser.add_argument('schema', type=file, help='The schema to validate against')


args = parser.parse_args()

json_obj = json.loads(args.json.read())
schema_obj = json.loads(args.schema.read())

good = False
try:
	Draft4Validator.check_schema(schema_obj)
except SchemaError as err:
	print "Schema has an error:"
	print err
else:
	print "Schema looks good!"
	good = True

if good:
	try:
		validate(json_obj, schema_obj, Draft4Validator)
	except Exception as inst:
		print "Error validating"
		print inst
	else:
		print "Congratulations!  Validation ok"

