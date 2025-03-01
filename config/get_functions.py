"""
@file get_functions.py
@brief A Python script to retrieve device functions from the Tuya API.
@details This script demonstrates how to retrieve device functions from the Tuya API using HMAC-SHA256 authentication.

@author Nishan Dananjaya
@date 2025-02-13
@version 1.0
"""

import os
import time
import hmac
import hashlib
import requests
import uuid
from dotenv import load_dotenv

# Specify the path to the .env file in the project root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def generate_signature(client_id, secret, access_token, t, nonce, url, method="GET", body=""):
    """
    @brief Generate the HMAC-SHA256 signature for Tuya API requests.
    
    @details This function creates a signature using HMAC-SHA256 algorithm required for
             authenticating requests to the Tuya API. The signature is generated based on
             the concatenation of various parameters and the request body hash.
    
    @param client_id: str The client ID (Access ID) provided by Tuya
    @param secret: str The client secret (Access Key) provided by Tuya
    @param access_token: str The access token for API authentication
    @param t: str Timestamp in milliseconds
    @param nonce: str A unique identifier for the request
    @param url: str The API endpoint URL
    @param method: str The HTTP method (default: "GET")
    @param body: str The request body (default: "")
    
    @return str The generated HMAC-SHA256 signature in uppercase hexadecimal format
    """
    headers_str = ""  # No special headers needed for signing
    body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    
    string_to_sign = method + "\n" + \
                    body_hash + "\n" + \
                    headers_str + "\n" + \
                    url
    
    str_to_sign = client_id + access_token + t + nonce + string_to_sign
    
    signature = hmac.new(
        secret.encode('utf-8'),
        str_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature

def get_device_functions(url, client_id, secret, access_token, device_id):
    """
    @brief Retrieve the device functions from Tuya API.
    
    @details This function makes an authenticated GET request to the Tuya API
             to retrieve the functions available for a specific device. It handles
             the generation of required authentication parameters and headers.
    
    @param url: str The base URL of the Tuya API
    @param client_id: str The client ID (Access ID) provided by Tuya
    @param secret: str The client secret (Access Key) provided by Tuya
    @param access_token: str The access token for API authentication
    @param device_id: str The ID of the device to query
    
    @return dict|None Returns the JSON response from the API if successful, None if an error occurs
    
    @exception requests.exceptions.RequestException Raised when the API request fails
    """
    t = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    
    endpoint = f"/v1.0/iot-03/devices/{device_id}/functions"
    full_url = f"{url}{endpoint}"
    
    signature = generate_signature(client_id, secret, access_token, t, nonce, endpoint)
    
    headers = {
        'client_id': client_id,
        't': t,
        'sign': signature,
        'sign_method': 'HMAC-SHA256',
        'nonce': nonce,
        'access_token': access_token,
        'Accept': '*/*',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(full_url, headers=headers)
        
        print(f"Request URL: {full_url}")
        print(f"Timestamp: {t}")
        print(f"Nonce: {nonce}")
        print(f"Generated signature: {signature}")
        print(f"Response status code: {response.status_code}")
        print(f"Access Token: {access_token}")
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving device functions: {e}")
        return None

if __name__ == "__main__":
    """
    @brief Main entry point for the script.
    
    @details Loads environment variables and executes the device function retrieval.
             Required environment variables:
             - TUYA_BASE_URL: The base URL for the Tuya API
             - TUYA_ACCESS_ID: The client ID provided by Tuya
             - TUYA_ACCESS_KEY: The client secret provided by Tuya
             - ACCESS_TOKEN: The access token for authentication
             - DEVICE_ID: The ID of the device to query
    """
    API_URL = os.getenv("TUYA_BASE_URL")
    CLIENT_ID = os.getenv("TUYA_ACCESS_ID")
    SECRET = os.getenv("TUYA_ACCESS_KEY")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    DEVICE_ID = os.getenv("DEVICE_ID")
    
    if not all([API_URL, CLIENT_ID, SECRET, ACCESS_TOKEN, DEVICE_ID]):
        print("Error: Missing required environment variables in .env file.")
    else:
        result = get_device_functions(API_URL, CLIENT_ID, SECRET, ACCESS_TOKEN, DEVICE_ID)
        print("\nDevice Functions Response:", result)