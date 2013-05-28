# apt_test.py
# Copyright (c) 2013 Aptomar AS, All Rights Reserved
#
# Author: Matt Long <matthew.long@aptomar.com>
# Date:   2013-03-04
#
# This is a simple set of tests for the aptomar file format schema.  The main idea is to start with
# a set of validating files, then show that removing required elemets causes validation errors.


import unittest
import json
from jsonschema import validate, Draft3Validator, Draft4Validator, SchemaError, ValidationError, FormatChecker

SCHEMA_FILE = "../src/apt.schema.json"
VALIDATOR = Draft4Validator

def load_json_from_file(filename):
	f = open(filename, 'r')
	data = json.loads(f.read())
	f.close()
	return data

def validate_or_fail(self, instance, schema):
	try:
		validate(instance, schema, VALIDATOR, format_checker=FormatChecker())
	except ValidationError as err:
		self.fail("Instance validation raised an error: " + repr(err))	

def expect_validate_failure(self, instance, schema):
	with self.assertRaises(ValidationError) as ex:
		validate(instance, schema, VALIDATOR, format_checker=FormatChecker())

class TestJsonSchema(unittest.TestCase):

	def test_check_uri(self):
		self.assertTrue("uri" in FormatChecker.checkers)

	def test_check_date_time(self):
		self.assertTrue("date-time" in FormatChecker.checkers)


class TestSchema(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)

	def test_schema_validates(self):
		try:
			VALIDATOR.check_schema(self.schema)
		except SchemaError as err:
			self.fail("Schema validation raised an error: " + repr(err))


