from __future__ import annotations
import requests
import time
import base64
import pprint
import re
import logging
import json
from colorama import Fore
from colorama import Style
from pydantic import BaseModel
from typing import Optional, Union, List, Dict


logger = logging.getLogger("MosyleSnipeSync")

class RowResult[T]:
    def __init__(self, total: int = 0, rows: list[T] = []):
        self.total = total
        self.rows = rows

class Timestamp(BaseModel):
    date: str
    formatted: str

class Maintenances:
    pass # TBD

class AvailableActions(BaseModel):
    update: Optional[bool]
    delete: Optional[bool]
    clone: Optional[bool]
    restore: Optional[bool]
    checkout: Optional[bool]
    checkin: Optional[bool]
    audit: Optional[bool]
    bulk_selectable: Optional[AvailableActions] = None

class Department(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    fax: Optional[str]
    image: Optional[str]
    email: Optional[str]
    company: Optional[Company]
    manager: Optional[User]
    location: Optional[Location]
    users_count: str = "0"
    notes: str = ""
    created_at: Optional[Timestamp]
    created_by: Optional[User]
    updated_at: Optional[Timestamp]
    available_actions: AvailableActions

class License(BaseModel):
            id: int
            name: str
            company: Optional[Company]
            manufacturer: Optional[Manufacturer]
            product_key: Optional[str]
            order_number: Optional[str]
            purchase_order: Optional[str]
            purchase_date: Optional[Timestamp]
            termination_date: Optional[Timestamp]
            depreciation: Optional[Depreciation]
            purchase_cost: Optional[float]
            purchase_cost_numeric: Optional[str]
            notes: str = ""
            expiration_date: Optional[Timestamp]
            seats: int = 0
            free_seats_count: int = 0
            remaining: int = 0
            min_amt: int | None = 0
            license_name: Optional[str]
            license_email: Optional[str]
            reassignable: bool = False
            maintained: bool = False
            supplier: Optional[Supplier]
            category: Optional[Category]
            created_by: Optional[User]
            created_at: Optional[Timestamp]
            updated_at: Optional[Timestamp]
            deleted_at: Optional[Timestamp]
            user_can_checkout: bool = False
            available_actions: AvailableActions

class User(BaseModel):
    pass

class Manufacturer(BaseModel):
    id: int
    name: str

class Field(BaseModel):
    id: int
    name: str
    db_column_name: Optional[str]
    format: Optional[str]
    field_values: Optional[str]
    field_values_array: Optional[list[str]]
    type: Optional[str]
    required: bool = False
    display_in_user_view: bool = False
    auto_add_to_fieldsets: bool = False
    show_in_listview: bool = False
    display_checkin: bool = False
    display_checkout: bool = False
    display_audit: bool = False
    created_at: Optional[Timestamp]
    updated_at: Optional[Timestamp]

class Fieldset(BaseModel):
    id: int
    name: str
    description: Optional[str]
    fields: RowResult[Field]
    created_by: Optional[User]
    created_at: Optional[Timestamp]
    updated_at: Optional[Timestamp]

class Depreciation:
    pass

class Category(BaseModel):
            id: int
            name: str
            image: Optional[str]
            category_type: Optional[str]
            has_eula: bool = False
            use_default_eula: bool = False
            eula: Optional[str]
            checkin_email: bool = False
            require_acceptance: bool = False
            item_count: int = 0
            assets_count: int = 0
            accessories_count: int = 0
            consumables_count: int = 0
            components_count: int = 0
            licenses_count: int = 0
            notes: str = ""
            created_by: Optional[User]
            created_at: Optional[Timestamp]
            updated_at: Optional[Timestamp]
            available_actions: AvailableActions

class FieldsetValue(BaseModel):
    field: Field
    default: Optional[str]

class Model(BaseModel):
            id: int 
            name: str 
            manufacturer: Optional[Manufacturer]
            image: Optional[str]
            model_number: Optional[str]
            min_amt: Optional[int]
            remaining: Optional[int]
            depreciation: Optional[Depreciation]
            assets_count: int = 0
            category: Optional[Category]
            fieldset: Optional[Fieldset]
            default_fieldset_values: list[FieldsetValue] = []
            eol: Optional[str]
            requestable: bool = False
            notes: str = ""
            created_by: Optional[User]
            created_at: Optional[Timestamp]
            updated_at: Optional[Timestamp]
            deleted_at: Optional[Timestamp]
            available_actions: AvailableActions

class Status(BaseModel):
            id: int
            name: str
            type: str
            color: Optional[str]
            show_in_nav: bool = False
            default_label: bool = False
            assets_count: int = 0
            notes: str = ""
            created_by: Optional[User]
            created_at: Optional[Timestamp]
            updated_at: Optional[Timestamp]
            available_actions: AvailableActions

class Supplier(BaseModel):
    id: int
    name: str
    image: Optional[str]
    url: Optional[str]
    address: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    zip: Optional[str]
    fax: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    contact: Optional[str]
    assets_count: int = 0
    accessories_count: int = 0
    licenses_count: int = 0
    consumables_count: int = 0
    components_count: int = 0
    notes: str = ""
    created_at: Optional[Timestamp]
    created_by: Optional[User]
    updated_at: Optional[Timestamp]
    available_actions: AvailableActions

class Company(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    image: Optional[str]
    assets_count: int = 0
    licenses_count: int = 0
    accessories_count: int = 0
    consumables_count: int = 0
    components_count: int = 0
    users_count: int = 0
    created_by: Optional[User]
    created_at: Optional[Timestamp]
    updated_at: Optional[Timestamp]
    notes: str = ""
    available_actions: AvailableActions

class Location(BaseModel):
    id: int
    name: str
    image: Optional[str]
    address: Optional[str]
    address2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    accessories_count: int = 0
    assigned_accessories_count: int = 0
    assets_count: int = 0
    assigned_assets_count: int = 0
    rtd_assets_count: int = 0
    users_count: int = 0
    currency: Optional[str]
    ldap_ou: Optional[str]
    notes: str = ""
    created_at: Optional[Timestamp]
    created_by: Optional[User]
    updated_at: Optional[Timestamp]
    parent: Optional[Location]
    manager: Optional[User]
    company: Optional[Company]
    children: list[Location] = []
    available_actions: AvailableActions

class Asset(BaseModel):
    id: int
    name: Optional[str]
    asset_tag: Optional[str]
    serial: Optional[str]
    model: Optional[Model]
    model_number: Optional[str]
    status_label: Optional[Status]
    category: Optional[Category]
    manufacturer: Optional[Manufacturer]
    supplier: Optional[Supplier]
    notes: str = ""
    order_number: Optional[str]
    byod: bool = False
    eol: Optional[str]
    asset_eol_date: Optional[Timestamp]
    company: Optional[str]
    location: Optional[Location]
    rtd_location: Optional[Location]
    image: Optional[str]
    qr: Optional[str]
    alt_barcode: Optional[str]
    assigned_to: Optional[User]
    warranty_months: Optional[int]
    warranty_expires: Optional[Timestamp]
    created_by: Optional[User]
    created_at: Optional[Timestamp]
    updated_at: Optional[Timestamp]
    last_audit_date: Optional[Timestamp]
    next_audit_date: Optional[Timestamp]
    deleted_at: Optional[Timestamp]
    purchase_date: Optional[Timestamp]
    agent: Optional[str]
    last_checkout: Optional[Timestamp]
    last_checkin: Optional[Timestamp]
    expected_checkin: Optional[Timestamp]
    purchase_cost: Optional[int]
    checkin_counter: Optional[int]
    checkout_counter: Optional[int]
    requests_counter: Optional[int]
    user_can_checkout: bool = True
    book_value: Optional[int]
    custom_fields: Optional[dict[str, Field]]
    available_actions: AvailableActions

class Snipe:
    def __init__(
            self, 
            snipe_token:        str,
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
    
    def api_request(
            self,
            method: str,
            endpoint: str,
            params: dict[str, str] | None = None,
            json: dict[str,str] | None = None) -> requests.Response | None:
        self.request_count += 1
        if(self.request_count >= self.rate_limit):
            logger.warning(Fore.YELLOW + "Max requests per minute reached. Sleeping for 60 seconds")
            time.sleep(60) 
            self.request_count = 0
            logger.info(Fore.GREEN + "Request count has been reset", "Continuing", Style.RESET_ALL)

        type = method.upper()
        methods = ["GET", "POST", "PATCH", "DELETE"]
        if(type not in methods):
            logger.error(Fore.RED + "Unknown request type: %s" + Style.RESET_ALL, type)
            return None
        
        return requests.get(f"{self.url}/api/v1{endpoint}", headers=self.headers, params=params, json=json, verify=self.verify_ssl)

    def get_all_hardware(self, limit: int = 50, offset: int = 0) -> list[Asset] | None:
        print('Requesting Snipe Hardware list at url ' + self.url + "/hardware")
        response = self.api_request("GET", "/hardware", params={"limit": str(limit), "offset": str(offset)})
        if response is None:
            logger.error("Failed to fetch hardware: No response from server")
            return None
        if not response.ok:
            logger.error("Error fetching hardware: %s", response.text)
            return None
        json_response = response.json()
        if 'rows' not in json_response:
            logger.error("Unexpected response format: %s", json_response)
            return None
        assets = []
        for row in json_response['rows']:
            asset_model = self.get_model_by_id(row['model']['id'])
            if asset_model is None:
                logger.error("Failed to fetch model for asset ID %s", row['id'])
                continue
            del row['model']
            asset = Asset(
                id=row['id'],
                name=row['name'],
                asset_tag=row['asset_tag'],
                serial=row['serial'],
                status_label=Status(id=row['status_label']['id'], name=row['status_label']['name'], type=row['status_label']['type']),
                category=Category(id=row['category']['id'], name=row['category']['name']),
                manufacturer=Manufacturer(id=row['manufacturer']['id'], name=row['manufacturer']['name']),
                supplier=Supplier(id=row['supplier']['id'], name=row['supplier']['name']) if row.get('supplier') else None,
                notes=row.get('notes', ''),
                order_number=row.get('order_number'),
                byod=row.get('byod', False),
                eol=row.get('eol'),
                asset_eol_date=Timestamp(date=row.get('asset_eol_date', ''), formatted=''),
                company=row.get('company'),
                location=Location(id=row['location']['id'], name=row['location']['name']) if row.get('location') else None,
                rtd_location=Location(id=row['rtd_location']['id'], name=row['rtd_location']['name']) if row.get('rtd_location') else None,
                image=row.get('image'),
                qr=row.get('qr'),
                alt_barcode=row.get('alt_barcode'),
                assigned_to=None,  # This would need to be fetched separately
                warranty_months=int(row.get('warranty_months', 0)),
                warranty_expires=Timestamp(date='', formatted=''),  # This would need to be parsed correctly
                created_by=None,  # This would need to be fetched separately
                created_at=Timestamp(date='', formatted=''),  # This would need to be parsed correctly
                updated_at=Timestamp(date='', formatted=''),  # This would need to be parsed correctly
                last_audit_date=Timestamp(date='', formatted=''),  # This would need to be parsed correctly
                next_audit_date= Timestamp(date='', formatted=''),  # This would need to be parsed correctly
            
        
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