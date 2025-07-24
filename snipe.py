from cgi import print_arguments
import mimetypes
from unittest import result
import requests
import time
import base64
import pprint
import sys
import re
import logging
from colorama import Fore
from colorama import Style

logger = logging.getLogger("MosyleSnipeSync")

class Snipe:
    def __init__(self, snipetoken, url,manufacturer_id,macos_category_id,ios_category_id,tvos_category_id,rate_limit,macos_fieldset_id,ios_fieldset_id,tvos_fieldset_id,apple_image_check, verify_ssl = True):
        self.url = url
        self._snipetoken = snipetoken
        self.manufacturer_id = manufacturer_id
        self.macos_category_id = macos_category_id
        self.ios_category_id = ios_category_id
        self.tvos_category_id = tvos_category_id
        self.rate_limit = rate_limit
        self.request_count = 0
        self.macos_fieldset_id = macos_fieldset_id
        self.ios_fieldset_id = ios_fieldset_id
        self.tvos_fieldset_id = tvos_fieldset_id
        self.apple_image_check = apple_image_check
        self.verify_ssl = verify_ssl
        self.custom_fields = {}

        # Handle expected custom fields.
        # Fields we expect:
        fields_to_create = [
            'bluetooth_mac_address',
            'cpu_model',
            'percent_disk',
            'available_disk',
            'operating_system',
            'operating_system_version',
            'mac_address'
        ]
        fields = self.getCustomFields().json()
        for row in fields['rows']:
            field_name = re.search(r'_snipeit_(.*)_\d+', row['db_column_name'])
            mat = field_name.group(1)
            if mat is not None and mat in fields_to_create:
                self.custom_fields[mat] = row['db_column_name']
                fields_to_create.remove(mat)
        for row in fields_to_create:
            formatted_name = row.replace('mac', 'MAC').replace('_', ' ').capitalize()
            ret = self.createCustomField(formatted_name)
            if not ret.ok:
                logger.error("Error creating field %s: %s", formatted_name, ret.text)
            ret = ret.json()
            if ret['status'] == "error" and ret['messages']['name'][0] != "The name has already been taken.":
                logger.error("Error creating field %s: %s", formatted_name, ret.messages)
            self.custom_fields[row] = ret['payload']['db_column']

    @property
    def headers(self):
        return {
            "authorization": "Bearer " + self._snipetoken,
            "accept": "application/json",
            "content-type": "application/json",
        }    

    #@property
    def listHardware(self, serial):
        print('Requesting Snipe Harware list at url '+ self.url + "/hardware/byserial/")
        return self.snipeItRequest("GET", "/hardware/byserial/" + serial)

    def listAllModels(self):
        print('requesting all apple models')
        return self.snipeItRequest("GET","/models", params = {"limit": "50", "offset": "0", "sort": "created_at", "order": "asc"})

    def searchModel(self, model):
        print('Requesting Snipe Model list')
        result = self.snipeItRequest("GET", "/models", params = {"limit": "50", "offset": "0", "search": model, "sort": "created_at", "order": "asc"})
        print(result.json())
        jsonResult = result.json()
        #Did the search return a result?
        if jsonResult['total'] == 0:
            print("model was not found")
        else:
            print("the model was found")

            #does the model have a picture?
            if jsonResult['rows'][0]['image'] is None:
                print("the model does not have a picture. Let, set one")
                #No, it does not. Let's update it.
                imageResponse = self.getImageForModel(model);
                print("imageResponse", imageResponse)
                if(imageResponse == False):
                    print("loading the image failed..")
                else:
                    payload = {
                        "image": imageResponse
                    }
                    self.updateModel(str(jsonResult['rows'][0]['id']), payload)


            else:
                print('image already set.');
            
        #print(result)
        return result
    
    def createModel(self, model):

        payload = {
			"name": model,
            "category_id": self.macos_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.macos_fieldset_id
        }

        imageResponse = self.getImageForModel(model);
        if(imageResponse):
            payload["image"] = imageResponse




        print('Creating Snipe Model with payload:', payload)
        results = self.snipeItRequest("POST", "/models", json = payload)
        #print('the server returned ', results);
        return results
    
    def createCustomField(self, name):
        data = {"name": name, "element": "text"}
        return self.snipeItRequest("POST", "/fields", json=data)
    
    def getCustomFields(self):
        return self.snipeItRequest("GET", "/fields")

    def createAsset(self, model, payload, asset_tag):
        print('Creating Snipe Hardware')
        print(payload);
        payload['status_id'] = 3
        payload['model_id'] = model
        payload['asset_tag'] = asset_tag
        pprint.pprint(payload)
        
        asset = self.snipeItRequest("POST", "/hardware", json = payload).json()
        print("DEBUG ASSET =========")
        pprint.pprint(asset)
        payload = {
            "serial": payload['serial']
        }
        return self.snipeItRequest("PATCH", "/hardware/" + str(asset['payload']['id']), json = payload)
    



    def assignAsset(self, user, asset_id):
        print('Assigning asset '+str(asset_id)+' to user '+user)
        
        payload = {
            "search": user,
            "limit": 2
        }
        response = self.snipeItRequest("GET", "/users", params = payload).json()

        if response['total'] == 0:
            return

        payload = {
            "assigned_user": response['rows'][0]['id'],
            "checkout_to_type": "user"
        }
        return self.snipeItRequest("POST", "/hardware/" + str(asset_id) + "/checkout", json = payload)

    def unasigneAsset(self, asset_id):
        print('Unassigning asset '+str(asset_id))
        return self.snipeItRequest("POST", "/hardware/" + str(asset_id) + "/checkin")

    def updateAsset(self, asset_id, payload):
        print('Updating asset '+str(asset_id))
        #print(payload)
        return self.snipeItRequest("PATCH", "/hardware/" + str(asset_id), json = payload)

    def createMobileModel(self, model):
        print('creating new mobile Model')
        imageResponse = self.getImageForModel(model);
        if(imageResponse == False):
            imageResponse = None
        payload = {
			"name": model,
            "category_id": self.ios_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.ios_fieldset_id,
            "image": imageResponse
        }
        return self.snipeItRequest("POST", "/models", json = payload)
    def createAppleTvModel(self, model):
        print('creating new Apple Tv Model')
        imageResponse = self.getImageForModel(model);
        if(imageResponse == False):
            imageResponse = None
        payload = {
			"name": model,
            "category_id": self.tvos_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.tvos_fieldset_id,
            "image": imageResponse
        }
        return self.snipeItRequest("POST", "/models", json = payload)

    def updateModel(self, model_id, payload):
        print("updating model "+model_id+" with payload", payload)
        return self.snipeItRequest("PATCH", "/models/"+model_id, json = payload)

    def buildPayloadFromMosyle(self, payload):
        finalPayload = {
            #"asset_tag": asset,
            "name": payload['device_name'],
            "serial": payload['serial_number'],
            self.custom_fields['bluetooth_mac_address']: payload['bluetooth_mac_address']
        }
        
        #lets get the proper os name
        if(payload['os'] == "mac"):
            os = "MacOS"
            #cpu stuff is only supplied by MacOS
            finalPayload[self.custom_fields['cpu_model']]: payload['cpu_model']

            finalPayload[self.custom_fields['percent_disk']]: payload['percent_disk'] + " GB"
            finalPayload[self.custom_fields['available_disk']]: payload['available_disk'] + " GB"
        elif(payload['os'] == "ios"):
            os = "iOS"
            finalPayload[self.custom_fields['percent_disk']]: payload['percent_disk'] + " GB"
            finalPayload[self.custom_fields['available_disk']]: payload['available_disk'] + " GB"
        elif(payload['os'] == "tvos"):
            os = "tvos"
        else:
            os = "Not Known"
        
                
        finalPayload[self.custom_fields['operating_system']] = os
        
        #set os version
        finalPayload[self.custom_fields['operating_system_version']] = payload['osversion']
        
        #macaddress stuff
        wifiMac = payload['wifi_mac_address']
        eithernetMac = payload['ethernet_mac_address']
        
        #default to eithernet mac, if not, fall back to wifi mac. If neither, leave blank
        if(wifiMac != None and eithernetMac == None):
            finalPayload[self.custom_fields['mac_address']] = wifiMac
        elif(eithernetMac != None):
            finalPayload[self.custom_fields['mac_address']] = eithernetMac
        
        return finalPayload

    def snipeItRequest(self, type, url, params = None, json = None):
        self.request_count += 1
        if(self.request_count >= self.rate_limit):
            print(Fore.YELLOW + "Max requests per minute reached. Sleeping for 60 seconds")
            time.sleep(60) 
            self.request_count = 0
            print(Fore.GREEN + "Request count has been reset", "Continuing", Style.RESET_ALL)


        if(type == "GET"):
            print('Sending GET request to snipeit', url)
            return requests.get(self.url + url, headers = self.headers, params = params, verify=self.verify_ssl)
        elif(type == "POST"):
            print('Sending POST request to snipeit', url)
            return requests.post(self.url + url, headers = self.headers, json = json, verify=self.verify_ssl)
        elif(type == "PATCH"):
            print('Sending PATCH request to snipeit', url)
            return requests.patch(self.url + url, headers = self.headers, json = json, verify=self.verify_ssl)
        elif(type == "DELETE"):
            print('Sending DELETE request to snipeit', url)
            return requests.delete(self.url + url, headers = self.headers, verify=self.verify_ssl)
        else:
            print(Fore.RED+'Unknown request type'+Style.RESET_ALL)
            return None

    def getImageForModel(self, modelNumber):
        if self.apple_image_check == True:

            url = "https://img.appledb.dev/device@main/" + modelNumber + "/Starlight.png"
            print("Get image from URL", url)
            try:
                response = requests.get(url)
                response.raise_for_status()
                base64encoded = base64.b64encode(response.content).decode("utf8")
                fullImageSring = "data:image/png;name=0.png;base64,"+ base64encoded;
                return fullImageSring;
            
                
            except requests.exceptions.HTTPError as err:
                print(Fore.RED + "Error getting image from apple db", err, Style.RESET_ALL)
                return False
        else:
            print("Image checking is disabled.")
            return False
        

#if __name__ == "__main__":
    #token_snipe = Snipe("Bearer = ".self.token)
    #test2 = token_snipe.list
    #print(test2.text)