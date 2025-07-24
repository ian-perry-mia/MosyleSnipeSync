import base64
import requests
import logging
import pprint
import sys

logger = logging.getLogger("MosyleSnipeSync")

class Mosyle:
	
	# Create Mosyle instance
	def __init__(self, key, url = "https://businessapi.mosyle.com/v1", user = "", password = ""):
		# Attribute the variable to the instance
		self.url = url
		self.request = requests.Session()
		self.request.headers["accessToken"] = key
		self.request.headers["Content-Type"] = "application/json"

		# Removed: Basic auth is deprecated.
		# #base64 encode username and password for basic auth
		# userpass = user + ':' + password
		# encoded_u = base64.b64encode(userpass.encode()).decode()
		# self.request.headers["Authorization"] = "Basic %s" % encoded_u

		auth_data = {"email": user, "password": password}
		resp = self.request.post(self.url + "/login", json=auth_data)
		if resp.status_code == 200:
			self.request.headers["Authorization"] = resp.headers['Authorization']
		else:
			logger.error("Failed to login: " + resp.text)


	# Create variables requests
	def list(self, os):
		print("Listing devices for OS:", os)
		params = {
			"operation": "list",
			"options": {
				"os": os
			}
		}
		# Concatanate url and send the request
		return self.request.post(self.url + "/devices", json = params )

	def listTimestamp(self, start, end, os):
		params = {
			"operation": "list",
			"options": {
				"os": os,
				"enrolldate_start": start,
				"enrolldate_end": end	
			}
		}
		return self.request.post(self.url + "/devices", json = params )

	def listmobile(self):
		params = {
			"operation": "list",
			"options": {
				"os": "ios"
			}
		}
		return self.request.post(self.url + "/devices", json = params )

	def listuser(self, iduser):
		params = {
			"operation": "list_users",
			"options": { "identifiers": [iduser]
				}
		}
		return self.request.post(self.url + "/users", json = params )
    
	def setAssetTag(self, serialnumber, tag):
		params = {
			"operation": "update_device",
			"serialnumber": serialnumber,
			"asset_tag": tag
		}
		return self.request.post(self.url + "/devices", json = params )