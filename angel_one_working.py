import pyotp
import requests
import json

# Angel One credentials
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
    """Login to Angel One API"""
    totp_code = get_angel_totp()
    print(f"TOTP: {totp_code}")
    
    url = "https://apiconnect.angelone.in/rest/auth/angelbroking/user/v1/loginByMpin"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-UserType': 'USER',
        'X-SourceID': 'WEB',
        'X-ClientLocalIP': '127.0.0.1',
        'X-ClientPublicIP': '127.0.0.1',
        'X-MACAddress': 'fe80::216c:f2ff:fe71:25c8',
        'X-PrivateKey': API_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    payload = {
        "clientcode": USER_ID,
        "mpin": MPIN,
        "totp": totp_code
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status'):
                    token = data['data']['jwtToken']
                    print(f"SUCCESS! Token: {token[:50]}...")
                    return token
                else:
                    print(f"Login failed: {data.get('message')}")
            except:
                print(f"Response: {response.text}")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    return None

# Test just TOTP generation
def test_totp_only():
    """Test TOTP generation only"""
    print("Testing TOTP generation...")
    for i in range(3):
        totp = get_angel_totp()
        print(f"TOTP {i+1}: {totp}")
        import time
        time.sleep(1)

if __name__ == "__main__":
    print("Angel One API Test")
    print("1. Testing TOTP generation first...")
    test_totp_only()
    
    print("\n2. Testing login...")
    token = angel_login()
    
    if token:
        print("\nAngel One working!")
    else:
        print("\nAngel One failed - check credentials")