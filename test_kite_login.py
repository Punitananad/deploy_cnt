#!/usr/bin/env python3
"""
Test script for Kite login flow
"""
import requests
import json

# Your Kite credentials
USER_ID = "NES881"
API_KEY = "dg0e9xp065nfmkxm"
API_SECRET = "7y92wjx2c3xuafuwbtsxg3bfvvl3h0fu"

BASE_URL = "http://localhost:5000"

def register_kite_app():
    """Register Kite app credentials"""
    url = f"{BASE_URL}/api/multi_broker/register_app/kite"
    
    payload = {
        "user_id": USER_ID,
        "api_key": API_KEY,
        "api_secret": API_SECRET
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Registration Error: {e}")
        return False

def test_kite_login():
    """Test Kite login flow"""
    url = f"{BASE_URL}/api/multi_broker/kite/login?user_id={USER_ID}"
    
    try:
        response = requests.get(url, allow_redirects=False)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(f"Redirect URL: {redirect_url}")
            print("\nTo complete login:")
            print("1. Open the redirect URL in your browser")
            print("2. Login to Kite")
            print("3. The callback will be handled automatically")
        
        return response.status_code == 302
    except Exception as e:
        print(f"Login Error: {e}")
        return False

def check_kite_status():
    """Check Kite connection status"""
    url = f"{BASE_URL}/api/multi_broker/kite/status?user_id={USER_ID}"
    
    try:
        response = requests.get(url)
        print(f"Status Check: {response.status_code}")
        print(f"Status Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Status Check Error: {e}")
        return False

def main():
    print("=== Kite Login Test ===")
    print(f"User ID: {USER_ID}")
    print(f"API Key: {API_KEY}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Step 1: Register app
    print("Step 1: Registering Kite app...")
    if register_kite_app():
        print("[SUCCESS] App registered successfully")
    else:
        print("[ERROR] App registration failed")
        return
    
    print()
    
    # Step 2: Test login
    print("Step 2: Testing Kite login...")
    if test_kite_login():
        print("[SUCCESS] Login initiated successfully")
    else:
        print("[ERROR] Login failed")
        return
    
    print()
    
    # Step 3: Check status (before login completion)
    print("Step 3: Checking status (before login completion)...")
    check_kite_status()

if __name__ == "__main__":
    main()