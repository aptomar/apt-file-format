################################################################
#                                                              #
# aptofile.py                                                  #
# Copyright (c) 2013 Aptomar AS, All Rights Reserved           #
#                                                              #
# Author: Jarle Bauck Hamar: <jarle.hamar@aptomar.com>         #
# Date: 2013-03-11                                             #
#                                                              #
################################################################

#from __future__ import unicode_literals

import jsonschema
import json
import zipfile
import sys,os
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.ERROR)

testVerbose = False
def testCase(f):
    """
    Decorator for test case methods defined in the validate methods
    """
    def decorated(self,*args):
        if testVerbose: print "Testing %s... "%f.__name__,
        try:
            f(self,*args)
            if testVerbose: print "ok"
            return True
        except Exception as e:
            if testVerbose:
                traceback.print_exc()
                print "FAILED: %s"%e
            self.failedTests.append( (f.__name__, e) )
            return False
    return decorated

def writingMethod(f):
    """
    Decorator for methods that changes the manifest
    """
    def decorated(self,*args,**args2):
        self._assureWritable()
        ret = f(self,*args,**args2)
        if ret!=None: return ret
        else: return self.validate()
    return decorated

def stripFileName(fn):
    if fn.startswith('file:'):
        fn = fn[5:]
    return fn.lstrip('/').lstrip('\\')

