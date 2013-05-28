################################################################
#                                                              #
# testGeoUpload.py                                             #
# Copyright (c) 2013 Aptomar AS, All Rights Reserved           #
#                                                              #
# Author: Jarle Bauck Hamar: <jarle.hamar@aptomar.com>         #
# Date: 2013-05-23                                             #
#                                                              #
################################################################

import unittest
import sys
import os

sys.path.append('../src')
from aptofile import Aptofile, stripFileName
from geoupload import GeoUpload, getStyleName

testfile = 'tests/geotest.apt'
url = 'http://localhost/geoserver/rest'
username = 'admin'
password = 'geoserver'
style_dir = '/store/aptomar/geoserver/styles/'
# Workspace is created and deleted
workspace = 'testGeoserver'

class Test(unittest.TestCase):

    def setUp(self):
        self.geoupload = GeoUpload(url, username, password, style_dir, workspace)
        self.geoupload.cat.create_workspace(workspace, workspace)
        self.layers = []
        self.layer_groups = []
        self.resource_files = []
        self.styles = []

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        self.geoupload.deleteWorkspace()
        self.removeResourceFiles()

    def removeResourceFiles(self):
        for f in self.resource_files:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass

    def register(self, af):
        """
        Register layers, layer_groups, styles etc contained in aptofile
        for posttest deletion.
        """
        manifest = af.getManifest()
        asset_dict = manifest['asset']
        for layer_key, layer_dict in asset_dict['layers'].iteritems():
            layer_name = layer_dict['name'].replace(' ','_')
            if self.geoupload.workspace:
                layer_name = ':'.join([self.geoupload.workspace,layer_name])
            self.layers.append(layer_name)
            for fn in layer_dict['style']['data']:
                fn = stripFileName(fn)
                style_name = getStyleName(fn)
                if self.geoupload.workspace:
                    style_name = '_'.join([self.geoupload.workspace,style_name])
                if not self.geoupload.cat.get_style(style_name):
                    self.styles.append(style_name)

            try: resources = layer_dict['resources']['data']
            except KeyError: resources = []
            for fn in resources:
                fn = stripFileName(fn)
                basename = os.path.basename(fn)
                full_path = os.path.join(style_dir,'icons',basename)
                self.resource_files.append(full_path)

        for group_key, group_dict in asset_dict['groups'].iteritems():
            grp_name = group_dict['name']
            if self.geoupload.workspace:
                grp_name = '_'.join([self.geoupload.workspace,grp_name])
            self.layer_groups.append(grp_name)

    def checkUploads(self, layers=True, layer_groups = True,
                     styles = True, resources = True):
        """Check that everything is in place"""
        cat = self.geoupload.cat
        if layers:
            for layer in self.layers:
                self.assertIsNotNone(cat.get_layer(layer),
                                "Layer %s not found on server"%layer)
        if layer_groups:
            for layer_group in self.layer_groups:
                self.assertIsNotNone(cat.get_layergroup(layer_group),
                                "Layergroup %s not found on server"%layer_group)
        if styles:
            for style in self.styles:
                self.assertIsNotNone(cat.get_style(style),
                                "Style %s not found on server"%style)
        if resources:
            for resource in self.resource_files:
                self.assertTrue(os.path.exists(resource),
                                "Resource file %s not found on server"%resource)

    def checkRemoved(self, layers=True, layer_groups = True,
                     styles = True, resources = True):
        """Check that everything is in place"""
        cat = self.geoupload.cat
        if layers:
            for layer in self.layers:
                self.assertIsNone(cat.get_layer(layer),
                                "Layer %s not found on server"%layer)
        if layer_groups:
            for layer_group in self.layer_groups:
                self.assertIsNone(cat.get_layergroup(layer_group),
                                "Layergroup %s not found on server"%layer_group)
        if styles:
            for style in self.styles:
                self.assertIsNone(cat.get_style(style),
                                "Style %s not found on server"%style)
        if resources:
            for resource in self.resource_files:
                self.assertFalse(os.path.exists(resource),
                                "Resource file %s not found on server"%resource)


    def testUpload(self):
        with Aptofile.open(testfile) as af:
            if not af.validate():
                raise Exception(str(af.getFailedTests()))

            self.register(af)
            self.geoupload.uploadToStore(af)

        self.checkUploads()
        self.cleanup()
        self.checkRemoved()

    def testDeleteFile(self):
        with Aptofile.open(testfile) as af:
            if not af.validate():
                raise Exception(str(af.getFailedTests()))

            self.register(af)
            self.geoupload.uploadToStore(af)
            self.geoupload.deleteFile(af)

        self.checkRemoved(resources=False)



if __name__=='__main__':

    import logging

    logging.basicConfig(level=logging.ERROR)
    unittest.main()
