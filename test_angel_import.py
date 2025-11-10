#!/usr/bin/env python3
"""
Test script to verify Angel broker import functionality
"""

import requests
import json

# Test data based on the logs
angel_trade_data = {
    'symbol': 'IDEA-EQ',
    'tradingsymbol': 'IDEA-EQ',
    'filledshares': '1',
    'averageprice': 9.6,
    'transactiontype': 'BUY',
    'orderid': '251110000563024',
    'orderstatus': 'complete',
    'broker': 'angel',
    'trade_type': 'long'
}

def test_import_trade():
    """Test the import trade endpoint"""
    url = "http://localhost:5000/calculatentrade_journal/api/broker/import-trade"
    
    print("Testing Angel broker import with data:")
    print(json.dumps(angel_trade_data, indent=2))
    
    try:
        response = requests.post(url, json=angel_trade_data)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Import successful!")
            else:
                print(f"❌ Import failed: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_import_trade()