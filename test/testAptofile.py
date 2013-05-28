################################################################
#                                                              #
# testAptofile.py                                              #
# Copyright (c) 2013 Aptomar AS, All Rights Reserved           #
#                                                              #
# Author: Jarle Bauck Hamar: <jarle.hamar@aptomar.com>         #
# Date: 2013-05-23                                             #
#                                                              #
################################################################


import unittest
import sys
import json

sys.path.append('../src')
from aptofile import Aptofile
import jsonschema

class TestManifest(unittest.TestCase):

    def setUp(self):
        with open('tests/header.json') as fid:
            self.inst = json.load(fid)
        self.schema = Aptofile.SCHEMA

    def validate(self):
        try:
            jsonschema.validate(self.inst, self.schema, Aptofile.VALIDATOR,
                                format_checker = jsonschema.FormatChecker())
        except jsonschema.ValidationError:
            return False
        return True

    def test_schema_validates(self):
        Aptofile.VALIDATOR.check_schema(Aptofile.SCHEMA)

    def test_valid_manifest_header(self):
        self.assertTrue(self.validate())

    def test_manifest_missing_date(self):
        del self.inst["date"]
        self.assertFalse(self.validate())

    def test_manifest_missing_description(self):
        del self.inst["description"]
        self.assertFalse(self.validate())

    def test_manifest_missing_version(self):
        del self.inst["manifest_version"]
        self.assertFalse(self.validate())

    def test_manifest_missing_generator(self):
        del self.inst["generator"]
        self.assertFalse(self.validate())

    def test_manifest_bad_date(self):
        self.inst["date"] = "tomorrow"
        self.assertFalse(self.validate())

    def test_manifest_disallow_additional_properties(self):
        self.inst["extra"] = "large"
        self.assertFalse(self.validate())