class Aptofile:
    """
    Super class for Aptomar files

    IMPORTANT: Files in an archive cannot be updated, hence the files
    should be fully created before closing the files. If update is needed
    the content should be read from file, updated and then written to a
    new file. Since every change to the archive means an update of the
    manifest, this opening files with other modes than 'r' or 'w' is
    not supported.

    Provides static methods for validating a file, fetching manifest
    from a file, open a file and create a file.
    """

    MANIFEST_FILE = 'manifest.json'
    SCHEMA_FILE = 'apt.schema.json'
    VALIDATOR = jsonschema.Draft4Validator

    FILETYPES = ['asset','image','video','point','route','area']

    schema_file = os.path.join(os.path.dirname(__file__),SCHEMA_FILE)
    with open(schema_file) as fid:
        SCHEMA = json.load(fid)

    @staticmethod
    def validateFile(filename):
        """
        Validate an aptomar file

        Returns a boolean. To get the errors:

        with open(filename) as fid:
            errs = fid.getFailedTests()

        which then returns a list with each error as a tuple with
        (testname, exception) where exception is the exception
        raised by the method testname.

        """
        try:
            with Aptofile.open(filename) as af:
                return af.validate()
        except Exception as e:
            return False

    @staticmethod
    def getManifestFromFile(filename):
        with zipfile.ZipFile(filename) as zf:
            return json.loads(zf.read(Aptofile.MANIFEST_FILE))

    @staticmethod
    def open(filename,mode='r'):
        """
        Open an existing file.

        Returns an instance of the proper subclass dependent on filetype,
        which is found by reading the manifest.

        Only currently supported mode is 'r', since zipfile content
        cannot be updated. For creating a new file, use Aptofile.create().

        Supports the 'with' statement:
        with Aptofile.open(fn) as fid:
            #something
        """
        if mode == 'w':
            raise Exception("Use Aptofile.create() to create new file")


        zf = zipfile.ZipFile(filename)
        try:
            manifest = json.loads(zf.read(Aptofile.MANIFEST_FILE))
        except Exception as e:
            zf.close()
            raise e

        if manifest.has_key('asset'):
            return Assetfile(zf,manifest)
        if manifest.has_key('image'):
            return Imagefile(zf,manifest)
        if manifest.has_key('video'):
            return Videofile(zf,manifest)
        if manifest.has_key('point'):
            return Pointfile(zf,manifest)
        if manifest.has_key('route'):
            return Routefile(zf,manifest)
        if manifest.has_key('area'):
            return Areafile(zf,manifest)
        zf.close()
        raise NotImplementedError("File type not implemented")

    @staticmethod
    def create(filename,fileType,**args):
        """
        Create a new file

        Creates the zipfile archive, initialises the manifest
        and returns the proper subclass dependent on fileType.
        Because files cannot be updated, the manifest is not written
        to the archive until close(). Hence, close() is vital and
        the use of 'with' statement is adviced.

        Supports the 'with' statement:
        with Aptofile.create(fn,type) as fid:
            # Add content
        """
        if fileType not in Aptofile.FILETYPES:
            raise Exception("Invalid filetype: %s"%fileType)
        zf = zipfile.ZipFile(filename,"w",zipfile.ZIP_STORED)
        manifest={}
        manifest['description']=args.get('description','')
        manifest['generator']=args.get('generator',{})
        if not manifest['generator']:
            manifest['generator']['program']=args.get('program','')
            manifest['generator']['creator']=args.get('creator','')
        manifest['manifest_version']=args.get('manifest_version',1)
        try:
            d = datetime.utcfromtimestamp(int(time.time())).isoformat()+'Z'
        except Exception as e:
            zf.close()
            raise e
        manifest['date']=args.get('date',d)
        manifest[fileType] = {}

        if fileType=='asset': return Assetfile(zf,manifest)
        elif fileType=='image': return Imagefile(zf,manifest)
        elif fileType=='video': return Videofile(zf,manifest)
        elif fileType=='point': return Pointfile(zf,manifest)
        elif fileType=='route': return Routefile(zf,manifest)
        elif fileType=='area': return Areafile(zf,manifest)

        zf.close()
        return None

    # Methods for checking filetype, overriden by subclass
    def isAssetfile(self): return False
    def isImagefile(self): return False
    def isVideofile(self): return False
    def isPointfile(self): return False
    def isRoutefile(self): return False
    def isAreafile(self): return False

    def __init__(self,zipfile,manifest=None):
        """
        Initialise the file instance.

        zipfile should be an opened zipfile instance. Only currently supported
        modes are 'r' and 'w'.
        """
        self.zipfile = zipfile
        self.filename = zipfile.filename
        self.mode = zipfile.mode

        if self.mode not in ['r','w']:
            # Append not supported, since it is not possible to
            # update a file (e.g. the manifest) in the zipfile
            raise Exception("Mode '%s' not supported"%self.mode)


        self.manifest = manifest
        if not manifest:
            if self.mode in 'r':
                self._readManifest()
            else: raise Exception("Manifest needed when mode!='r'")
        self.failedTests = []
        self.valid = self.validate()

    # Enable with statement:
    def __enter__(self): return self
    def __exit__(self,type,value,tb): self.close()

    def _checkFiles(self,files):
        for f in files:
            if not ':' in f or f.startswith('file:'):
                f = stripFileName(f)
                if not f in self.namelist() and \
                        not f.replace('/','\\') in self.namelist() and \
                        not f.replace('\\','/') in self.namelist():
                    raise IOError("File not found: %s"%f)
            elif f.startswith('http://'):
                pass
            elif f.startswith('data:'):
                pass
            else: raise Exception("Invalid uri format: %s"%f)


    def _checkTimestamp(self,stamp):
        pass

    def _readManifest(self):
        self.manifest = json.loads(self.zipfile.read(Aptofile.MANIFEST_FILE))
    def _writeManifest(self):
        self.zipfile.writestr(Aptofile.MANIFEST_FILE,json.dumps(self.manifest,indent=4))
    def _assureWritable(self):
        if self.mode != 'w':
            raise Exception("File not writable.")


    def close(self):
        """
        Closes the file

        If the mode is 'w' it also writes the manifest. This is done
        only here, so closing of files are important. Use 'with'.
        """
        if self.mode == 'w': self._writeManifest()
        self.zipfile.close()
    def getManifest(self): return self.manifest
    def getPrettyManifest(self,indent=4):
        return json.dumps(self.manifest,indent=indent)
    def getDescription(self): return self.manifest['description']
    def namelist(self):
        return [ stripFileName(fn) for fn in self.zipfile.namelist() ]
    def readfile(self,fn):
        fn = stripFileName(fn)
        if fn in self.namelist():
            return self.zipfile.read(fn)
        elif fn.replace('\\','/') in self.namelist():
            return self.zipfile.read(fn.replace('\\','/'))
        elif fn.replace('/','\\') in self.namelist():
            return self.zipfile.read(fn.replace('/','\\'))
        else: raise Exception("File %s not found"%fn)


    @writingMethod
    def writefile(self,file):
        """
        Write a file to the archive

        file is a string with a local file (e.g. file://foo/bar/foobar.txt) or
        a network file (e.g. "http://www.foobar.com/foo.txt"). It may
        also be a tuple where the second element is a string with the
        archive name of the file. If a local file is added without this,
        the archive name will be the same as filename, but without a drive
        letter and with leading path separators removed.
        """
        if type(file)==tuple:
            try:
                self.zipfile.write(file[0],stripFileName(file[1]))
            except Exception as e:
                return False
        elif not ':' in file or file.startswith('file:'):
            self.zipfile.write(stripFileName(file))
        elif file.startswith('data:'):
            pass
        elif file.startswith('http:'):
            pass
        else:
            raise Exception("Invalid uri format: %s"%file)

        return True

    @writingMethod
    def setGenerator(self,program='',creator=''):
        if program: self.manifest['generator']['program'] = program
        if creator: self.manifest['generator']['creator'] = creator

    @writingMethod
    def setDate(self,date):
        self.manifest['date']=date

    @writingMethod
    def setDescription(self,desc):
        self.manifest['description']=desc

    def getFailedTests(self): return self.failedTests
    def validate(self):
        """
        Validate the file

        Performs tests which are defined as methods decorated with testCase.
        Each method throws an exception which is handeled in the decorator.
        """
        self.failedTests = []
        ret = True
        @testCase
        def testZip(self): self.zipfile.testzip()
        ret = testZip(self) and ret

        @testCase
        def validateManifest(self):
            jsonschema.validate(self.manifest, Aptofile.SCHEMA,
                                Aptofile.VALIDATOR,
                                format_checker = jsonschema.FormatChecker())
        ret = validateManifest(self) and ret

        @testCase
        def fileDate(self): self._checkTimestamp(self.manifest['date'])
        ret = fileDate(self) and ret

        return ret

