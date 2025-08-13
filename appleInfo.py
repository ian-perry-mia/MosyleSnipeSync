#this file can be run to update your Snipe-IT models without interacting with Mosyle.

import base64
from tracemalloc import stop
import requests
import json
import datetime
import configparser
import colorama
from sys import exit

from mosyle import Mosyle
from snipe import Snipe
from colorama import Fore
from colorama import Style
from operator import mod

model_number = "iPad11,2"

# Converts datetim/e to timestamp for Mosyle
ts = datetime.datetime.now().timestamp() - 200

# Set some Variables from the settings.conf:
config = configparser.ConfigParser()
config.read('settings.ini')

# This is the address, cname, or FQDN for your snipe-it instance.
apple_manufacturer_id = int(config['snipe-it']['manufacturer_id'])
macos_category_id = int(config['snipe-it']['macos_category_id'])
ios_category_id = int(config['snipe-it']['ios_category_id'])
tvos_category_id = int(config['snipe-it']['tvos_category_id'])
macos_fieldset_id = int(config['snipe-it']['macos_fieldset_id'])
ios_fieldset_id = int(config['snipe-it']['ios_fieldset_id'])
tvos_fieldset_id = int(config['snipe-it']['tvos_fieldset_id'])
deviceTypes = config['mosyle']['deviceTypes'].split(',')

snipe_url = config['snipe-it']['url']
api_key = config['snipe-it']['apiKey']
default_status = config['snipe-it']['defaultStatus']
device_types = config['mosyle']['deviceTypes'].split(',')

snipe_rate_limit = int(config['snipe-it']['rate_limit'])

apple_image_check = bool(config['snipe-it'].getboolean('apple_image_check'))

#setup the snipe-it api
snipe = Snipe(api_key, snipe_url, apple_manufacturer_id, macos_category_id, ios_category_id, tvos_category_id, snipe_rate_limit, macos_fieldset_id, ios_fieldset_id, tvos_fieldset_id, apple_image_check)


#get all models
models = snipe.list_all_models().json()
print(models);
#loop through each model
for model in models['rows']:
    #is the model's manufacturer Apple?
    print('Processing model: ' + str(model['id']), model["model_number"])
    print("Is the model's manufacturer Apple?", "checking manufacture id " + str(model['manufacturer']['id']) +" against known apple manufacturer id: "+ str(apple_manufacturer_id))
    if int(model['manufacturer']['id']) == int(apple_manufacturer_id):
        #yes!
        print(Fore.GREEN, "Yes! Checking for photo!", Style.RESET_ALL);
        #Does it need a picture?
        if model['image'] == None:
            print("No photo. Dowloading photos")
            imageResponse = snipe.get_image_for_model(model["model_number"])
            if imageResponse != False:
                print("Photo Downloaded")
                snipe.setImageForModel(model["id"],imageResponse.content)
                payload = {
                    "image": imageResponse
                }
            
                snipe.update_model(str(model['id']), payload)
            else:
                print("no photo found, moving on")
        else:
            print("picture already set. Skipping")
    else:
        print(Fore.YELLOW,'model is not apple. Skip.',Style.RESET_ALL)

