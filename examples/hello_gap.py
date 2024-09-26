#!/bin/env python
import os
import pprint
import gap_client


def get_env(key, fallback = None, do_debug = True):
	global env
	ret = os.environ.get(key) or fallback
	if do_debug:
		print(f"ENV {key} = {ret}")
	return ret


client_parameters = {
	  "base_url": get_env("TEST_GAP_CLIENT_ID")
	, "client_id": get_env("TEST_GAP_CLIENT_ID")
	, "client_secret": get_env("TEST_GAP_CLIENT_SECRET")
	, "client_token": get_env("TEST_GAP_TOKEN")
	, "account_id": get_env("TEST_GAP_ACCOUNT_ID")
	, "do_debug": True
}

print(f"Using credentials: {pprint.pformat(client_parameters)}")

# Create client with our credentials
gap = gap_client.Client(**client_parameters)

# Use client to see that it runs
gap.hello_gap()