class Assetfile(Aptofile):

    LAYER_FIELDS = ['geometry','style','resources']

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            asset = self.manifest['asset']
            asset['layers']=asset.get('layers',{})
            asset['groups']=asset.get('groups',{})

    def isAssetfile(self): return True



    @writingMethod
    def addLayer(self,key , **args):
        """
        Add a layer

        Argument       Description     Default
        -------------  --------------  ----------
        key            layer-key       Required
        name           Layer name      key
        geometry_data  List of files*  []
        geometry_type  Geometry type   'text/x-shapefile'
        style_data     List of files*  []
        style_type     Style type      'text/x-sld'
        resources      List of files*  Not set

        *List of files is a list where each element is
        string with a local file (e.g. file://foo/bar/foobar.txt) or
        a network file (e.g. "http://www.foobar.com/foo.txt"). It may
        also be a tuple where the second element is a string with the
        archive name of the file. If a local file is added without this,
        the archive name will be the same as filename, but without a drive
        letter and with leading path separators removed.
        """
        layer = {}
        layer['name']=args.get('name',key)
        layer['geometry']={}
        layer['geometry']['type'] = args.get('geometry_type','text/x-shapefile')
        layer['style']={}
        layer['style']['type'] = args.get('style_type','text/x-sld')
        if 'resources' in args:
            layer['resources']=args['resources']
        self.manifest['asset']['layers']=self.manifest['asset'].get('layers',{})
        self.manifest['asset']['layers'][key]=layer

        # Add the files
        for field in Assetfile.LAYER_FIELDS:
            if args.has_key(field+"_data"):
                for f in args[field+"_data"]:
                    self.addFile2Layer(f,key,field)

    @writingMethod
    def addGroup(self, key, name='', layers=None):
        """
        Add a new group

        Input:
        Argument Description     Default
        -------- --------------- --------
        key      Group key       Required
        name     Group name      key
        layers   List of members []

        Returns: bool for valid status

        There is no requirement that the layers exists.
        if the file is
        """
        group = {}
        if name: group['name'] = name
        else: group['name'] = key
        if layers: group['layers'] = layers
        else: group['layers'] = []

        self.manifest['asset']['groups'][key]=group


    @writingMethod
    def addFile2Layer(self,file,layerKey,fileType,writeFile=True):
        """
        Add a file to a layer

        Input:
        Argument  Description
        --------- -----------------
        file      string or tuple*
        layerKey  key of layer
        fileType  "geometry", "style" or "resources"

        Returns: bool for valid status

        file is a string with a local file (e.g. file://foo/bar/foobar.txt) or
        a network file (e.g. "http://www.foobar.com/foo.txt"). It may
        also be a tuple where the second element is a string with the
        archive name of the file. If a local file is added without this,
        the archive name will be the same as filename, but without a drive
        letter and with leading path separators removed.
        """
        if fileType not in Assetfile.LAYER_FIELDS:
            raise Exception("Invalid file type: %s"%fileType)

        if writeFile: self.writefile(file)
        if type(file)==tuple: file = file[1]
        if not self.manifest['asset']['layers'][layerKey].has_key(fileType):
            self.manifest['asset']['layers'][layerKey][fileType]={}
        ls=self.manifest['asset']['layers'][layerKey][fileType].get('data',[])
        ls.append(file)
        self.manifest['asset']['layers'][layerKey][fileType]['data']=ls

    def validate(self):
        ret = Aptofile.validate(self)

        @testCase
        def isAssetFile(self): self.manifest['asset']
        ret = isAssetFile(self) and ret

        @testCase
        def assetFiles(self):
            files = []
            for v in self.manifest['asset']['layers'].itervalues():
                if not v['geometry']['data']:
                    raise Exception("Layer %s has no geometry data"%v['name'])
                for key in ['geometry','style']:
                    files.extend(v[key]['data'])
                if v.has_key('resources'):
                    files.extend(v['resources']['data'])
            self._checkFiles(files)
        ret = assetFiles(self) and ret

        @testCase
        def assetGroups(self):
            layerDict = self.manifest['asset']['layers']
            for v in self.manifest['asset']['groups'].itervalues():
                for layername in v['layers']:
                    if not layerDict.has_key(layername):
                        raise Exception("Layer '%s' in group '%s' does not exist"%
                                        (layername,v['name']))
        ret = assetGroups(self) and ret

        self.valid=ret
        return ret


