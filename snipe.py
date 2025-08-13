import requests
import time
import base64
import pprint
import re
import logging
from colorama import Fore
from colorama import Style

logger = logging.getLogger("MosyleSnipeSync")

class User:
    pass

class Manufacturer:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Model:
    def __init__(
            self, 
            id: int, 
            name: str, 
            manufacturer: Manufacturer | None = None,
            image: str | None = None,
        ):
        self.id = id
        self.name = name
        self.model_number = model_number
        self.category_id = category
    )

class Asset:
    def __init__(
            self,
            id: int,
            serial: str,
            model: str,
            asset_tag: str,
            payload: dict[str,str]
        ):
        self.serial = serial
        self.model = model
        self.asset_tag = asset_tag
        self.payload = payload

    def __repr__(self):
        return f"Asset(serial={self.serial}, model={self.model}, asset_tag={self.asset_tag}, payload={self.payload})"

class Snipe:
    def __init__(
            self, 
            snipe_token:         str,
            url:                str,
            manufacturer_id:    int,
            macos_category_id:  int,
            ios_category_id:    int,
            tvos_category_id:   int,
            rate_limit:         int,
            macos_fieldset_id:  int,
            ios_fieldset_id:    int,
            tvos_fieldset_id:   int,
            apple_image_check:  bool,
            verify_ssl:         bool = True
        ):
        self.url = url
        self._snipe_token = snipe_token
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
        self.custom_fields: dict[str, str] = {}

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
        fields = self.get_custom_fields().json()
        for row in fields['rows']:
            field_name = re.search(r'_snipeit_(.*)_\d+', row['db_column_name'])
            mat = field_name.group(1) if field_name else None
            if mat is not None and mat in fields_to_create:
                self.custom_fields[mat] = row['db_column_name']
                fields_to_create.remove(mat)
        for row in fields_to_create:
            formatted_name = row.replace('mac', 'MAC').replace('_', ' ').capitalize()
            ret = self.create_custom_field(formatted_name)
            if not ret.ok:
                logger.error("Error creating field %s: %s", formatted_name, ret.text)
            ret = ret.json()
            if ret['status'] == "error" and ret['messages']['name'][0] != "The name has already been taken.":
                logger.error("Error creating field %s: %s", formatted_name, ret.messages)
            self.custom_fields[row] = ret['payload']['db_column']

    @property
    def headers(self):
        return {
            "authorization": "Bearer " + self._snipe_token,
            "accept": "application/json",
            "content-type": "application/json",
        }

    #@property
    def list_hardware(self, serial: str) -> requests.Response:
        print('Requesting Snipe Harware list at url '+ self.url + "/hardware/byserial/")
        return self.snipe_it_request("GET", "/hardware/byserial/" + serial)

    def list_all_models(self) -> requests.Response:
        print('requesting all apple models')
        return self.snipe_it_request("GET","/models", params = {"limit": "50", "offset": "0", "sort": "created_at", "order": "asc"})

    def search_model(self, model: str) -> requests.Response:
        print('Requesting Snipe Model list')
        result = self.snipe_it_request("GET", "/models", params = {"limit": "50", "offset": "0", "search": model, "sort": "created_at", "order": "asc"})
        logger.debug(result.json())
        json_result = result.json()
        #Did the search return a result?
        if json_result['total'] == 0:
            print("model was not found")
        else:
            print("the model was found")

            #does the model have a picture?
            if json_result['rows'][0]['image'] is None:
                print("the model does not have a picture. Let, set one")
                #No, it does not. Let's update it.
                image_response = self.get_image_for_model(model);
                print("image_response", image_response)
                if(image_response == False):
                    print("loading the image failed..")
                else:
                    payload = {
                        "image": image_response
                    }
                    self.updateModel(str(json_result['rows'][0]['id']), payload)


            else:
                print('image already set.');
            
        #print(result)
        return result
    
    def create_model(self, model: str) -> requests.Response:

        payload = {
			"name": model,
            "category_id": self.macos_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.macos_fieldset_id
        }

        image_response = self.get_image_for_model(model)
        if(image_response):
            payload["image"] = image_response




        print('Creating Snipe Model with payload:', payload)
        results = self.snipe_it_request("POST", "/models", json = payload)
        #print('the server returned ', results);
        return results
    
    def create_custom_field(self, name: str) -> requests.Response:
        data = {"name": name, "element": "text"}
        return self.snipe_it_request("POST", "/fields", json=data)
    
    def get_custom_fields(self) -> requests.Response:
        return self.snipe_it_request("GET", "/fields")

    def create_asset(self, model: str, payload: dict[str,str], asset_tag: str):
        print('Creating Snipe Hardware')
        print(payload);
        payload['status_id'] = "3"  # Assuming 3 is the default status ID for new assets
        payload['model_id'] = model
        payload['asset_tag'] = asset_tag
        pprint.pprint(payload)
        
        asset = self.snipe_it_request("POST", "/hardware", json = payload).json()
        print("DEBUG ASSET =========")
        pprint.pprint(asset)
        payload = {
            "serial": payload['serial']
        }
        return self.snipe_it_request("PATCH", "/hardware/" + str(asset['payload']['id']), json = payload)
    



    def assign_asset(self, user: str, asset_id: str):
        logger.info('Assigning asset %s to user %s', asset_id, user)
        
        payload = {
            "search": user,
            "limit": "2"
        }
        response = self.snipe_it_request("GET", "/users", params = payload).json()

        if response['total'] == 0:
            return
        
        if response['total'] > 0 and 'id' in response['rows'][0]:
            payload['assigned_user'] = response['rows'][0]['id']

        payload = {
            "checkout_to_type": "user"
        }
        return self.snipe_it_request("POST", "/hardware/" + str(asset_id) + "/checkout", json = payload)

    def unassign_asset(self, asset_id: str):
        logger.info('Unassigning asset %s', asset_id)
        return self.snipe_it_request("POST", "/hardware/" + str(asset_id) + "/checkin")

    def update_asset(self, asset_id: str, payload: dict[str,str]) -> requests.Response:
        print('Updating asset '+str(asset_id))
        #print(payload)
        return self.snipe_it_request("PATCH", "/hardware/" + str(asset_id), json = payload)

    def create_mobile_model(self, model):
        print('creating new mobile Model')
        image_response = self.get_image_for_model(model);
        if(image_response == False):
            image_response = None
        payload = {
			"name": model,
            "category_id": self.ios_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.ios_fieldset_id,
            "image": image_response
        }
        return self.snipe_it_request("POST", "/models", json = payload)

    def create_apple_tv_model(self, model):
        print('creating new Apple Tv Model')
        image_response = self.get_image_for_model(model);
        if(image_response == False):
            image_response = None
        payload = {
			"name": model,
            "category_id": self.tvos_category_id,
            "manufacturer_id": self.manufacturer_id,
            "model_number": model,
            "fieldset_id": self.tvos_fieldset_id,
            "image": image_response
        }
        return self.snipe_it_request("POST", "/models", json = payload)

    def update_model(self, model_id, payload):
        print("updating model "+model_id+" with payload", payload)
        return self.snipe_it_request("PATCH", "/models/"+model_id, json = payload)

    def build_payload_from_mosyle(self, payload):
        final_payload: dict[str,str] = {}
        final_payload["name"] = payload['device_name']
        final_payload["serial"] = payload['serial_number']
        if 'bluetooth_mac_address' in payload:
            final_payload[self.custom_fields['bluetooth_mac_address']] = payload['bluetooth_mac_address']
        
        #lets get the proper os name
        if(payload['os'] == "mac"):
            os = "MacOS"
            #cpu stuff is only supplied by MacOS
            final_payload[self.custom_fields['cpu_model']] = payload['cpu_model'] if 'cpu_model' in payload else None

            final_payload[self.custom_fields['percent_disk']] = payload['percent_disk'] + " GB" if 'percent_disk' in payload else None
            final_payload[self.custom_fields['available_disk']] = payload['available_disk'] + " GB" if 'available_disk' in payload else None
        elif(payload['os'] == "ios"):
            os = "iOS"
            final_payload[self.custom_fields['percent_disk']]: payload['percent_disk'] + " GB"
            final_payload[self.custom_fields['available_disk']]: payload['available_disk'] + " GB"
        elif(payload['os'] == "tvos"):
            os = "tvos"
        else:
            os = "Not Known"
        
                
        final_payload[self.custom_fields['operating_system']] = os
        
        #set os version
        final_payload[self.custom_fields['operating_system_version']] = payload['osversion']
        
        #macaddress stuff
        wifi_mac = str(payload['wifi_mac_address']) if 'wifi_mac_address' in payload else None
        ethernet_mac = str(payload['ethernet_mac_address']) if 'ethernet_mac_address' in payload else None
        
        #default to eithernet mac, if not, fall back to wifi mac. If neither, leave blank
        if(wifi_mac != None and ethernet_mac == None):
            final_payload[self.custom_fields['mac_address']] = wifi_mac
        elif(ethernet_mac != None):
            final_payload[self.custom_fields['mac_address']] = ethernet_mac
        
        return final_payload

    def snipe_it_request(self, type: str, url: str, params: dict[str, str] | None = None, json: dict[str,str] | None = None) -> requests.Response | None:
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

    def get_image_for_model(self, model_number: str) -> str:
        if self.apple_image_check:

            url = "https://img.appledb.dev/device@main/" + model_number + "/Starlight.png"
            print("Get image from URL", url)
            try:
                response = requests.get(url)
                response.raise_for_status()
                base64encoded = base64.b64encode(response.content).decode("utf8")
                fullImageSring = "data:image/png;name=0.png;base64,"+ base64encoded;
                return fullImageSring;
            
                
            except requests.exceptions.HTTPError as err:
                print(Fore.RED + "Error getting image from apple db", err, Style.RESET_ALL)
                return ""
        else:
            print("Image checking is disabled.")
            return ""
        

#if __name__ == "__main__":
    #token_snipe = Snipe("Bearer = ".self.token)
    #test2 = token_snipe.list
    #print(test2.text)