class TestAsset(unittest.TestCase):

    def testCreateAsset(self):
        f = 'tests/asset.apt'
        with Aptofile.create(f,'asset') as af:
            af.setDescription("This is a description of the asset.")
            af.setGenerator("aptfile.py", "Aptomar AS")
            af.addLayer('layer1', name='layer1-name',
                        geometry_data=[('tests/asset/layers/layer1.dbf',
                                        'file:/layers/layer1.dbf'),
                                       ('tests/asset/layers/layer1.shp',
                                        'layers/layer1.shp'),
                                       ('tests/asset/layers/layer1.shx',
                                        'layers/layer1.shx')])
            af.addFile2Layer(('tests/asset/styles/layer1.xml',
                             'styles/layer1.xml'), 'layer1', 'style')
            af.addFile2Layer(('tests/asset/resource1.png','resource1.png'),
                             'layer1', 'resources')
            af.addFile2Layer(('tests/asset/resource2.png','resource2.png'),
                             'layer1', 'resources')
            af.addLayer('layer2',name='layer2-name')
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.dbf', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shx', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('styles/layer1.xml','layer2',
                             'style', writeFile=False)
            af.addFile2Layer('resource1.png','layer2','resources', writeFile=False)
            af.addFile2Layer('resource2.png','layer2','resources', writeFile=False)
            af.addFile2Layer('http://very-big-file.com/','layer2','resources', writeFile=True)
            af.addGroup('group1','group1-name',['layer1'])
            af.addGroup('group2','group2-name',['layer2'])

            #Validate before write:
            self.assertTrue(af.validate())

        #Validate after write and open
        self.assertTrue(Aptofile.validateFile(f))

    def testAssetMissingFile(self):
        f = 'tests/asset_missing_file.apt'
        with Aptofile.create(f,'asset') as af:
            af.setDescription("This is a description of the asset.")
            af.setGenerator("aptfile.py", "Aptomar AS")
            af.addLayer('layer1', name='layer1-name',
                        geometry_data=[('tests/asset/layers/layer1.dbf',
                                        'layers/layer1.dbf'),
                                       ('tests/asset/layers/layer1.shp',
                                        'layers/layer1.shp'),
                                       ('tests/asset/layers/layer1.shx',
                                        'layers/layer1.shx')])
            af.addFile2Layer(('tests/asset/styles/layer1.xml',
                             'styles/layer1.xml'), 'layer1', 'style')
            af.addFile2Layer(('tests/asset/resource1.png','resource1.png'),
                             'layer1', 'resources')
            af.addFile2Layer(('tests/asset/resource2.png','resource2.png'),
                             'layer1', 'resources')
            af.addLayer('layer2',name='layer2-name')
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.dbf', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shx', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('styles/layer1.xml','layer2',
                             'style', writeFile=False)
            af.addFile2Layer('resource1.png','layer2','resources', writeFile=False)
            af.addFile2Layer('resource2.png','layer2','resources', writeFile=False)
            af.addFile2Layer('http://very-big-file.com/','layer2','resources', writeFile=True)
            af.addGroup('group1','group1-name',['layer1'])
            af.addGroup('group2','group2-name',['layer2'])

            #Validate before write:
            self.assertTrue(af.validate())
            af.addFile2Layer('resource3.png','layer2','resources', writeFile=False)

        #Validate after write and open
        self.assertFalse(Aptofile.validateFile(f))

    def testAssetIncorrectLayerInGroup(self):
        f = 'tests/asset_incorrect_layer_in_group.apt'
        with Aptofile.create(f,'asset') as af:
            af.setDescription("This is a description of the asset.")
            af.setGenerator("aptfile.py", "Aptomar AS")
            af.addLayer('layer1', name='layer1-name',
                        geometry_data=[('tests/asset/layers/layer1.dbf',
                                        'layers/layer1.dbf'),
                                       ('tests/asset/layers/layer1.shp',
                                        'layers/layer1.shp'),
                                       ('tests/asset/layers/layer1.shx',
                                        'layers/layer1.shx')])
            af.addFile2Layer(('tests/asset/styles/layer1.xml',
                             'styles/layer1.xml'), 'layer1', 'style')
            af.addFile2Layer(('tests/asset/resource1.png','resource1.png'),
                             'layer1', 'resources')
            af.addFile2Layer(('tests/asset/resource2.png','resource2.png'),
                             'layer1', 'resources')
            af.addLayer('layer2',name='layer2-name')
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.dbf', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shx', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('styles/layer1.xml','layer2',
                             'style', writeFile=False)
            af.addFile2Layer('resource1.png','layer2','resources', writeFile=False)
            af.addFile2Layer('resource2.png','layer2','resources', writeFile=False)
            af.addFile2Layer('http://very-big-file.com/','layer2','resources', writeFile=True)
            af.addGroup('group1','group1-name',['layer1'])
            af.addGroup('group2','group2-name',['layer3'])

            #Validate before write:
            self.assertFalse(af.validate())

        #Validate after write and open
        self.assertFalse(Aptofile.validateFile(f))

    def testAssetMissingStyle(self):
        f = 'tests/asset_missing_style.apt'
        with Aptofile.create(f,'asset') as af:
            af.setDescription("This is a description of the asset.")
            af.setGenerator("aptfile.py", "Aptomar AS")
            af.addLayer('layer1', name='layer1-name',
                        geometry_data=[('tests/asset/layers/layer1.dbf',
                                        'layers/layer1.dbf'),
                                       ('tests/asset/layers/layer1.shp',
                                        'layers/layer1.shp'),
                                       ('tests/asset/layers/layer1.shx',
                                        'layers/layer1.shx')])
            af.addFile2Layer(('tests/asset/styles/layer1.xml',
                             'styles/layer1.xml'), 'layer1', 'style')
            af.addFile2Layer(('tests/asset/resource1.png','resource1.png'),
                             'layer1', 'resources')
            af.addFile2Layer(('tests/asset/resource2.png','resource2.png'),
                             'layer1', 'resources')
            af.addLayer('layer2',name='layer2-name')
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.dbf', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shx', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('styles/layer1.xml','layer2',
                             'style', writeFile=False)
            af.addFile2Layer('resource1.png','layer2','resources', writeFile=False)
            af.addFile2Layer('resource2.png','layer2','resources', writeFile=False)
            af.addFile2Layer('http://very-big-file.com/','layer2','resources', writeFile=True)
            af.addGroup('group1','group1-name',['layer1'])
            af.addGroup('group2','group2-name',['layer2'])

            #Validate before write:
            self.assertTrue(af.validate())
            del af.manifest['asset']['layers']['layer1']['style']

        #Validate after write and open
        self.assertFalse(Aptofile.validateFile(f))

    def testAssetIncorrectDataType(self):
        f = 'tests/asset_incorrect_data_type.apt'
        with Aptofile.create(f,'asset') as af:
            af.setDescription("This is a description of the asset.")
            af.setGenerator("aptfile.py", "Aptomar AS")
            af.addLayer('layer1', name='layer1-name',
                        geometry_data=[('tests/asset/layers/layer1.dbf',
                                        'layers/layer1.dbf'),
                                       ('tests/asset/layers/layer1.shp',
                                        'layers/layer1.shp'),
                                       ('tests/asset/layers/layer1.shx',
                                        'layers/layer1.shx')])
            af.addFile2Layer(('tests/asset/styles/layer1.xml',
                             'styles/layer1.xml'), 'layer1', 'style')
            af.addFile2Layer(('tests/asset/resource1.png','resource1.png'),
                             'layer1', 'resources')
            af.addFile2Layer(('tests/asset/resource2.png','resource2.png'),
                             'layer1', 'resources')
            af.addLayer('layer2',name='layer2-name')
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.dbf', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shx', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('layers/layer1.shp', 'layer2',
                             'geometry', writeFile=False)
            af.addFile2Layer('styles/layer1.xml','layer2',
                             'style', writeFile=False)
            af.addFile2Layer('resource1.png','layer2','resources', writeFile=False)
            af.addFile2Layer('resource2.png','layer2','resources', writeFile=False)
            af.addFile2Layer('http://very-big-file.com/','layer2','resources', writeFile=True)
            af.addGroup('group1','group1-name',['layer1'])
            af.addGroup('group2','group2-name',['layer2'])

            #Validate before write:
            self.assertTrue(af.validate())
            d=af.manifest['asset']['layers']['layer1']['style']['data'].pop()
            af.manifest['asset']['layers']['layer1']['style']['data'] = d

        #Validate after write and open
        self.assertFalse(Aptofile.validateFile(f))