class Imagefile(Aptofile):

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            imageDict = self.manifest['image']
            imageDict['created']=imageDict.get('created',self.manifest['date'])
            imageDict['description']=imageDict.get('description','')
            imageDict['name']=imageDict.get('name','')

    def isImagefile(self): return True

    @writingMethod
    def setImageName(self,name):
        self.manifest['image']['name']=name

    @writingMethod
    def setImageDescription(self,desc):
        self.manifest['image']['description']=desc

    @writingMethod
    def setImageCreated(self, timestamp):
        self.manifest['image']['created']=timestamp

    @writingMethod
    def addImageFile(self, file):
        self.writefile(file)
        if type(file)==tuple: file = file[1]
        self.manifest['image']['data']=[file]

    @writingMethod
    def setImageGeoreference(self, lon, lat, elev):
        d={}
        d['longitude']=lon
        d['latitude']=lat
        d['elevation']=elev
        self.manifest['image']['georeference']=d

    @writingMethod
    def setImageBounds(self, data, type="text/x-worldfile"):
        d={}
        d['type']=type
        d['data']=data
        self.manifest['image']['bounds']=d

    def validate(self):
        ret = Aptofile.validate(self)
        @testCase
        def isImageFile(self): self.manifest['image']
        ret = isImageFile(self) and ret

        @testCase
        def imageFiles(self):
            if not self.manifest['image']['data']:
                raise Exception("Image file missing")
            self._checkFiles(self.manifest['image']['data'])
        ret = imageFiles(self) and ret

        @testCase
        def imageDate(self): self._checkTimestamp(self.manifest['image']['created'])
        ret = imageDate(self) and ret

        self.valid=ret
        return ret

class Videofile(Aptofile):

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            videoDict = self.manifest['video']
            videoDict['created']=videoDict.get('created',self.manifest['date'])
            videoDict['description']=videoDict.get('description','')
            videoDict['name']=videoDict.get('name','')

    def isVideofile(self): True

    @writingMethod
    def setVideoName(self, name):
        self.manifest['video']['name'] = name

    @writingMethod
    def setVideoDescription(self, desc):
        self.manifest['video']['description'] = desc

    @writingMethod
    def setVideoCreated(self, timestamp):
        self.manifest['video']['created']=timestamp

    @writingMethod
    def addVideoFile(self, file):
        self.writefile(file)
        if type(file)==tuple: file = file[1]
        self.manifest['video']['data']=[file]

    @writingMethod
    def setVideoGeoreference(self, lon, lat, elev):
        d={}
        d['longitude']=lon
        d['latitude']=lat
        d['elevation']=elev
        self.manifest['video']['georeference']=d

    def validate(self):
        ret = Aptofile.validate(self)

        @testCase
        def isVideoFile(self): self.manifest['video']
        ret = isVideoFile(self) and ret

        @testCase
        def videoFiles(self): self._checkFiles(self.manifest['video']['data'])
        ret = videoFiles(self) and ret
        @testCase
        def videoDate(self):
            self._checkTimestamp(self.manifest['video']['created'])
        ret = videoDate(self) and ret

        self.valid=ret
        return ret

