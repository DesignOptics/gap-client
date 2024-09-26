import gap_client as gap
import csv
import datetime
import html
import logging
import math
import os
import pprint
import pytest
import random
import re
from ..common import *

logger = logging.getLogger(__name__)



# Test fixtures
#######################################################################


soa_csv_fn = 'data/SoA.csv'



@pytest.fixture(scope='function')
def gap_client(request, do_debug = False):
	project_folder = os.path.join(here, "data/catalogue")
	if do_debug:
		logger.info(f"here:{here}, project_folder:{project_folder}")
	gap_data = {
		  "base_url": "https://grc.arribatec.cloud"
		, "client_id": get_env("TEST_GAP_CLIENT_ID")
		, "client_secret": get_env("TEST_GAP_CLIENT_SECRET")
		, "client_token": get_env("TEST_GAP_TOKEN")
		, "account_id": get_env("TEST_GAP_ACCOUNT_ID")
	}
	if do_debug:
		logger.info(pprint.pformat(gap_data))
	client = gap.Client(**gap_data)
	assert(client)
	def teardown():
		logger.info("TEARDONE")
		client = None
	request.addfinalizer(teardown)
	return client


# Test cases
#######################################################################


def test_gap_membership(gap_client):
	memberships, memberships_err = gap_client.get_memberships()
	assert memberships, memberships_err
	assert not memberships_err, memberships_err
	logger.info(pprint.pformat(memberships))

# OK 2023-11-20
def test_gap_get_audits(gap_client):
	audits, audits_err = gap_client.get_audits(do_debug = True)
	assert audits, audits_err
	assert not audits_err, audits_err
	logger.info(pprint.pformat(audits))

# OK 2023-12-08
def test_gap_get_audit_goals(gap_client):
	audit_goals, audit_goals_err = gap_client.get_audit_goals(do_debug=True)
	assert audit_goals, audit_goals_err
	assert not audit_goals_err, audit_goals_err
	logger.info(pprint.pformat(audit_goals))


# OK 2023-12-21
def test_get_custom_fields(gap_client):
	custom_fields, custom_fields_err = gap_client.get_custom_fields(do_debug=False)
	assert custom_fields, custom_fields_err
	assert not custom_fields_err, custom_fields_err
	logger.info(pprint.pformat(custom_fields))

def test_gap_create_audit_goal(gap_client):
	audit_id = 9503 # https://grc.arribatec.cloud/audits/9503
	query_body1 ={
#		  "id": 0
		  "title": "My Audit Goal"
		, "description": "<p>The best audit goal in years</p>"
		, "parent_id": audit_id
		, "status": gap.Status.not_started
		, "guide": "Here is how to do it. A. B. C."
		, "documentation": "my documentation"
		, "note": "Remember to floss"
		, "icon": "book"
		, "custom_field": "my custom field"
		, "archived": 0
	}
	query_body =	{
		  "title": "My Audit Goal"
		, "parent_id": audit_id
		, "description": "<p>The best audit goal in years</p>"
		, "status": gap.Status.not_started
		, "guide": "<p>Here is how to do it. A. B. C.</p>"
		, "documentation": "<p>Here is how to do it. A. B. C.</p>"
		, "note": None
		, "icon": {
			"value": None
			, "color": None
		}
	}
	audit_goal, audit_goal_err = gap_client.create_audit_goal(raw_audit_goal=query_body)
	assert audit_goal, audit_goal_err
	assert not audit_goal_err, audit_goal_err
	logger.info(pprint.pformat(audit_goal))


def test_delete_audit(gap_client):
	audit_name = "Test Audit Delete"
	raw_audit_body = {
		  "title": audit_name
		, "description": sentence(5)
		, "overall_status": gap.Status.not_started
		, "note": sentence(10)
	}
	audit_res, audit_err = gap_client.create_audit(raw_audit = raw_audit_body)
	assert audit_res, audit_err
	assert not audit_err, audit_err
	delete_res, delete_err = gap_client.delete_audit(audit_res.get("id"), do_debug = True)
	assert not delete_err, delete_err


