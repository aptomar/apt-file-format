#! /usr/bin/python

################################################################
#                                                              #
# validateFile.py                                              #
# Copyright (c) 2013 Aptomar AS, All Rights Reserved           #
#                                                              #
# Author: Jarle Bauck Hamar: <jarle.hamar@aptomar.com>         #
# Date: 2013-05-23                                             #
#                                                              #
################################################################

import argparse

from aptofile import Aptofile
parser = argparse.ArgumentParser(description="Tool for validating Aptofiles")
parser.add_argument('filename', help="name of aptofile to be validated")
args = parser.parse_args()

f = args.filename
print "Checking file '%s'... "%f,
with Aptofile.open(f) as af:
    if not af.validate():
        print "failed!"
        for test, msg in af.getFailedTests():
            print "Test '%s' failed: %s"%(test,msg)
    else: print "ok"