class TestManifest(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/header.json")

	def test_valid_manifest_header(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_manifest_missing_date(self):
		del self.inst["date"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_manifest_missing_description(self):
		del self.inst["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_manifest_missing_version(self):
		del self.inst["manifest_version"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_manifest_missing_generator(self):
		del self.inst["generator"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_manifest_bad_date(self):
		self.inst["date"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_manifest_disallow_additional_properties(self):
		self.inst["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)



class TestArea(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/area.json")

	def test_valid_area(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_area_bad_created_date(self):
		self.inst["area"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_invalid_type(self):
		self.inst["area"]["geometry"]["type"] = "ewk"
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_no_data(self):
		del self.inst["area"]["geometry"]["data"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_no_created_date(self):
		del self.inst["area"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_no_desc(self):
		del self.inst["area"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_no_geom(self):
		del self.inst["area"]["geometry"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_no_name(self):
		del self.inst["area"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_disallow_additional_properties(self):
		self.inst["area"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

	def test_area_data_from_string(self):
		self.inst["area"]["geometry"]["data"] = ["data:,Geometry string"]
		validate_or_fail(self, self.inst, self.schema)


class TestAsset(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/asset.json")

	def test_valid_asset(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_valid_asset_multi(self):
		inst = load_json_from_file("tests/valid/asset-multi.json")
		validate_or_fail(self, inst, self.schema)

	def test_asset_disallow_additional_properties(self):
		self.inst["asset"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_groups(self):
		del self.inst["asset"]["groups"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layers(self):
		del self.inst["asset"]["layers"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_group_elem(self):
		del self.inst["asset"]["groups"]["group-1"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layer_elem(self):
		del self.inst["asset"]["layers"]["layer-1"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_group_layers(self):
		del self.inst["asset"]["groups"]["group-1"]["layers"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_group_name(self):
		del self.inst["asset"]["groups"]["group-1"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layer_style(self):
		del self.inst["asset"]["layers"]["layer-1"]["style"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layer_name(self):
		del self.inst["asset"]["layers"]["layer-1"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layer_geometry(self):
		del self.inst["asset"]["layers"]["layer-1"]["geometry"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_asset_missing_layer_resources_ok(self):
		del self.inst["asset"]["layers"]["layer-1"]["resources"]
		validate_or_fail(self, self.inst, self.schema)

class TestImage(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/image.json")

	def test_valid_image(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_image_bad_created_date(self):
		self.inst["image"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_file(self):
		del self.inst["image"]["data"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_created_date(self):
		del self.inst["image"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_desc(self):
		del self.inst["image"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_name(self):
		del self.inst["image"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_missing_lat(self):
		del self.inst["image"]["georeference"]["latitude"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_missing_lon(self):
		del self.inst["image"]["georeference"]["longitude"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_georeference(self):
		del self.inst["image"]["georeference"]
		validate_or_fail(self, self.inst, self.schema)

	def test_image_disallow_additional_properties(self):
		self.inst["image"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_no_bounds(self):
		del self.inst["image"]["bounds"]
		validate_or_fail(self, self.inst, self.schema)

	def test_image_invalid_bounds_type(self):
		self.inst["image"]["bounds"]["type"] = "foo"
		expect_validate_failure(self, self.inst, self.schema)

	def test_image_bounds_file(self):
		self.inst["image"]["bounds"]["data"] = ["file1", "file2"]
		validate_or_fail(self, self.inst, self.schema)

class TestRadar(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/radar.json")

	def test_valid_image(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_radar_bad_created_date(self):
		self.inst["image"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_no_file(self):
		del self.inst["image"]["data"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_no_created_date(self):
		del self.inst["image"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_no_desc(self):
		del self.inst["image"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_no_name(self):
		del self.inst["image"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_disallow_additional_properties(self):
		self.inst["image"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_no_bounds(self):
		del self.inst["image"]["bounds"]
		validate_or_fail(self, self.inst, self.schema)

	def test_radar_bounds_missing_pwidth(self):
		del self.inst["image"]["bounds"]["pixel_width"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_bounds_missing_pheight(self):
		del self.inst["image"]["bounds"]["pixel_height"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_bounds_missing_punits(self):
		del self.inst["image"]["bounds"]["pixel_units"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_bounds_missing_rotx(self):
		del self.inst["image"]["bounds"]["rotation_x"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_radar_bounds_missing_roty(self):
		del self.inst["image"]["bounds"]["rotation_y"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_observation_missing_date(self):
		del self.inst["observation"]["date"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_observation_missing_nwbounds(self):
		del self.inst["observation"]["bounds_nw"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_observation_missing_sebounds(self):
		del self.inst["observation"]["bounds_se"]
		expect_validate_failure(self, self.inst, self.schema)		

	def test_sensor_missing_shortname(self):
		del self.inst["sensor"]["shortname"]
		expect_validate_failure(self, self.inst, self.schema)		

	def test_sensor_missing_location_name(self):
		del self.inst["sensor"]["location_name"]
		expect_validate_failure(self, self.inst, self.schema)		

	def test_sensor_missing_manufacturer_name(self):
		del self.inst["sensor"]["manufacturer_name"]
		expect_validate_failure(self, self.inst, self.schema)		

	def test_sensor_missing_model_number(self):
		del self.inst["sensor"]["model_number"]
		expect_validate_failure(self, self.inst, self.schema)		

	def test_sensor_missing_serial_number(self):
		del self.inst["sensor"]["serial_number"]
		expect_validate_failure(self, self.inst, self.schema)		



class TestPoint(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/point.json")

	def test_valid_point(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_point_bad_created_date(self):
		self.inst["point"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_invalid_type(self):
		self.inst["point"]["object-type"] = "foo"
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_no_data(self):
		del self.inst["point"]["geometry"]["data"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_no_created_date(self):
		del self.inst["point"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_no_desc(self):
		del self.inst["point"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_no_geom(self):
		del self.inst["point"]["geometry"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_no_name(self):
		del self.inst["point"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_point_disallow_additional_properties(self):
		self.inst["point"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

class TestRoute(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/route.json")

	def test_valid_route(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_route_bad_created_date(self):
		self.inst["route"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_invalid_type(self):
		self.inst["route"]["geometry"]["type"] = "ewk"
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_no_data(self):
		del self.inst["route"]["geometry"]["data"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_no_created_date(self):
		del self.inst["route"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_no_desc(self):
		del self.inst["route"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_no_geom(self):
		del self.inst["route"]["geometry"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_no_name(self):
		del self.inst["route"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_route_disallow_additional_properties(self):
		self.inst["route"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)

class TestVideo(unittest.TestCase):

	def setUp(self):
		self.schema = load_json_from_file(SCHEMA_FILE)
		self.inst = load_json_from_file("tests/valid/video.json")

	def test_valid_video(self):
		validate_or_fail(self, self.inst, self.schema)

	def test_video_bad_created_date(self):
		self.inst["video"]["created"] = "tomorrow"
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_no_created_date(self):
		del self.inst["video"]["created"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_no_desc(self):
		del self.inst["video"]["description"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_no_name(self):
		del self.inst["video"]["name"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_missing_lat(self):
		del self.inst["video"]["georeference"]["latitude"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_missing_lon(self):
		del self.inst["video"]["georeference"]["longitude"]
		expect_validate_failure(self, self.inst, self.schema)

	def test_video_no_georeference(self):
		del self.inst["video"]["georeference"]
		validate_or_fail(self, self.inst, self.schema)

	def test_video_disallow_additional_properties(self):
		self.inst["video"]["extra"] = "large"
		expect_validate_failure(self, self.inst, self.schema)


if __name__ == '__main__':
    unittest.main()