class TestImage(unittest.TestCase):

    def testImage(self):
        f = 'tests/image.apt'
        with Aptofile.create(f,'image') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the image')
            af.setImageName('The image name')
            af.setImageDescription('An image of something')
            af.setImageGeoreference( 10.4344, 63.4181, 150.60)
            af.setImageBounds(['data:,bounds as a string'])
            af.addImageFile(('tests/image/image.jpg','image.jpg'))

            self.assertTrue(af.validate())

        self.assertTrue(Aptofile.validateFile(f))

    def testImageMissingDate(self):
        f = 'tests/image_missing_date.apt'
        with Aptofile.create(f,'image') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the image')
            af.setImageName('The image name')
            af.setImageDescription('An image of something')
            af.setImageGeoreference( 10.4344, 63.4181, 150.60)
            af.setImageBounds(['data:,bounds as a string'])
            af.addImageFile(('tests/image/image.jpg','image.jpg'))

            self.assertTrue(af.validate())
            del af.manifest['image']['created']
        self.assertFalse(Aptofile.validateFile(f))

    def testImageIncorrectDate(self):
        f = 'tests/image_missing_date.apt'
        with Aptofile.create(f,'image') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the image')
            af.setImageName('The image name')
            af.setImageDescription('An image of something')
            af.setImageGeoreference( 10.4344, 63.4181, 150.60)
            af.setImageBounds(['data:,bounds as a string'])
            af.addImageFile(('tests/image/image.jpg','image.jpg'))

            self.assertTrue(af.validate())
            af.manifest['image']['created'] = '23.05.13'
            af.validate()
        self.assertFalse(Aptofile.validateFile(f))

    def testImageMissingFileAndGenerator(self):
        f = 'tests/image_missing_file_and_generator.apt'
        with Aptofile.create(f,'image') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the image')
            af.setImageName('The image name')
            af.setImageDescription('An image of something')
            af.setImageGeoreference( 10.4344, 63.4181, 150.60)
            af.setImageBounds(['data:,bounds as a string'])
            af.manifest['image']['data']=['image.jpg']
            del af.manifest['generator']
            self.assertFalse(af.validate())
        self.assertFalse(Aptofile.validateFile(f))


    def testImageMissingGenerator(self):
        f = 'tests/image_missing_generator.apt'
        with Aptofile.create(f,'image') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the image')
            af.setImageName('The image name')
            af.setImageDescription('An image of something')
            af.setImageGeoreference( 10.4344, 63.4181, 150.60)
            af.setImageBounds(['data:,bounds as a string'])
            af.addImageFile(('tests/image/image.jpg','image.jpg'))

            self.assertTrue(af.validate())
            del af.manifest['generator']
        self.assertFalse(Aptofile.validateFile(f))

