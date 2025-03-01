"""
@file main.py
@brief script for Tuya API authentication management.
@details This script demonstrates the usage of the AuthManager class for handling
         Tuya API authentication, including token management and signature generation.

@author Nishan Dananjaya
@date 2025-02-13
@version 1.0
"""

from tuya_api.auth import AuthManager
from datetime import datetime

def main():
    """
    @brief Main function to demonstrate AuthManager functionality.
    
    @details This function demonstrates various authentication-related operations:
             - Retrieving access and refresh tokens
             - Checking token expiration
             - Getting authentication signatures and timestamps
             - Converting expiry times to human-readable format
    
    The function creates an instance of AuthManager and showcases its core
    authentication management capabilities.
    
    @exception Exception Catches and prints any exceptions that occur during
                        authentication operations
    
    Example usage:
    @code
        if __name__ == "__main__":
            main()
    @endcode
    """
    auth_manager = AuthManager()
    try:
        # Get the access token
        access_token = auth_manager.get_token()
        print("Access Token:", access_token)

        # Get the expiry time
        expiry_time = auth_manager.get_expiry_time()
        print("Token Expiry Time (Unix Timestamp):", expiry_time)

        # Convert expiry time to a human-readable format
        expiry_datetime = datetime.fromtimestamp(expiry_time)
        print("Token Expiry Time (Human-Readable):", 
              expiry_datetime.strftime("%Y-%m-%d %H:%M:%S"))

        # Get the refresh token
        refresh_token = auth_manager.get_refresh_token()
        print("Refresh Token:", refresh_token)

        # Get the timestamp
        timestamp = auth_manager.get_timestamp()
        print("Timestamp (t):", timestamp)

        # Get the signature
        signature = auth_manager.get_signature()
        print("Signature (sign):", signature)

        # Get the sign method
        sign_method = auth_manager.get_sign_method()
        print("Sign Method (sign_method):", sign_method)

        # Check if the token is expired
        if auth_manager.is_token_expired():
            print("Token is expired.")
        else:
            print("Token is still valid.")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    """
    @brief Script entry point.
    
    @details Executes the main function when the script is run directly.
             This ensures the authentication demonstration only runs when
             the script is executed as the primary program.
    """
    main()