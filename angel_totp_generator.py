#!/usr/bin/env python3
"""
Angel One TOTP Generator
Generates 30-second TOTP codes for Angel One API authentication
"""

import pyotp
import time
import requests
import json
from datetime import datetime

# Angel One API Credentials
API_KEY = "dizbjQCI"
SECRET_KEY = "5359a24e-3bdd-4b81-972f-65c9525b84eb"
TOTP_SECRET = "LAQ5VTMK6QOU2XPPMAQIIVMCSA"
USER_ID = "P54947093"

def generate_totp():
    """Generate TOTP code for Angel One API"""
    try:
        totp = pyotp.TOTP(TOTP_SECRET)
        current_totp = totp.now()
        print(f"Current TOTP: {current_totp}")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return current_totp
    except Exception as e:
        print(f"Error generating TOTP: {e}")
        return None

def test_angel_login():
    """Test Angel One API login with generated TOTP"""
    try:
        totp_code = generate_totp()
        if not totp_code:
            return False
        
        login_url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '192.168.1.1',
            'X-ClientPublicIP': '106.193.147.98',
            'X-MACAddress': '00:00:00:00:00:00',
            'X-PrivateKey': API_KEY
        }
        
        payload = {
            "clientcode": USER_ID,
            "password": SECRET_KEY,
            "totp": totp_code
        }
        
        print(f"\nTesting Angel One login...")
        print(f"URL: {login_url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(login_url, headers=headers, json=payload, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status'):
                print(f"[SUCCESS] Login successful!")
                print(f"JWT Token: {result.get('data', {}).get('jwtToken', 'Not found')}")
                return True
            else:
                print(f"[FAILED] Login failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during login test: {e}")
        return False

def continuous_totp_monitor():
    """Monitor TOTP generation continuously"""
    print("[INFO] Starting continuous TOTP monitoring...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            current_time = datetime.now()
            seconds = current_time.second
            
            # Generate new TOTP every 30 seconds (when seconds is 0 or 30)
            if seconds % 30 == 0:
                print(f"\n[TIME] {current_time.strftime('%H:%M:%S')} - Generating new TOTP...")
                totp_code = generate_totp()
                
                # Show remaining validity
                remaining = 30 - (seconds % 30)
                print(f"Valid for next {remaining} seconds")
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[STOP] TOTP monitoring stopped")

def validate_totp_secret():
    """Validate if TOTP secret is working correctly"""
    try:
        print("[INFO] Validating TOTP Secret...")
        totp = pyotp.TOTP(TOTP_SECRET)
        
        # Generate current TOTP
        current_totp = totp.now()
        print(f"Current TOTP: {current_totp}")
        
        # Verify the TOTP
        is_valid = totp.verify(current_totp)
        print(f"TOTP Validation: {'[VALID]' if is_valid else '[INVALID]'}")
        
        # Show timing info
        current_time = int(time.time())
        time_step = current_time // 30
        remaining_time = 30 - (current_time % 30)
        
        print(f"Current Unix Time: {current_time}")
        print(f"Time Step: {time_step}")
        print(f"Remaining Time: {remaining_time} seconds")
        
        return is_valid
        
    except Exception as e:
        print(f"[ERROR] Error validating TOTP: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Angel One TOTP Generator")
    print("=" * 50)
    
    print(f"API Key: {API_KEY}")
    print(f"User ID: {USER_ID}")
    print(f"TOTP Secret: {TOTP_SECRET}")
    print()
    
    # Validate TOTP secret first
    if validate_totp_secret():
        print("\n" + "=" * 50)
        
        # Test login
        if test_angel_login():
            print("\n[SUCCESS] Angel One API integration is working!")
        else:
            print("\n[FAILED] Angel One API integration failed")
            print("\n[INFO] Starting continuous TOTP monitoring to debug...")
            continuous_totp_monitor()
    else:
        print("\n[ERROR] TOTP Secret validation failed!")
        print("Please check your TOTP_SECRET configuration")