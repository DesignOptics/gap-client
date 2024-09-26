from enum import Enum, EnumMeta
from requests_oauth2client import OAuth2Client, OAuth2ClientCredentialsAuth
import json
import logging
import os
import sys
import pprint
import re
import requests
from .helpers import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


logger = logging.getLogger(__name__)


#######################################################################



class MetaEnum(EnumMeta):
	def __contains__(cls, item):
		try:
			cls(item)
		except ValueError:
			return False
		return True    

class BaseEnum(Enum, metaclass=MetaEnum):
	def __str__(self):
		return str(self.value)


class Status(str, BaseEnum):
	not_started = "not_started"
	in_progress = "in_progress"
	completed = "completed"


class Icon(str, BaseEnum):
	people = "people"
	book = "book"
	bank = "bank"
	warning = "warning"
	hashtag = "hashtag"
	
	
# Ugly hardcoded stuff
default_status_options = '[{"name":"not_started","color":"secondary"},{"name":"in_progress","color":"warning"},{"name":"completed","color":"success"}]'


#######################################################################


class Client:
	session = None
	base_url = None
	client_id = None
	client_secret = None
	account_id = None
	auth_url = None
	api_url = None
	token_url = None
	ticket_url = None
	error = None
	
	def set_status(self, error=None):
		self.error = error

	def is_ok(self):
		return not self.error

	def __init__(self, base_url:str, client_id:str, client_secret:str, account_id:str, client_token:str = None, do_debug = False):
		"""
		Create an instance of the gap-client. Requirest that you provide essentials such as api URL and credentials
		The optional do_Debug parameter allows you to swithc on debug logging
		"""
		self.base_url = base_url
		self.client_id = client_id
		self.client_secret = client_secret
		self.account_id = account_id
		self.auth_url = f"{self.base_url}/auth"
		self.api_url = f"{self.base_url}/api-v1"
		self.token_url = f"{self.auth_url}/token"
		self.ticket_url = f"{self.api_url}/tickets"
		self.error = None
		if not self.base_url:
			self.set_status("No base_url specified")
		if not self.account_id:
			self.set_status("No account_id specified")
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		self.session = requests.Session()
		if client_token:
			if do_debug:
				logger.info(f"Using token '{client_token}'")
			self.session.headers["Accept"] = "application/json"
			self.session.headers["Authorization"] = f"Bearer {client_token}"
		else:
			if do_debug:
				logger.info("Using oauth")
			if not self.client_id:
				self.set_status("No client_id specified")
			if not self.client_secret:
				self.set_status("No client_secret specified")
			self.oauth2client = OAuth2Client( token_endpoint=self.token_url, client_id=self.client_id, client_secret=self.client_secret)
			self.auth = OAuth2ClientCredentialsAuth( self.oauth2client, scope="all", resource=self.base_url)
			self.session.auth = self.auth
		self.change_account(account_id = account_id)

	def hello_gap(self):
		"""
		Simple check to see that client is installed and runs
		"""
		logger.info("Welcome to gap client! It seems to run! 🎉🎉🎉")

	def get_memberships(self):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/account/get-memberships"
			logger.info(f"Using get memberships URL:{url}")
			res = self.session.get(url)
			res.raise_for_status()
			raw_result = res.json()
			result = list()
			for item in raw_result:
				clean, err = clean_membership(item)
				if clean:
					result.append(clean)
				else:
					raise Exception(err)
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return result, err

	def change_account(self, account_id = None):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		self.account_id = account_id or self.account_id
		result = None
		err = None
		try:
			url = f"{self.api_url}/account/change-account/{self.account_id}"
			query_body = {
				"account_id": account_id
			}
			logger.info(f"Using change account url:{url}")
			res = self.session.post(url, params = query_body)
			res.raise_for_status()
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return True, err

	def delete_audit(self, id, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/audits/{id}"
			res = self.session.delete(url)
			res.raise_for_status()
			result = True
		except requests.exceptions.RequestException as e:
			err = str(e)
			if do_debug:
				logger.warning(f"delete_audit: {err}")
		return result, err

	def get_audits(self, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		return generic_get(session=self.session, url=f"{self.api_url}/{self.account_id}/audits", name="audits", sub=None, clean_fun=None, do_debug = do_debug)
	
	def old_get_audits(self, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/audits"
			# GET parameter that also fetches all audit_goals
			relation = "audit_goals"
			if do_debug:
				logger.info(f"Using get audits  url:{url}")
			done = False
			result = list()
			while not done:
				if do_debug:
					logger.info(f" + {url} ({len(result)})")
				res = self.session.get(url)
				res.raise_for_status()
				raw_result = res.json()
				#logger.info(f"raw_result:{pprint.pformat(raw_result)}")
				for item in raw_result.get("data"):
					if item:
						result.append(item)
					else:
						logger.warning("Skipping item")
				next_page_url = raw_result.get("next_page_url")
				if not next_page_url:
					done = True
				else:
					url = next_page_url
			if do_debug:
				logger.info(f"result:{pprint.pformat(result)}")
		except requests.exceptions.RequestException as e: 
			err = f"EXCEPTION: {e}, BODY:{res.text}"
		return result, err


	def create_audit_goal(self, raw_body, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			audit_goal, err = clean_audit_goal_out(raw_body, do_debug=do_debug)
			if not audit_goal:
				raise Exception(f"No audit goal, {err}")
			url = f"{self.api_url}/{self.account_id}/audit-goals"
			if do_debug:
				logger.info(f"Using create audit goal url:{url}")
				logger.info(f"Using create audit goal body:{pprint.pformat(audit_goal)}")
				logger.info(f"Using create audit goal json:{json.dumps(audit_goal)}")
			res = self.session.post(url, json = audit_goal)
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.info(f"create_audit_goal return raw_result={pprint.pformat(raw_result)}")
			result, err = clean_audit_goal_in(raw_result)
			if do_debug:
				logger.info(f"create_audit_goal return result={pprint.pformat(result)}")
		except requests.exceptions.RequestException as e: 
			err = str(e) + "|" + res.text
		return result, err


	def patch_audit_goal(self, id, raw_audit_goal=dict(), do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		# Accepts custom fields
		try:
			url = f"{self.api_url}/{self.account_id}/audit-goals/{id}"
			if do_debug:
				logger.info(f"Using patch audit goal url:{url}")
			if do_debug:
				logger.warning("PATCHING AUDIT GOAL WITH BODY:" + pprint.pformat(raw_audit_goal))
			res = self.session.put(url, json = raw_audit_goal)
			if do_debug:
				logger.warning("PATCHING AUDIT GOAL RES:" + pprint.pformat(res))
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.warning("PATCHING AUDIT GOAL RESPONSE:"+pprint.pformat(raw_result))
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return result, err

	def delete_audit_goal(self, id, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/audit-goals/{id}"
			res = self.session.delete(url)
			res.raise_for_status()
			result = res.json()
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return result, err

	def get_audit_goal(self, id, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/audit-goals/{id}"
			###
			logger.info(f"Using get audit goal url:{url}")
			done = False
			result = list()
			logger.info(f" + {url} ({len(result)})")
			res = self.session.get(url)
			res.raise_for_status()
			raw_result = res.json()
			logger.info(f"raw_result:{pprint.pformat(raw_result)}")
			for item in raw_result.get("data"):
				clean, err = clean_audit_goal_in(item)
				if clean:
					result.append(clean)
				else:
					raise Exception(err)
			logger.info(f"result:{pprint.pformat(result)}")
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return result, err


	def get_audit_by_title(self, title, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		audits, err = self.get_audits(do_debug = do_debug)
		if err:
			return None, err
		for audit in audits:
			if audit.get("title") == title:
				return audit, None
		return None, None


	def get_audit_goals(self, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/audit-goals"
			if do_debug:
				logger.info(f"Using get audit goals url:{url}")
			done = False
			result = list()
			while not done:
				if do_debug:
					logger.info(f" + {url} ({len(result)})")
				res = self.session.get(url)
				res.raise_for_status()
				raw_result = res.json()
				#logger.info(f"raw_result:{pprint.pformat(raw_result)}")
				for item in raw_result.get("data"):
					#clean, err = clean_audit_goal_in(item)
					clean = item
					if clean:
						result.append(clean)
					else:
						raise Exception(err)
				next_page_url = raw_result.get("next_page_url")
				if not next_page_url:
					done = True
				else:
					url = next_page_url
				if do_debug:
					logger.info(f"result:{pprint.pformat(result)}")
		except requests.exceptions.RequestException as e: 
			err = str(e)
		return result, err


	def get_audit_goal_by_title(self, title, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		goals, err = self.get_audit_goals(do_debug = do_debug)
		if err:
			return None, err
		for goal in goals:
			if goal.get("title") == title:
				return clean_audit_goal_in(goal)
		return None, None


	def upsert_audit_goal_by_title(self, raw_body, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		if not raw_body:
			return None, "No body specified"
		title = raw_body.get("title")
		if not title:
			return None, "No title in specified in body"
		audit_goal, err = self.get_audit_goal_by_title(title)
		if not audit_goal:
			if do_debug:
				logger.info("upsert audit goal : no existing, creating")
			if err:
				return None, err
			return self.create_audit_goal(raw_body, do_debug = do_debug)
		fields = [ "title"
				, "description"
				, "parent_id"
				, "status"
				, "guide"
				, "documentation"
				, "note"
				, "icon" ]
		out = dict()
		for field in fields:
			out[field] = audit_goal.get(field, raw_body.get(field))
		logger.info("upsert audit goal : existed:\n{pprint.pformat(audit_goal)}\npatching with:\n{pprint.pformat(out)}\n")
		return self.patch_audit_goal(out)


	def create_audit(self, raw_body, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			audit, err = clean_audit_out(raw_body)
			if not audit:
				raise Exception(f"No audit goal, {err}")
			url = f"{self.api_url}/{self.account_id}/audits"
			logger.info(f"create_audit url:{url}")
			if do_debug:
				logger.warning("create_audit body:"+pprint.pformat(audit))
			res = self.session.post(url, json = audit)
			if do_debug:
				logger.warning("create_audit res:"+pprint.pformat(res))
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.warning("create_audit result:"+pprint.pformat(raw_result))
			result = raw_result
		except requests.exceptions.RequestException as e: 
			result = None
			err = str(e) + res.text
			if do_debug:
				logger.warning("create_audit error:"+pprint.pformat(err))
		return result, err


	def patch_audit(self, id, raw_body = dict(), do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		# Accepts custom fields
		try:
			url = f"{self.api_url}/{self.account_id}/audits/{id}"
			if do_debug:
				logger.info(f"patch_audit url:{url}")
			if do_debug:
				logger.warning(f"patch_audit raw body: {pprint.pformat(raw_body)}")
			audit, clean_err = clean_audit_out(raw_body)
			# audit={"title":"aaa"}
			if do_debug:
				logger.warning(f"patch_audit cleaned body: {pprint.pformat(audit)}")
			if not audit:
				return None, "Could not clean audit: " + clean_err
			
			
			try:
				import http.client as http_client
			except ImportError:
				# Python 2
				import httplib as http_client
			http_client.HTTPConnection.debuglevel = 1
			
			logging.getLogger().setLevel(logging.DEBUG)
			requests_log = logging.getLogger("requests.packages.urllib3")
			requests_log.setLevel(logging.DEBUG)
			requests_log.propagate = True
			
			self.session.headers["_method"] = "patch"
			
			#res = self.session.post(url, json = audit)
			res = self.session.patch(url, json = audit)
			if do_debug:
				logger.warning(f"patch_audit res: {pprint.pformat(res)}")
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.warning(f"patch_audit result: {pprint.pformat(raw_result)}")

			result = raw_result
		except requests.exceptions.RequestException as e: 
			err = str(e)
			if do_debug:
				logger.warning(f"patch_audit err: {err}")
		return result, err


	def upsert_audit(self, raw_body, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		if not raw_body:
			return None, "No body specified"
		title = raw_body.get("title")
		if not title:
			return None, "No title in specified in body"
		audit, err = self.get_audit_by_title(title)
		if not audit:
			if do_debug:
				logger.info("upsert audit: no existing, creating")
			if err:
				return None, err
			return self.create_audit(raw_body, do_debug = do_debug)
		id = audit.get("id")
		if do_debug:
			logger.info(f"upsert_audit patch: {id}")
		return self.patch_audit(id, raw_body, do_debug = do_debug)


	def create_custom_field(self, field_type, raw_field, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		valid_field_types = [
			  "data_recepients"
			, "data_responsible"
			, "event_logs"
			, "it_system"
			, "project_audit_goals"
			, "work_processes"
		]
		try:
			if field_type not in valid_field_types:
				raise Exception(f"Invalid field type")
			field, err = clean_custom_field(raw_field)
			if not field:
				raise Exception(f"No field, {err}")
			query_body = {
				  "account_id": self.account_id
				, "type": field_type
				, "fields" : [ field ]
			}
			url = f"{self.api_url}/{self.account_id}/custom-fields"
			if do_debug:
				logger.info(f"create_custom_field query body:{json.dumps(query_body, indent=3)}")
				logger.info(f"create_custom_field url:{url}")
			res = self.session.post(url, json = query_body)
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.info(f"create_custom_field result: {pprint.pformat(raw_result)}")
			result = list()
			for custom_field in raw_result.get("fields"):
				result.append( clean_custom_field(custom_field))
		except requests.exceptions.RequestException as re: 
			err = str(re) + res.text
			if do_debug:
				logger.warning(f"create_custom_field RequestException: {err}")
		except Exception as e: 
			err = str(e)
			if do_debug:
				logger.warning(f"create_custom_field Exception: {err}")
		return result, err


	# This is really complex because output from server is in a contorted format that needs to be normalized to be useful
	def get_custom_fields(self, do_debug = False):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		session = self.session
		url = f"{self.api_url}/{self.account_id}/custom-fields"
		name = "custom-fields"
		clean_fun = clean_custom_field
		result = None
		err = None
		try:
			if do_debug:
				logger.info(f"Using get '{name}' url:'{url}'")
			done = False
			result = list()
			while not done:
				if do_debug:
					logger.info(f" + {url} ({len(result)})")
				res = session.get(url)
				res.raise_for_status()
				raw_result = res.json()
				if do_debug:
					logger.info(f"raw_result:{pprint.pformat(raw_result)}")
				for raw_item in raw_result.get("data"):
					if raw_item:
						if do_debug:
							logger.info(f"raw_item:{pprint.pformat(raw_item)}")
							for k, v in raw_item.items():
								logger.info(f" + K='{k}', V='{v}'")
						raw_items2 = raw_item.get("fields")
						for raw_item2 in raw_items2:
							if do_debug:
								logger.info(f"raw_item2:{pprint.pformat(raw_item2)}")
							if clean_fun:
								item, clean_err = clean_fun(raw_item2)
								if not item:
									logger.warning(f"Error cleaning {name} item: {clean_err}")
									continue
								if do_debug:
									logger.info(f"cleaned_item:{pprint.pformat(item)}")
							else:
								item = raw_item2
							for k in ["account_id", "type", "created_at", "updated_at"]:
								v = raw_item.get(k)
								if v:
									item[k] = v
							result.append(item)
					else:
						logger.warning("Skipping item")
				next_page_url = raw_result.get("next_page_url")
				if not next_page_url:
					done = True
				else:
					url = next_page_url
			if do_debug:
				logger.info(f"result:{pprint.pformat(result)}")
		except requests.exceptions.RequestException as e: 
			err = f"EXCEPTION: {e}, BODY:{res.text}"
		return result, err
	

	def old_get_custom_fields(self, do_debug = True):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		try:
			url = f"{self.api_url}/{self.account_id}/custom-fields"
			res = self.session.get(url)
			if do_debug:
				logger.info(f"get_custom_fields res: {pprint.pformat(res)}")
			res.raise_for_status()
		except requests.exceptions.RequestException as re: 
			err = str(re) + res.text
		except Exception as e: 
			err = str(e)
		return result, err


	def upsert_custom_fields(self, field_type, raw_fields = list()):
		if self.error:
			logger.error(f"Error: {self.error}")
			return
		result = None
		err = None
		return result, err

