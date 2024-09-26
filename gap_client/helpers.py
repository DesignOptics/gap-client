import random
import logging
import bs4

logger = logging.getLogger(__name__)




# Wrapper for HTML parser "beautiful soup" to alert if parsing engine is missing
def parse_soup(html, bs_parser = 'html5lib'):
	try:
		soup = bs4.BeautifulSoup(html, bs_parser)
		return soup, None
	except bs4.FeatureNotFound as nf:
		err = f"You need to install library to supply BeautifulSoup4 parser for '{bs_parser}'"
		logger.error(err)
		return None, err


# Check
def has_visible_content(html):
	if not html:
		return False
	soup, soup_err = parse_soup(html)
	if soup:
		# Remove script and style elements
		for script_or_style in soup(["script", "style"]):
			script_or_style.extract()
		# Get text and remove any whitespace characters
		text = soup.get_text()
		text = re.sub(r'\s+', ' ', text).strip()
		# Return True if there is visible text
		return bool(text)
	else:
		return False

def extract_links(data):
	if not data:
		return dict()
	out = dict()
	soup, soup_err = parse_soup(data)
	if soup:
		links = soup.find_all('a')
		for link in links:
			h = link.get('href')
			t = link.text
			if h and t:
				out[t] = h
	return out

def clean_mapped(indata, do_debug = False):
	out = dict()
	fmt = '"\''
	for k,v in indata.items():
		if not k:
			continue
		ks = k and k.strip().strip(fmt)
		if "" == ks:
			logger.info(f"Skipping empty key")
		vs = v and v.strip().strip(fmt)
		if do_debug:
			logger.info(f"Stripping '{k}:{v}' => '{ks}:{vs}'")
		out[ks] = vs
	return out
	
def map_audit_goal(indata, do_debug = False):
	map = {
		  "Comments": "description"
		, "Title": "title"
		, "Clause": "clause"
		, "Explanation": "guide"
		, "Implemented": {
			  "_name": "status"
			, "_default": str(Status.not_started)
			, "Completely": str(Status.completed)
			, "Partially": str(Status.in_progress)
			, "": str(Status.not_started)
		}
		, "Control Objectives": "documentation"
		#, "Control Description": "control_description"
		#, "Control Owner": "control_owner"
		#, "Applicable": "applicable"
	}
	# What can be directly mapped?
	outdata = dict()
	custom_fields = dict(indata)
	not_found = "sdgfsdfsdfsdfdfgcfgjhfghkhjsdlfkgjsldkfjglksdjfglksdjfghlksdjgfhklsdgjmhlksdjfh"
	indata = clean_mapped(indata, do_debug=True)
	
	
	for inkey, out in indata.items():
		inval = indata.get(inkey, not_found)
		out = map.get(inkey, not_found)
		if out != not_found:
			if isinstance(out, str):
				if inval != not_found:
					if do_debug:
						logger.info(f"Mapped string match for key: '{inkey}' => '{out}'")
						
						
						
					links = extract_links(inval)
					if links:
						for name, link in links.items():
							inval = f'<a href="{link}">{name}</a>'
					else:
						if not has_visible_content(inval):
							inval=""

					outdata[out] = inval
					del custom_fields[inkey]
					continue
				else:
					if do_debug:
						logger.info(f"Matched string key failed: '{inkey}' => '{out}'")
					continue
			elif isinstance(out, dict):
				outkey = out.get("_name", not_found)
				outdef = out.get("_default", not_found)
				outval = out.get(inval, not_found)
				if outval != not_found:
					#logger.info(f"Mapped dict match for key: '{inkey}' => '{outkey}' outval='{outval}'")
					if do_debug:
						logger.info(f"Mapped dict match: inval='{inval}' inkey='{inkey}' outval='{outval}' outkey='{outkey}'")
					outdata[outkey] = outdef == not_found and "" or outdef
					del custom_fields[inkey]
					continue
				else:
					if do_debug:
						logger.info(f"Matched dict key failed: inval='{inval}' inkey='{inkey}' outval='{outval}' outkey='{outkey}'")
					outdata[inkey] = ""
					del custom_fields[inkey]
					continue
			else:
				if do_debug:
					logger.info(f"Map is not string {pprint.pformat(outkey)} ({inkey})")
				continue
		if do_debug:
			logger.info(f"No match for {inkey}")
	logger.info(f"map_audit_goal outdata: {pprint.pformat(outdata)}")
	return outdata, custom_fields.keys()


def clean_membership(data):
	return data


