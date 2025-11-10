#!/usr/bin/env python3
"""
Test script to verify the import trade functionality
"""

import requests
import json

# Test data
test_trade = {
    "symbol": "RELIANCE",
    "quantity": 10,
    "price": 2500.50,
    "trade_type": "long",
    "broker": "dhan",
    "broker_id": "TEST123",
    "date": "2025-01-10"
}

def test_import_trade():
    """Test the import trade endpoint"""
    url = "http://localhost:5000/calculatentrade_journal/api/broker/import-trade"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Testing import trade endpoint: {url}")
        print(f"Test data: {json.dumps(test_trade, indent=2)}")
        
        response = requests.post(url, json=test_trade, headers=headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Import trade test PASSED")
        else:
            print("❌ Import trade test FAILED")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_import_trade()