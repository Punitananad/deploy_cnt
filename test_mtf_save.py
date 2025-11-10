import requests
import json

# Test the MTF save endpoint directly
url = "http://localhost:5000/save_mtf_result"

# Sample data that would be sent from the frontend
test_data = {
    'trade_type': 'buy',
    'avg_price': 100.0,
    'quantity': 10,
    'expected_return': 5.0,
    'risk_percent': 2.0,
    'capital_used': 250.0,
    'target_price': 105.0,
    'stop_loss_price': 98.0,
    'total_reward': 50.0,
    'total_risk': 20.0,
    'rr_ratio': 2.5,
    'symbol': 'TESTSTOCK',
    'comment': 'Test MTF trade',
    'leverage': 4.0
}

try:
    response = requests.post(url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 500:
        print("Server error occurred - check Flask console for detailed error logs")
    
except Exception as e:
    print(f"Request failed: {e}")