def clean_audit_out(raw_audit, do_debug = False):
	return raw_audit, None
	if not raw_audit:
		return None, "No raw_audit"
	if do_debug:
		logger.info("RAW:"+pprint.pformat(raw_audit))
	title = raw_audit.get("title")
	if not title:
		return None, "No title for raw_audit"
	overall_status = raw_audit.get("overall_status", Status.not_started)
	if not overall_status or (not overall_status.startswith("{") and overall_status not in Status):
		return None, f"Invalid status '{overall_status}' for raw_audit"
	audit = {
			"title": title
		  , "description": raw_audit.get("description")
		  , "status_options": default_status_options
		  , "default_status_options": default_status_options
		  , "overall_status": str(overall_status)
		  , "note": raw_audit.get("note")
		}
	if do_debug:
		logger.info(f"Clean audit goal: {pprint.pformat(audit)}")
	return audit, None



def clean_audit_in(raw_audit, do_debug = False):
	return raw_audit, None
	if not raw_audit:
		return None, "No raw_audit"
	if do_debug:
		logger.info("RAW:"+pprint.pformat(raw_audit))
	title = raw_audit.get("title")
	if not title:
		return None, "No title for raw_audit"
	overall_status = raw_audit.get("overall_status", Status.not_started)
	if not overall_status or (not overall_status.startswith("{") and overall_status not in Status):
		return None, f"Invalid status '{overall_status}' for raw_audit"
	audit = {
			"title": title
		  , "description": raw_audit.get("description")
		  , "default_status_options": default_status_options
		  , "overall_status": str(overall_status)
		  , "note": raw_audit.get("note")
		}
	if do_debug:
		logger.info(f"Clean audit goal: {pprint.pformat(audit)}")
	return audit, None


def clean_audit_goal_out(raw_audit_goal, do_debug = False):
	if not raw_audit_goal:
		return None, "No raw_audit_goal"
	if do_debug:
		logger.info(f"clean_audit_goal_out raw: {pprint.pformat(raw_audit_goal)}")
	title = raw_audit_goal.get("title")
	if not title:
		return None, "No title for raw_audit_goal"
	status = raw_audit_goal.get("status", Status.not_started)
	if not status or (not status.startswith("{") and status not in Status):
		return None, f"Invalid status '{status}' ('{Status.not_started}') for raw_audit_goal"
	#icon = raw_audit_goal.get("icon")
	#if icon and (icon not in Icon and not isinstance(icon, dict)):
	#	return None, f"Invalid icon '{icon}' for raw_audit_goal"
	# From Jacob 2024-01-23
	audit_goal_x = {
		"id": 0,
		"title": "Title",
		"parent_id": 0,
		"status": "not_started",
		"description": null,
		"settings": {
			"titleBold": false,
			"included_in_dashboard": true,
			"descriptionEnabled": true,
			"guideEnabled": true,
			"documentationEnabled": true,
			"general_report": false,
			"attachments": true,
			"elementsEnabled": true,
			"statusEnabled": true,
			"tasksEnabled": true,
			"customFieldsEnabled": true
		},
		"guide": null,
		"documentation": null,
		"custom_field": [],
		"created_at": "2024-01-24T11:07:12.000000Z",
		"updated_at": "2024-01-24T11:07:21.000000Z",
		"work_processes": [],
		"it_systems": [],
		"data_handlers": [],
		"security_measures": [],
		"risks": [],
		"risk_categories": [],
		"inspections": [],
		"files": [],
		"audits": [],
		"local_audit_goals": [],
		"project_audit_tasks": [],
		"risk_assessments": [],
		"attachments": []
	}
	 
	audit_goal = {
#		  "id": 0
		  "title": title
		, "description": raw_audit_goal.get("description") # "<p>The best audit goal in years</p>"
		, "parent_id": raw_audit_goal.get("parent_id", "")
#		, "status": str(status)
		, "guide": raw_audit_goal.get("guide", "")
		, "documentation": raw_audit_goal.get("documentation", "")
		, "note": raw_audit_goal.get("note", "")
		, "settings": {
			  "titleBold": false
			, "included_in_dashboard": true
			, "descriptionEnabled": true
			, "guideEnabled": true
			, "documentationEnabled": true
			, "general_report": false
			, "attachments": true
			, "elementsEnabled": true
			, "statusEnabled": true
			, "tasksEnabled": true
			, "customFieldsEnabled": true
		},
		# NOTE: Goal should not have icon
#		, "icon": raw_audit_goal.get("icon", '{"value": null , "color": null }')
#		, "custom_field": list()
#		, "archived": False
	}
	if do_debug:
		logger.info(f"Clean audit goal: {pprint.pformat(audit_goal)}")
	return audit_goal, None



