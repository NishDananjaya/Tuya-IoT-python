"""
@file get_devices_list.py
@brief Returns the list of devices with only name and ID
@details This script retrieves the list of devices from the Tuya Cloud API and returns the device names and IDs.
         The script reads the Tuya Cloud API credentials from the .env file in the project root directory.
         The script can be run directly to print the device list to the console.
@author Nishan Dananjaya
@date 2025-02-13
@version 1.0
"""

import hashlib
import hmac
import json
import time
import requests
import os 
from dotenv import load_dotenv

# Specify the path to the .env file in the project root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

class Cloud(object):
    """
    A class to interact with the Tuya Cloud API.
    
    This class provides methods to authenticate, send requests, and retrieve device information
    from the Tuya Cloud platform.
    """

    def __init__(self, apiKey=None, apiSecret=None, apiDeviceID=None, new_sign_algorithm=True, initial_token=None, **extrakw):
        """
        Initialize the Cloud class with API credentials and configuration.

        @param apiKey: The API key for Tuya Cloud.
        @param apiSecret: The API secret for Tuya Cloud.
        @param apiDeviceID: The device ID for Tuya Cloud.
        @param new_sign_algorithm: Whether to use the new signing algorithm (default is True).
        @param initial_token: An initial access token (optional).
        @param extrakw: Additional keyword arguments.
        """
        # Class Variables
        self.CONFIGFILE = 'tinytuya.json'
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.apiDeviceID = apiDeviceID
        self.urlhost = os.getenv("TUYA_BASE_URL").replace('https://', '')  # Get URL from .env
        self.uid = None     # Tuya Cloud User ID
        self.token = os.getenv("ACCESS_TOKEN") if initial_token is None else initial_token
        self.error = None
        self.new_sign_algorithm = new_sign_algorithm
        self.server_time_offset = 0
        self.use_old_device_list = True
        self.mappings = None

        if (not apiKey) or (not apiSecret):
            try:
                # Load defaults from config file if available
                config = {}
                with open(self.CONFIGFILE) as f:
                    config = json.load(f)
                    self.apiKey = config['apiKey']
                    self.apiSecret = config['apiSecret']
                    if 'apiDeviceID' in config:
                        self.apiDeviceID = config['apiDeviceID']
            except:
                raise TypeError('Tuya Cloud Key and Secret required')

    def _tuyaplatform(self, uri, action='GET', post=None, ver='v1.0', recursive=False, query=None, content_type=None):
        """
        Handle GET and POST requests to Tuya Cloud.

        @param uri: The URI to request.
        @param action: The HTTP action (GET, POST, PUT, DELETE).
        @param post: The POST data (optional).
        @param ver: The API version (default is 'v1.0').
        @param recursive: Whether to retry the request if the token is invalid (default is False).
        @param query: The query parameters (optional).
        @param content_type: The content type for the request (optional).
        @return: The response from the Tuya Cloud API.
        """
        # Build URL and Header
        if ver:
            url = "https://%s/%s/%s" % (self.urlhost, ver, uri)
        elif uri[0] == '/':
            url = "https://%s%s" % (self.urlhost, uri)
        else:
            url = "https://%s/%s" % (self.urlhost, uri)
        
        headers = {}
        body = {}
        sign_url = url
        if post is not None:
            body = json.dumps(post)
        if action not in ('GET', 'POST', 'PUT', 'DELETE'):
            action = 'POST' if post else 'GET'
        if action == 'POST' and content_type is None:
            content_type = 'application/json'
        if content_type:
            headers['Content-type'] = content_type
        if query:
            # note: signature must be calculated before URL-encoding!
            if type(query) == str:
                # if it's a string then assume no url-encoding is needed
                if query[0] == '?':
                    url += query
                else:
                    url += '?' + query
                sign_url = url
            else:
                # dicts are unsorted, however Tuya requires the keys to be in alphabetical order for signing
                #  as per https://developer.tuya.com/en/docs/iot/singnature?id=Ka43a5mtx1gsc
                if type(query) == dict:
                    sorted_query = []
                    for k in sorted(query.keys()):
                        sorted_query.append( (k, query[k]) )
                    query = sorted_query
                    # calculate signature without url-encoding
                    sign_url += '?' + '&'.join( [str(x[0]) + '=' + str(x[1]) for x in query] )
                    req = requests.Request(action, url, params=query).prepare()
                    url = req.url
                else:
                    req = requests.Request(action, url, params=query).prepare()
                    sign_url = url = req.url
        now = int(time.time()*1000)
        headers = dict(list(headers.items()) + [('Signature-Headers', ":".join(headers.keys()))]) if headers else {}
        if self.token is None:
            payload = self.apiKey + str(now)
            headers['secret'] = self.apiSecret
        else:
            payload = self.apiKey + self.token + str(now)

        # If running the post 6-30-2021 signing algorithm update the payload to include it's data
        if self.new_sign_algorithm:
            payload += ('%s\n' % action +                                                # HTTPMethod
                hashlib.sha256(bytes((body or "").encode('utf-8'))).hexdigest() + '\n' + # Content-SHA256
                ''.join(['%s:%s\n'%(key, headers[key])                                   # Headers
                            for key in headers.get("Signature-Headers", "").split(":")
                            if key in headers]) + '\n' +
                '/' + sign_url.split('//', 1)[-1].split('/', 1)[-1])
        # Sign Payload
        signature = hmac.new(
            self.apiSecret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()

        # Create Header Data
        headers['client_id'] = self.apiKey
        headers['sign'] = signature
        headers['t'] = str(now)
        headers['sign_method'] = 'HMAC-SHA256'
        headers['mode'] = 'cors'

        if self.token is not None:
            headers['access_token'] = self.token

        # Send Request to Cloud and Get Response
        if action == 'GET':
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, data=body)
            

        # Check to see if token is expired
        if "token invalid" in response.text:
            if recursive is True:
              
                return None
            if not self.token:
                return None
            else:
                return self._tuyaplatform(uri, action, post, ver, True)

        try:
            response_dict = json.loads(response.content.decode())
            self.error = None
        except:
            try:
                response_dict = json.loads(response.content)
            except:
                return self.error
        # Check to see if token is expired
        return response_dict

    def _getuid(self, deviceid=None):
        """
        Get user ID (UID) for a specific device.

        @param deviceid: The device ID to get the UID for.
        @return: The UID of the device.
        """
        if not self.token:
            return self.error
        if not deviceid:
            return 0
        uri = 'devices/%s' % deviceid
        response_dict = self._tuyaplatform(uri)

        if not response_dict['success']:
            if 'code' not in response_dict:
                response_dict['code'] = -1
            if 'msg' not in response_dict:
                response_dict['msg'] = 'Unknown Error'

        uid = response_dict['result']['uid']
        return uid

    def cloudrequest(self, url, action=None, post=None, query=None):
        """
        Make a generic cloud request and return the results.

        @param url: The URL to fetch, i.e. "/v1.0/devices/0011223344556677/logs".
        @param action: The HTTP action (GET, POST, DELETE, or PUT). Defaults to GET, unless POST data is supplied.
        @param post: The POST body data. Will be fed into json.dumps() before posting.
        @param query: A dict containing query string key/value pairs.
        @return: The response from the Tuya Cloud API.
        """
        if not self.token:
            return self.error
        if action is None:
            action = 'POST' if post else 'GET'
        return self._tuyaplatform(url, action=action, post=post, ver=None, query=query)

    # merge device list 'result2' into 'result1'
    # if result2 has a device which is not in result1 then it will be added
    # if result2 has a key which does not exist or is empty in result1 then that key will be copied over
    def _update_device_list( self, result1, result2 ):
        """
        Merge two device lists.

        @param result1: The first device list.
        @param result2: The second device list.
        """
        for new_device in result2:
            if 'id' not in new_device or not new_device['id']:
                continue
            found = False
            for existing_device in result1:
                if 'id' in existing_device and existing_device['id'] == new_device['id']:
                    found = True
                    for k in new_device:
                        if k not in existing_device or not existing_device[k]:
                            existing_device[k] = new_device[k]
            if not found:
                result1.append( new_device )

    def _get_all_devices( self, uid=None, device_ids=None ):
        """
        Retrieve all devices associated with a user or a list of device IDs.

        @param uid: The user ID to retrieve devices for (optional).
        @param device_ids: A list of device IDs to retrieve (optional).
        @return: A dictionary containing the list of devices and metadata.
        """
        fetches = 0
        our_result = { 'result': [] }
        last_row_key = None
        has_more = True
        total = 0

        if uid:
            # get device list for specified user id
            query = {'page_size':'75', 'source_type': 'tuyaUser', 'source_id': uid}
            # API docu: https://developer.tuya.com/en/docs/cloud/dc413408fe?id=Kc09y2ons2i3b
            uri = '/v1.3/iot-03/devices'
            if device_ids:
                if isinstance( device_ids, tuple ) or isinstance( device_ids, list ):
                    query['device_ids'] = ','.join(device_ids)
                else:
                    query['device_ids'] = device_ids
        else:
            # get all devices
            query = {'size':'50'}
            # API docu: https://developer.tuya.com/en/docs/cloud/fc19523d18?id=Kakr4p8nq5xsc
            uri = '/v1.0/iot-01/associated-users/devices'

        while has_more:
            result = self.cloudrequest( uri, query=query )
            fetches += 1
            has_more = False


            # format it the same as before, basically just moves result->devices into result
            for i in result:
                if i == 'result':
                    # by-user-id has the result in 'list' while all-devices has it in 'devices'
                    if 'list' in result[i] and 'devices' not in result[i]:
                        our_result[i] += result[i]['list']
                    elif 'devices' in result[i]:
                        our_result[i] += result[i]['devices']

                    if 'total' in result[i]: total = result[i]['total']
                    if 'last_row_key' in result[i]:
                        query['last_row_key'] = result[i]['last_row_key']
                    if 'has_more' in result[i]:
                        has_more = result[i]['has_more']
                else:
                    our_result[i] = result[i]

        our_result['fetches'] = fetches
        our_result['total'] = total

        return our_result

    def getdevices(self):
        """
        Return a list of devices with only name and ID.

        @return: A list of dictionaries containing device names and IDs.
        """
        json_data = self._get_all_devices()
        
        if not json_data or 'result' not in json_data:
            return []

        devs = json_data['result']
        device_list = []
        
        for dev in devs:
            device_list.append({
                'name': dev.get('name', ''),
                'id': dev.get('id', '')
            })
            
        return device_list

if __name__ == '__main__':
    # Load environment variables
    CLIENT_ID = os.getenv("TUYA_ACCESS_ID")
    ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY")

    # Get devices with only name and ID
    devices = Cloud(apiKey=CLIENT_ID, apiSecret=ACCESS_KEY).getdevices()
    print(json.dumps(devices))