class testVideo(unittest.TestCase):

    def testVideo(self):
        f = 'tests/video.apt'
        with Aptofile.create(f,'video') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the video')
            af.setVideoName('The video name')
            af.setVideoDescription('A video of something')
            af.setVideoGeoreference( 10.4344, 63.4181, 150.60)
            af.addVideoFile(('tests/video/video.avi','video.avi'))

            self.assertTrue(af.validate())
        self.assertTrue(Aptofile.validateFile(f))

    def testVideoMissingFile(self):
        f = 'tests/video_missing_file.apt'
        with Aptofile.create(f,'video') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the video')
            af.setVideoName('The video name')
            af.setVideoDescription('A video of something')
            af.setVideoGeoreference( 10.4344, 63.4181, 150.60)

            self.assertFalse(af.validate())
        self.assertFalse(Aptofile.validateFile(f))

    def testVideoFileNotFound(self):
        f = 'tests/video_file_not_found.apt'
        with Aptofile.create(f,'video') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the video')
            af.setVideoName('The video name')
            af.setVideoDescription('A video of something')
            af.setVideoGeoreference( 10.4344, 63.4181, 150.60)

            af.manifest['video']['data']=['video.avi']
            self.assertFalse(af.validate())
        self.assertFalse(Aptofile.validateFile(f))

    def testVideoMissingName(self):
        f = 'tests/video_missing_name.apt'
        with Aptofile.create(f,'video') as af:
            af.setGenerator(program='aptfile.py',creator='Aptomar AS')
            af.setDescription('This is a description of the video')
            af.setVideoName('The video name')
            af.setVideoDescription('A video of something')
            af.setVideoGeoreference( 10.4344, 63.4181, 150.60)
            af.addVideoFile(('tests/video/video.avi','video.avi'))

            self.assertTrue(af.validate())
            del af.manifest['video']['name']
        self.assertFalse(Aptofile.validateFile(f))

class TestPoint(unittest.TestCase):

    def testPoint(self):
        f = 'tests/point.apt'
        with Aptofile.create(f,'point') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the point.')
            af.setPointName('The Point')
            af.setPointDescription('This is a description of a point.')
            af.setPointType('boat')
            af.setPointGeometry('data:data_describing_the_point')

            self.assertTrue(af.validate())
        self.assertTrue(Aptofile.validateFile(f))

    def testPointInvalidType(self):
        f = 'tests/point_invalid_type.apt'
        with Aptofile.create(f,'point') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the point.')
            af.setPointName('The Point')
            af.setPointDescription('This is a description of a point.')
            af.setPointType('boat')
            af.setPointGeometry('data:data_describing_the_point')

            self.assertTrue(af.validate())
            af.manifest['point']['object-type'] = 'UFO'
        self.assertFalse(Aptofile.validateFile(f))


    def testRoute(self):
        f = 'tests/route.apt'
        with Aptofile.create(f,'route') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the route.')
            af.setRouteName('The Route')
            af.setRouteDescription('This is a description of the route.')
            af.setRouteGeometry('data:data_describing_the_route')

            self.assertTrue(af.validate())
        self.assertTrue(Aptofile.validateFile(f))

    def testRouteMissingGeometry(self):
        f = 'tests/route.apt'
        with Aptofile.create(f,'route') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the route.')
            af.setRouteName('The Route')
            af.setRouteDescription('This is a description of the route.')
            af.setRouteGeometry('data:data_describing_the_route')
            self.assertTrue(af.validate())
            del af.manifest['route']['geometry']

        self.assertFalse(Aptofile.validateFile(f))

class TestArea(unittest.TestCase):

    def testArea(self):
        f = 'tests/area.apt'
        with Aptofile.create(f,'area') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the area.')
            af.setAreaName('The Point')
            af.setAreaDescription('This is a description of the area.')
            af.setAreaGeometry('data:data_describing_the_area')
            self.assertTrue(af.validate())
        self.assertTrue(Aptofile.validateFile(f))

    def testAreaMissingAreaDescription(self):
        f = 'tests/area_missing_area_desc.apt'
        with Aptofile.create(f,'area') as af:
            af.setGenerator('aptfile.py','Aptomar AS')
            af.setDescription('This is a description of the area.')
            af.setAreaName('The Point')
            af.setAreaDescription('This is a description of a area.')
            af.setAreaGeometry('data:data_describing_the_area')
            self.assertTrue(af.validate())
            del af.manifest['area']['description']
        self.assertFalse(Aptofile.validateFile(f))

if __name__=='__main__':
    unittest.main()
