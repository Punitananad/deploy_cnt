import pyotp
import requests
import json

# Your Angel One credentials
API_KEY = "dizbjQCI"
SECRET_KEY = "5359a24e-3bdd-4b81-972f-65c9525b84eb"
TOTP_SECRET = "LAQ5VTMK6QOU2XPPMAQIIVMCSA"
USER_ID = "P54947093"
MPIN = "1465"

def get_angel_totp():
    """Generate TOTP for Angel One"""
    totp = pyotp.TOTP(TOTP_SECRET)
    return totp.now()

def angel_login():
    """Login to Angel One API using MPIN"""
    totp_code = get_angel_totp()
    print(f"Generated TOTP: {totp_code}")
    
    url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByMpin"
    
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
        "mpin": MPIN,
        "totp": totp_code
    }
    
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status'):
            token = data['data']['jwtToken']
            print(f"SUCCESS! JWT Token: {token}")
            return token
        else:
            print(f"Login failed: {data.get('message')}")
    
    return None

if __name__ == "__main__":
    print("Testing Angel One API with MPIN...")
    token = angel_login()
    if token:
        print("Angel One integration working!")
    else:
        print("Angel One integration failed!")