def test_patch_audit(gap_client):
	audit_name = sentence(3)
	# Make sure it does not exist
	audit_get_res, audit_get_err = gap_client.get_audit_by_title(audit_name)
	if audit_get_res:
		delete_res, delete_err = gap_client.delete_audit(audit_get_res.get("id"))
		assert not delete_err, delete_err
	# It should be deleted so if we find it, it is an error
	audit_get_res, audit_get_err = gap_client.get_audit_by_title(audit_name)
	assert not audit_get_res, audit_get_err
	# Create it
	raw_audit_body = {
		  "title": audit_name
		, "description": sentence(5)
		, "overall_status": "not_started"
		, "note": sentence(10)
	}
	audit_create_res, audit_create_err = gap_client.create_audit(raw_body = raw_audit_body, do_debug = True)
	assert audit_create_res, audit_create_err
	# Extract the id
	id = audit_create_res.get("id")
	logger.info(f"Created audit with id: {id}")
	assert id, "No id"
	# Patch #1: set name to "aaa"
	patch_audit_body1 = {
		"title": "aaa"
	}
	audit_patch_res, audit_patch_err = gap_client.patch_audit(id = id, raw_body = patch_audit_body1, do_debug = True)
	assert audit_patch_res, audit_patch_err
	# Patch #2: set name to "aaa"
	patch_audit_body2 = {
		"title": "bbb"
	}
	audit_patch_res, audit_patch_err = gap_client.patch_audit(id = id, raw_body = patch_audit_body2, do_debug = True)
	assert audit_patch_res, audit_patch_err
	# Cleanup
	delete_res, delete_err = gap_client.delete_audit(id = id)



def test_upsert_audit(gap_client):
	audit_name = "Test Audit Upsert"
	raw_audit_body = {
		"title": audit_name
	  , "description": sentence(5)
	  , "overall_status": gap.Status.not_started
	  , "note": sentence(10)
	}
	# Make sure it does not exist
	audit_get_res, audit_get_err = gap_client.get_audit_by_title(audit_name)
	if audit_get_res:
		delete_res, delete_err = gap_client.delete_audit(audit_get_res.get("id"))
		assert not delete_err, delete_err
	audit_get_res, audit_get_err = gap_client.get_audit_by_title(audit_name)
	# It should be deleted so if we find it, it is an error
	assert not audit_get_res, audit_get_err
	# Upsert test #1: when it does NOT exist
	raw_audit_body1 = {
		"title": audit_name
	  , "description": sentence(5)
	  , "overall_status": gap.Status.not_started
	  , "note": sentence(10)
	}
	audit_upsert_res, audit_upsert_err = gap_client.upsert_audit(raw_body = raw_audit_body1, do_debug = True)
	assert audit_upsert_res, audit_upsert_err
	# Upsert test #2: when it DOES exist
	raw_audit_body2 = {
		"title": audit_name
	  , "description": sentence(5)
	  , "overall_status": gap.Status.not_started
	  , "note": sentence(10)
	}
	audit_upsert_res, audit_upsert_err = gap_client.upsert_audit(raw_body = raw_audit_body2, do_debug = True)
	assert audit_upsert_res, audit_upsert_err
	audit_id = audit_upsert_res.get("id")
	# Cleanup
	delete_res, delete_err = gap_client.delete_audit(id = audit_id)


def test_csv():
	import csv
	with open(soa_csv_fn, "r", encoding='utf-8-sig') as csvfile:
		data = csv.DictReader(csvfile, delimiter=',', quotechar='"')
		for row in data:
			logger.info("--------------------")
			logger.info(row)


def test_get_audit_goal_by_title(gap_client):
	audit_goal, audit_goal_err = gap_client.get_audit_goal_by_title("THIS AUDIT GOAL BETTER NOT EXIST")
	assert not audit_goal
	assert not audit_goal_err
	audit_goal, audit_goal_err = gap_client.get_audit_goal_by_title("My Audit Goal")
	assert audit_goal
	assert not audit_goal_err


def test_enums():
	logger.info(gap.Status)
	logger.info(gap.Status.not_started)
	logger.info(gap.Status.not_started.value)
	logger.info(gap.Status.not_started.name)
	logger.info(gap.Icon)
	logger.info(gap.Icon.warning)
	logger.info(gap.Icon.warning.value)
	logger.info(gap.Icon.warning.name)


def test_map(gap_client):
	with open('SoA.csv', "r", encoding='utf-8-sig') as csvfile:
		data = csv.DictReader(csvfile, delimiter=',', quotechar='"')
		assert data
		logger.info("SOA")
		ht = to_html(data)
		with open("SoA.html", "w") as htfile:
			htfile.write(ht)
		for indata in data:
			logger.info("")
			logger.info("##################### IN: #################################")
			logger.info(pprint.pformat(indata))
			logger.info("-------------------- OUT: ---------------------------------")
			outdata=gap.map_audit_goal(indata)
			logger.info(pprint.pformat(outdata))


