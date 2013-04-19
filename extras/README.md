Requirements for running the validator and tests:

jsonschema:
    > pip install jsonschema

This needs a few things to validate properly:

    > pip install rfc3987 isodate

The tests should check for the latter two.

# TESTS

You should be able to run

    > python manifest_test.py

and see something like the following:

~~~
...................................................................
----------------------------------------------------------------------
Ran 67 tests in 1.171s

OK
~~~

# VALIDATION

~~~
> python validate.py -h
usage: validate.py [-h] json schema

Validate a JSON file against a schema.

positional arguments:
  json        The JSON file to validate
  schema      The schema to validate against

optional arguments:
  -h, --help  show this help message and exit
~~~

So you can run the following:

~~~
> python validate.py tests/valid/route.json apt.schema.json
Schema looks good!
Congratulations!  Validation ok
~~~

or 

~~~
> python validate.py json_full.json apt.schema.json 
Schema looks good!
Error validating
Additional properties are not allowed (u'file' was unexpected)
~~~


---
Matt Long
2013-03-04
This file and all others in this archive are (c) Aptomar AS, 2013