def clean_audit_goal_in(raw_audit_goal, do_debug = False):
	if not raw_audit_goal:
		return None, "No raw_audit_goal"
	if do_debug:
		logger.info(f"clean_audit_goal_in raw: {pprint.pformat(raw_audit_goal)}")
	title = raw_audit_goal.get("title")
	if not title:
		return None, "No title for raw_audit_goal"
	status = raw_audit_goal.get("status", None)
	#logger.error(f"STATUS: {status}")
	status = status or Status.not_started
	if not status or (not status.startswith("{") and status not in Status):
		return None, f"Invalid status '{status}' ('{Status.not_started}') for raw_audit_goal"
	#icon = raw_audit_goal.get("icon")
	#if icon and (icon not in Icon and not isinstance(icon, dict)):
	#	return None, f"Invalid icon '{icon}' for raw_audit_goal"
	audit_goal = {
#		  "id": 0
		  "title": title
		, "description": raw_audit_goal.get("description") # "<p>The best audit goal in years</p>"
		, "parent_id": raw_audit_goal.get("parent_id", "")
#		, "status": str(status)
		, "guide": raw_audit_goal.get("guide", "")
		, "documentation": raw_audit_goal.get("documentation", "")
		, "note": raw_audit_goal.get("note", "")
		# NOTE: Goal should not have icon
		#, "icon": '{"value": null , "color": null }'
#		, "custom_field": list()
#		, "archived": False
	}
	if do_debug:
		logger.info(f"Clean audit goal: {pprint.pformat(audit_goal)}")
	return audit_goal, None


def clean_custom_field(raw_field, do_debug = False):
	if not raw_field:
		return None, "No raw_field"
	name = raw_field.get("name")
	if not name:
		logger.info(f"clean_custom_field: missing name for '{pprint.pformat(raw_field)}'")
		return None, "Skipping custom field missing required name"
	field_type = raw_field.get("type", "text")
	valid_field_types = [
		  "multiSelect"
		, "richArea"
		, "select"
		, "text"
		, "textArea"
	]
	if field_type not in valid_field_types:
		return None, f"Invalid field type {field_type}"
	
	field = {
		  "name": name
		, "type": field_type
		, "slug": raw_field.get("slug")
		, "in_table": raw_field.get("in_table", True)
		, "options": raw_field.get("options", list())
		, "toggleDefault": raw_field.get("toggleDefault", False)
		, "selectDefault": raw_field.get("selectDefault", None)
		, "multiSelectDefault": raw_field.get("multiSelectDefault", list())
	}
	if do_debug:
		logger.info(f"Clean custom field: {pprint.pformat(field)}")
	return field, None

"""
def clean_custom_fields(raw_fields, do_debug = False):
	valid_field_types = [
		  "data_recepients"
		, "data_responsible"
		, "event_logs"
		, "it_system"
		, "project_audit_goals"
		, "work_processes"
	]
	if field_type not in valid_field_types:
		return None, f"Invalid field type {field_type}"
	fields = list()
	for raw_field in raw_fields:
		field = clean_custom_field(raw_field, do_debug = do_debug)
		if not field:
			continue
		fields.append(field)
	return fields, None
"""

###########################################################################################
	
def generic_get(session, url, name, sub=None, clean_fun=None, do_debug = False):
	result = None
	err = None
	try:
		if do_debug:
			logger.info(f"Using get '{name}' url:'{url}'")
		done = False
		result = list()
		while not done:
			if do_debug and False:
				logger.info(f" + {url} ({len(result)})")
			res = session.get(url)
			res.raise_for_status()
			raw_result = res.json()
			if do_debug:
				logger.info(f"raw_result:{pprint.pformat(raw_result)}")
			for raw_item in raw_result.get("data"):
				if raw_item:
					if sub:
						raw_items2 =raw_item.get(sub)
						for raw_item2 in raw_items2:
							if clean_fun:
								item = clean_fun(raw_item2, do_debug = do_debug)
								if do_debug:
									logger.info(f"cleaned_item:{pprint.pformat(item)}")
							else:
								item = raw_item
							result.append(item)
					else:
						if clean_fun:
							item = clean_fun(raw_item)
							if do_debug:
								logger.info(f"cleaned_item:{pprint.pformat(item)}")
						else:
							item = raw_item
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

