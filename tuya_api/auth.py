"""
@file auth_manager.py
@brief Authentication manager for the Tuya IoT API.
@details This module provides a comprehensive authentication management system for
         the Tuya IoT API, including automatic token refresh, signature generation,
         and environment variable management.

@author Nishan Dananjaya
@date 2025-02-13
@version 1.0
"""

import os
import time
import hmac
import hashlib
import uuid
import requests
from dotenv import load_dotenv, set_key
import threading

load_dotenv()  # Load environment variables from .env file

class AuthManager:
    """
    @brief Authentication manager class for Tuya API.
    
    @details Handles all authentication-related operations including token management,
             signature generation, and automatic token refresh in a background thread.
             The class manages environment variables and provides methods to access
             various authentication parameters.
    """

    def __init__(self):
        """
        @brief Initialize the AuthManager with environment variables.
        
        @details Loads all required authentication parameters from environment variables
                 and initializes threading components for automatic token refresh.
        """
        self.base_url = os.getenv("TUYA_BASE_URL")
        self.client_id = os.getenv("TUYA_ACCESS_ID")
        self.secret = os.getenv("TUYA_ACCESS_KEY")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.timestamp = os.getenv("TIMESTAMP")
        self.signature = os.getenv("SIGNATURE")
        self.sign_method = os.getenv("SIGN_METHOD")
        self.nonce = os.getenv("NONCE")
        self.token_expiry_time = float(os.getenv("TOKEN_EXPIRY_TIME", 0))
        self._stop_event = threading.Event()
        self._thread = None

    def _generate_signature(self, timestamp, nonce, string_to_sign):
        """
        @brief Generate HMAC-SHA256 signature for API authentication.
        
        @param timestamp str Current timestamp in milliseconds
        @param nonce str Unique identifier for the request
        @param string_to_sign str The string to be signed
        
        @return str The generated HMAC-SHA256 signature in uppercase hexadecimal format
        """
        return hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

    def _save_to_env(self, key, value):
        """
        @brief Save a key-value pair to the .env file.
        
        @param key str The environment variable key
        @param value str The value to save
        """
        set_key(".env", key, value)

    def get_access_token(self):
        """
        @brief Get access token from Tuya API.
        
        @details Retrieves a new access token if the current one is expired or
                 returns the existing valid token. Handles the complete token
                 acquisition process including signature generation and API call.
        
        @return str The valid access token
        
        @exception Exception Raised when token acquisition fails
        @exception requests.exceptions.RequestException Raised on API request failure
        """
        if self.access_token and time.time() < self.token_expiry_time:
            return self.access_token

        endpoint = "/v1.0/token"
        params = "grant_type=1"
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())

        headers_str = ""
        body_hash = hashlib.sha256("".encode('utf-8')).hexdigest()
        url_with_params = f"{endpoint}?{params}"
        string_to_sign = "GET" + "\n" + body_hash + "\n" + headers_str + "\n" + url_with_params
        str_to_sign = self.client_id + timestamp + nonce + string_to_sign

        signature = self._generate_signature(timestamp, nonce, str_to_sign)
        sign_method = "HMAC-SHA256"

        headers = {
            'client_id': self.client_id,
            't': timestamp,
            'sign': signature,
            'sign_method': sign_method,
            'nonce': nonce,
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }

        try:
            full_url = f"{self.base_url}{endpoint}?{params}"
            response = requests.get(full_url, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            if token_data.get("success", False):
                self.access_token = token_data["result"]["access_token"]
                self.token_expiry_time = time.time() + token_data["result"]["expire_time"]
                self.refresh_token = token_data["result"].get("refresh_token")
                self.timestamp = timestamp
                self.signature = signature
                self.sign_method = sign_method

                self._save_to_env("ACCESS_TOKEN", self.access_token)
                if self.refresh_token:
                    self._save_to_env("REFRESH_TOKEN", self.refresh_token)
                self._save_to_env("TIMESTAMP", self.timestamp)
                self._save_to_env("SIGNATURE", self.signature)
                self._save_to_env("SIGN_METHOD", self.sign_method)
                self._save_to_env("NONCE", nonce)

                return self.access_token
            else:
                raise Exception(f"Failed to get access token: {token_data.get('msg')}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting access token: {e}")

    def get_token(self):
        """
        @brief Public method to retrieve the access token.
        
        @return str The current access token
        """
        return self.get_access_token()

    def get_expiry_time(self):
        """
        @brief Get the expiry time of the access token.
        
        @return float Unix timestamp when the current token will expire
        """
        return self.token_expiry_time

    def get_refresh_token(self):
        """
        @brief Get the refresh token.
        
        @return str The current refresh token
        """
        return self.refresh_token

    def get_timestamp(self):
        """
        @brief Get the timestamp from the last API call.
        
        @return str The timestamp used in the most recent API call
        """
        return self.timestamp

    def get_signature(self):
        """
        @brief Get the signature from the last API call.
        
        @return str The signature used in the most recent API call
        """
        return self.signature

    def get_sign_method(self):
        """
        @brief Get the sign method used in the last API call.
        
        @return str The signing method (typically "HMAC-SHA256")
        """
        return self.sign_method
    
    def get_nonce(self):
        """
        @brief Get the nonce from the last API call.
        
        @return str The nonce used in the most recent API call
        """
        return self.nonce

    def is_token_expired(self):
        """
        @brief Check if the current access token is expired.
        
        @return bool True if the token is expired, False otherwise
        """
        return time.time() >= self.token_expiry_time

    def _check_token_expiry(self):
        """
        @brief Background task to check token expiration.
        
        @details Runs in a separate thread to periodically check if the token
                 is expired and automatically refreshes it when needed.
        """
        while not self._stop_event.is_set():
            if self.is_token_expired():
                try:
                    self.get_access_token()
                    print("Token refreshed successfully.")
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
            time.sleep(60)  # Check every 60 seconds

    def start_token_refresh_thread(self):
        """
        @brief Start the background token refresh thread.
        
        @details Initializes and starts a daemon thread that monitors token
                 expiration and handles automatic refresh.
        """
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._check_token_expiry)
            self._thread.daemon = True
            self._thread.start()

    def stop_token_refresh_thread(self):
        """
        @brief Stop the background token refresh thread.
        
        @details Signals the background thread to stop and waits for it to complete.
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()

if __name__ == "__main__":
    """
    @brief Example usage of the AuthManager class.
    
    @details Demonstrates how to initialize and use the AuthManager with
             automatic token refresh in a background thread.
    """
    auth_manager = AuthManager()
    auth_manager.start_token_refresh_thread()
    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        auth_manager.stop_token_refresh_thread()