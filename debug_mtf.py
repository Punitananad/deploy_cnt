#!/usr/bin/env python3

# Debug script to test MTF save functionality
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, MTFTrade, current_user
from datetime import datetime, timezone
import json

# Test data that would typically be sent from frontend
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

def test_mtf_save():
    with app.app_context():
        try:
            print("Testing MTF trade creation...")
            print(f"Test data: {json.dumps(test_data, indent=2)}")
            
            # Simulate the save_mtf_result function logic
            trade_data = {
                'user_id': 1,  # Test user ID
                'trade_type': test_data.get('trade_type', 'buy'),
                'avg_price': float(test_data.get('avg_price')),
                'quantity': int(test_data.get('quantity')),
                'expected_return': float(test_data.get('expected_return')),
                'risk_percent': float(test_data.get('risk_percent')),
                'capital_used': float(test_data.get('capital_used')),
                'target_price': float(test_data.get('target_price')),
                'stop_loss_price': float(test_data.get('stop_loss_price')),
                'total_reward': float(test_data.get('total_reward')),
                'total_risk': float(test_data.get('total_risk')),
                'rr_ratio': float(test_data.get('rr_ratio')),
                'symbol': test_data.get('symbol'),
                'comment': test_data.get('comment'),
                'leverage': float(test_data.get('leverage', 4.0)),
                'timestamp': datetime.now(timezone.utc)
            }
            
            print(f"Trade data for MTFTrade: {json.dumps({k: str(v) for k, v in trade_data.items()}, indent=2)}")
            
            # Try to create MTFTrade instance
            trade = MTFTrade(**trade_data)
            print(f"MTFTrade instance created successfully: {trade}")
            
            # Try to add to session (without committing)
            db.session.add(trade)
            print("Trade added to session successfully")
            
            # Check if we can access the trade attributes
            print(f"Trade attributes:")
            print(f"  ID: {trade.id}")
            print(f"  Symbol: {trade.symbol}")
            print(f"  Avg Price: {trade.avg_price}")
            print(f"  Quantity: {trade.quantity}")
            print(f"  Leverage: {trade.leverage}")
            
            db.session.rollback()  # Don't actually save
            print("Test completed successfully!")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    test_mtf_save()