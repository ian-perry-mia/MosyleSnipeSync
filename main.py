# Import all the things
import json
import datetime
import configparser
import colorama
import logging
import argparse
import pprint
from sys import exit

from mosyle import Mosyle
from snipe import Snipe
from colorama import Fore
from colorama import Style

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging output")
parser.add_argument("-i", "--insecure", action="store_true", help="disable SSL verification for snipe-it")

args = parser.parse_args()

logger = logging.getLogger("MosyleSnipeSync")

if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARN)

if args.insecure:
    verify_ssl = False
else:
    verify_ssl = True

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


snipe_url = config['snipe-it']['url']
api_key = config['snipe-it']['apiKey']
default_status = config['snipe-it']['defaultStatus']
device_types = config['mosyle']['deviceTypes'].split(',')

snipe_rate_limit = int(config['snipe-it']['rate_limit'])

apple_image_check = bool(config['snipe-it'].getboolean('apple_image_check'))



# Set the token for the Mosyle Api
mosyle = Mosyle(config['mosyle']['token'], config['mosyle']['url'], config['mosyle']['user'], config['mosyle']['password'])

# Set the call type for Mosyle
calltype = config['mosyle']['calltype']

#setup the snipe-it api
snipe = Snipe(api_key, snipe_url, apple_manufacturer_id, macos_category_id, ios_category_id, tvos_category_id, snipe_rate_limit, macos_fieldset_id, ios_fieldset_id, tvos_fieldset_id, apple_image_check, verify_ssl=verify_ssl)

for device_type in device_types:
    # Get the list of devices from Mosyle based on the deviceType and call type

    if calltype == "timestamp":
        mosyle_response = mosyle.list_timestamp(ts, ts, device_type).json()
    else:
        mosyle_response = mosyle.list(device_type).json()
    logger.debug(pprint.pformat(mosyle_response))

    # Check if the response is valid
    if 'status' in mosyle_response:
        if mosyle_response['status'] != "OK":
            logger.fatal('There was an issue with the Mosyle API. Stopping.', mosyle_response['message'])
    if 'status' in mosyle_response['response'][0]:
        logger.error('There was an issue with the Mosyle API. Stopping script.')
        logger.fatal(mosyle_response['response'][0]['info'])

    logger.info('Starting Snipe sync and looping through Mosyle hardware list')
    logger.debug(pprint.pformat(device))
    # Return Mosyle hardware and search them in snipe
    for device in mosyle_response['response'][0]['devices']:
        # If the device does not have an asset tag, skip it.
        if device['asset_tag'] is None:
            logger.info("Device does not have an asset tag, please assign and then sync again.")
            continue
        logger.info('Sarting for Mosyle Device ', device['device_name'])

        # If the device does not have a serial number, skip it.
        if device['serial_number'] == None:
            logger.info('There is no serial number here. It might be user-enrolled.')
            continue
        
        logger.info('Device serial number: ',str(device['serial_number']))
        
        logger.info('Checking snipe for Mosyle device by serial number: '+str(device['serial_number']))
        asset = snipe.listHardware(device['serial_number']).json()
        
        #check to see if Device model already exists on snipe
            
        logger.info("Checking to see if device model already exist on SnipeIt:", device['device_model'])
    model = snipe.search_model(device['device_model']).json()
        logger.info("Model:", model)
        # Create the asset model if is not exist
        if model['total'] == 0:
            logger.info('Model does not exist in Snipe. Need to make it.')
            if device['os'] == "mac":
                logger.info('Making a new Mac model', device['device_model'])
                model = snipe.create_model(device['device_model']).json()
                model = model['payload']['id']
            if device['os'] == "ios":
                logger.info('Making a new ios model', device['device_model'])
                model = snipe.create_mobile_model(device['device_model']).json()
                model = model['payload']['id']
            if device['os'] == "tvos":
                logger.info('Making New Apple TV Model', device['device_model'])
                model = snipe.create_apple_tv_model(device['device_model']).json()
                model = model['payload']['id']

        else:
            logger.info('Model already exists in SnipeIt!')
            model = model['rows'][0]['id']

        
        if device['CurrentConsoleManagedUser'] != None and "userid" in device:
            mosyle_user = device['userid']

        else:
            logger.info('this device is not currently assigned. Dont try to assign it later');
            mosyle_user = None
            

        #Create payload translating Mosyle to SnipeIt
    devicePayload = snipe.build_payload_from_mosyle(sn)
        
        # If asset doesnt exist create and assign it
        if ('messages' in asset and asset['messages'] == "Asset does not exist.") or ('total' in asset and asset['total'] == 0):
            asset = snipe.create_asset(model, devicePayload, device['asset_tag']).json()
            if mosyle_user != None:
                logger.info('Assigning asset to SnipIT user based on Mosyle Assignment')
                snipe.assign_asset(mosyle_user, asset['payload']['id'])
                continue

        # Update existing Devices
        if asset['total'] == 1:
            #f"{x:.2f}"
            logger.info('Asset ', device['serial_number'],' already exists in SnipeIt. Update it.')
            logger.info(asset['rows'][0]['name'])
            snipe.update_asset(asset['rows'][0]['id'], devicePayload)

        # Check the asset assignement state
        if mosyle_user != None:
            if asset['rows'][0]['assigned_to'] == None and device['userid'] != None:
                    snipe.assign_asset(device['userid'], asset['rows'][0]['id'])
                    #continue

            elif device['userid'] == None:
                snipe.unasigne_asset(asset['rows'][0]['id'])
                #continue

            elif asset['rows'][0]['assigned_to']['username'] == device['userid']:
                logger.info('nothing to see here')
            elif asset['rows'][0]['assigned_to']['username'] != device['userid']:
                snipe.unasigne_asset(asset['rows'][0]['id'])
                snipe.assign_asset(device['userid'], asset['rows'][0]['id'])
            else:
                logger.info('no assignement actions')
        
        logger.info("Checking to see if Mosyle needs an updated asset tag")
        #if there is no asset tag on mosyle, add the snipeit asset tag
        if(device['asset_tag'] == None or device['asset_tag'] == "" or device['asset_tag'] != asset['rows'][0]['asset_tag']):
            logger.info('update the mosyle asset tag of device ', device['serial_number'], 'to ', asset['rows'][0]['asset_tag'])
            mosyle.setAssetTag(device['serial_number'], asset['rows'][0]['asset_tag'])
        else:
            logger.info('Mosyle already has an assest tag of: ', device['asset_tag'])
    
    logger.info('Finished with OS: ', deviceType)