class Pointfile(Aptofile):

    OBJECT_TYPES = ['boat','bouy','debris','fishfarm','green','oil',
                    'personel','red','unknown','vessel','yellow']

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            pointDict = self.manifest['point']
            pointDict['created'] = pointDict.get('created',self.manifest['date'])
            pointDict['description'] = pointDict.get('description','')
            pointDict['name'] = pointDict.get('name','')
            pointDict['object-type'] = pointDict.get('object-type','unknown')
            pointDict['geometry'] = pointDict.get('geometry',{})

    def isPointfile(self): True

    @writingMethod
    def setPointName(self,name): self.manifest['point']['name']

    @writingMethod
    def setPointDescription(self, desc):
        self.manifest['point']['description'] = desc

    @writingMethod
    def setPointCreated(self, timestamp):
        self.manifest['point']['created'] = timestamp

    @writingMethod
    def setPointType(self, type):
        type = type.lower()
        if not type in Pointfile.OBJECT_TYPES:
            raise Exception("Invalid type %s"%type)
        self.manifest['point']['object-type'] = type

    @writingMethod
    def setPointGeometry(self, file, gType = 'text/x-ewkt'):
        self.writefile(file)
        if type(file)==tuple: file = file[1]
        self.manifest['point']['geometry']['data'] = [file]
        self.manifest['point']['geometry']['type'] = gType

    def validate(self):
        ret = Aptofile.validate(self)

        @testCase
        def isPointFile(self): self.manifest['point']
        ret =  isPointFile(self) and ret

        @testCase
        def pointDate(self):
            self._checkTimestamp(self.manifest['point']['created'])
        ret = pointDate(self) and ret

        @testCase
        def pointType(self):
            pt = self.manifest['point']['object-type']
            if not pt.lower() in Pointfile.OBJECT_TYPES:
                raise Exception("Invalid object type: '%s'"%pt)
        ret = pointType(self) and ret

        self.valid=ret
        return ret

class Routefile(Aptofile):

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            routeDict = self.manifest['route']
            routeDict['name'] = routeDict.get('name','')
            routeDict['description'] = routeDict.get('description','')
            routeDict['created'] = routeDict.get('created',self.manifest['date'])
            routeDict['geometry'] = routeDict.get('geometry',{})

    def isRoutefile(self): True

    @writingMethod
    def setRouteName(self, name):
        self.manifest['route']['name'] = name

    @writingMethod
    def setRouteDescription(self, desc):
        self.manifest['route']['description'] = desc


    @writingMethod
    def setRouteCreated(self, timestamp):
        self.manifest['route']['created'] = timestamp

    @writingMethod
    def setRouteGeometry(self, file, gType = 'text/x-ewkt'):
        self.writefile(file)
        if type(file)==tuple: file = file[1]
        self.manifest['route']['geometry']['data'] = [file]
        self.manifest['route']['geometry']['type'] = gType

    def validate(self):
        ret = Aptofile.validate(self)

        @testCase
        def isRouteFile(self): self.manifest['route']
        ret = isRouteFile(self) and ret

        @testCase
        def routeDate(self):
            self._checkTimestamp(self.manifest['route']['created'])
        ret = routeDate(self) and ret

        self.valid=ret
        return ret

class Areafile(Aptofile):

    def __init__(self, zipfile, manifest=None):
        Aptofile.__init__(self, zipfile, manifest)

        if self.mode == 'w':
            areaDict = self.manifest['area']
            areaDict['name'] = areaDict.get('name','')
            areaDict['description'] = areaDict.get('description','')
            areaDict['created'] = areaDict.get('created',self.manifest['date'])
            areaDict['geometry'] = areaDict.get('geometry',{})

    def isAreafile(self): True

    @writingMethod
    def setAreaName(self, name):
        self.manifest['area']['name'] = name

    @writingMethod
    def setAreaDescription(self, desc):
        self.manifest['area']['description'] = desc


    @writingMethod
    def setAreaCreated(self, timestamp):
        self.manifest['area']['created'] = timestamp

    @writingMethod
    def setAreaGeometry(self, file, gType = 'text/x-ewkt'):
        self.writefile(file)
        if type(file)==tuple: file = file[1]
        self.manifest['area']['geometry']['data'] = [file]
        self.manifest['area']['geometry']['type'] = gType

    def validate(self):
        ret = Aptofile.validate(self)

        @testCase
        def isAreaFile(self): self.manifest['area']
        ret = isAreaFile(self) and ret

        @testCase
        def areaDate(self):
            self._checkTimestamp(self.manifest['area']['created'])
        ret = areaDate(self) and ret

        self.valid=ret
        return ret



