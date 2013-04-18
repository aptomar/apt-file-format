# Introduction

aptofile is a tool for opening, creating and validating aptomar
files. Aptomar files are used for sharing of GIS data and is a
zip archive with a manifest.json file and data.

aptofile checks if the manifest.json is valid against an aptomar
json schema file by using jsonschema 
(https://github.com/Julian/jsonschema). In addition, aptofile runs
various other tests against the entire file.

# Install

aptofile is a debian package and can be installed by:

    dpkg-buildpackage
	dpkg -i <debfilename>

This installs the package into /opt/aptomar/pyshared/. To use 
aptofile, append the package directory to your python path.
E.g:

    import sys
    sys.path.append('/opt/aptomar/pyshared')

# Use

Aptofile can be used for creating new files, opening existing
files or validating existing files:

    from aptofile import Aptofile
    
    with Aptofile.open(filename) as af:
        print af.getManifest()
        print af.getDescription()
        print af.readfile(fn)

    with Aptofile.create(filename,filetype) as af:
        # Add data

    if Aptofile.validateFile(filename):
        print "File is valid"

For more detailed examples please take a look at the test script in test/.