# disabled
# ambitious import/sync data from .csv
def _test_import(gap_client):
	data = None
	# Generate random name (that does not exist)
	audit_name = sentence(3)
	# Create the audit under our name
	raw_audit_body = {
		"title": audit_name
	  , "description": sentence(5)
	  , "overall_status": gap.Status.not_started
	  , "note": sentence(10)
	}
	audit, audit_err = gap_client.upsert_audit(raw_audit_body)
	# Check again to make sure that this time it actually exists
	audit, audit_err = gap_client.get_audit_by_title(audit_name)
	
	assert audit, f"Audit by name '{audit_name}' did not exist"
	assert not audit_err, f"Error fetching audit by name '{audit_name}'"
	audit_id = audit.get("id")
	#logger.info(pprint.pformat(audit))
	# keep custom-field slugs
	raw_custom_fields,custom_fields_err = gap_client.get_custom_fields()
	assert raw_custom_fields, custom_fields_err
	assert not custom_fields_err, custom_fields_err
	custom_fields_by_name = dict()
	for cf in raw_custom_fields:
		custom_fields_by_name[cf.get("name")] = cf
	logger.info(f"custom_fields_by_name: {pprint.pformat(custom_fields_by_name)}")
	# Go through csv input line by line where each line is one audit goal
	with open('SoA.csv', "r", encoding='utf-8-sig') as csvfile:
		data = csv.DictReader(csvfile, delimiter=',', quotechar='"')
		assert data
		# First stage: discover missing custom fields and prep audit goals:
		custom_fields_missing = set()
		prepped_audits=list()
		ct = 0
		for row in data:
			logger.info("")
			logger.info("----------------------------------------------------------")
			# logger.info(row)
			# Look for the existence of this audit goal in our current audit
			audit_goal_name = row.get("Title")
			if not audit_goal_name:
				logger.warning(f"Skipping invalid audit goal title '{audit_goal_name}'")
				continue
			audit_goal_data, custom_fields = gap.map_audit_goal(row)
			logger.info(f"row: {pprint.pformat(row)}")
			logger.info(f"audit_goal_data: {pprint.pformat(audit_goal_data)}")
			logger.info(f"custom_fields: {pprint.pformat(custom_fields)}")
			audit_goal_data["parent_id"] = audit_id
			audit_goal_data, err = gap.clean_audit_goal_out(audit_goal_data)
			assert audit_goal_data, err
			assert not err, err
			# Look for missing custom fields:
			prepped_audits.append(audit_goal_data)
			for custom_field_name in custom_fields:
				if not custom_field_name:
					continue
				custom_field = custom_fields_by_name.get(custom_field_name)
				logger.info(f"Found {pprint.pformat(custom_field)} for '{custom_field_name}'")
				if not custom_field:
					custom_fields_missing.add(custom_field_name)
			ct += 1
			if ct > 3:
				# break
				pass
		
		# Second stage: create all missing custom fields
		for custom_field_name in list(custom_fields_missing):
			logger.info(f"CREATING MISSING CF: {custom_field_name}")
			if not clean_audit_goal:
				logger.warning(f" + No name")
				continue
			custom_field = {
				  "name": custom_field_name
				, "type": "text"
			}
			create_custom_field_res, create_custom_field_err = gap_client.create_custom_field("project_audit_goals", custom_field, do_debug=True)
			assert create_custom_field_res, create_custom_field_err
			assert not create_custom_field_res, create_custom_field_err
			custom_fields.append(create_custom_field_res)
		#TODO: Put custom fields by their slugs into body before upserting them
		logger.info("Total list of custom fields: %%%%%%%%%%%%")
		logger.info(pprint.pformat(custom_fields))
		# Third stage: upload audit goals
		logger.info(f"prepped_audits: {len(prepped_audits)}")
		for audit_goal_data in prepped_audits:
			audit_goal_name = audit_goal_data.get("title")
			logger.info("")
			logger.info(f"---------------------------------------------------------- {audit_goal_data}")
			#row = {k.lower(): v for k, v in row.items()}
			#logger.info("UPSERTING "+pprint.pformat(row))
			audit_goal_res, audit_goal_err = gap_client.upsert_audit_goal_by_title(audit_goal_data, do_debug=True)
			assert not audit_goal_err, f"Error upserting audit goal by name '{audit_goal_name}': {audit_goal_err}"


def test_replicate_this(gap_client):
	# Create it
	raw_audit_body = {
		"title": "Original title",
		"description": "Original description",
		"overall_status": "not_started",
		"note": "Original note"
	}
	audit_create_res, audit_create_err = gap_client.create_audit(raw_body = raw_audit_body, do_debug = True)
	assert audit_create_res, audit_create_err
	# Patch
	patch_audit_body = {
		"title": "Edited title",
		"description": "Edited description",
		"overall_status": "in_progress",
		"note": "Edited note"
	}
	audit_id = audit_create_res.get("id")
	audit_patch_res, audit_patch_err = gap_client.patch_audit(id = audit_id, raw_body = patch_audit_body, do_debug = True)
	assert audit_patch_res, audit_patch_err
	# Cleanup
	delete_res, delete_err = gap_client.delete_audit(id = audit_id)
	assert audit_patch_res, audit_patch_err

