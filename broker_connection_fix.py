# Broker Connection Production Fix
# Add this to your multi_broker_system.py or create a separate fix file

import os
import logging
from datetime import datetime

def diagnose_broker_connection():
    """Diagnose broker connection issues in production"""
    
    print("=== BROKER CONNECTION DIAGNOSIS ===")
    
    # 1. Check environment variables
    print("\n1. Environment Variables:")
    env_vars = [
        'DHAN_CLIENT_ID', 'DHAN_ACCESS_TOKEN',
        'FLASK_ENV', 'DATABASE_TYPE'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'TOKEN' in var or 'SECRET' in var:
                masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"  {var}: {masked}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: NOT SET ❌")
    
    # 2. Check token validity
    print("\n2. Token Status:")
    from token_store import get_token
    try:
        token = get_token()
        if token:
            print(f"  Token exists: {token[:10]}...{token[-4:]}")
            print(f"  Token length: {len(token)}")
        else:
            print("  No token found ❌")
    except Exception as e:
        print(f"  Token error: {e} ❌")
    
    # 3. Check API connectivity
    print("\n3. API Connectivity:")
    try:
        import requests
        from multi_broker_system import get_dhan_headers, DHAN_BASE_URL
        
        headers = get_dhan_headers()
        url = f"{DHAN_BASE_URL}/v2/marketfeed/ltp"
        
        # Test with a simple request
        response = requests.post(
            url, 
            headers=headers, 
            json={"NSE_EQ": [1333]},  # HDFC Bank
            timeout=10
        )
        
        print(f"  API Status: {response.status_code}")
        if response.status_code == 200:
            print("  API Connection: OK ✅")
        else:
            print(f"  API Error: {response.text} ❌")
            
    except Exception as e:
        print(f"  API Connection Error: {e} ❌")
    
    # 4. Check session storage
    print("\n4. Session Storage:")
    try:
        from multi_broker_system import USER_SESSIONS
        for broker in ['kite', 'dhan', 'angel']:
            count = len(USER_SESSIONS.get(broker, {}))
            print(f"  {broker.upper()} sessions: {count}")
    except Exception as e:
        print(f"  Session check error: {e}")
    
    print("\n=== END DIAGNOSIS ===")

def fix_production_config():
    """Apply production fixes"""
    
    print("=== APPLYING PRODUCTION FIXES ===")
    
    # 1. Update environment for production
    fixes = []
    
    # Check if we're in production
    if os.getenv('FLASK_ENV') == 'production':
        fixes.append("Production environment detected")
        
        # Ensure HTTPS for OAuth redirects
        if not os.getenv('FORCE_HTTPS'):
            os.environ['FORCE_HTTPS'] = 'true'
            fixes.append("Forced HTTPS for OAuth")
        
        # Set secure session cookies
        if not os.getenv('SESSION_COOKIE_SECURE'):
            os.environ['SESSION_COOKIE_SECURE'] = 'true'
            fixes.append("Enabled secure session cookies")
    
    # 2. Validate required tokens
    required_tokens = ['DHAN_CLIENT_ID', 'DHAN_ACCESS_TOKEN']
    missing_tokens = []
    
    for token in required_tokens:
        value = os.getenv(token)
        if not value or value == f'your-{token.lower().replace("_", "-")}-here':
            missing_tokens.append(token)
    
    if missing_tokens:
        print(f"❌ Missing tokens: {missing_tokens}")
        print("Please update these in your production environment")
    else:
        fixes.append("All required tokens present")
    
    # 3. Database connection fix
    if os.getenv('DATABASE_TYPE') == 'postgres':
        db_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_db = [var for var in db_vars if not os.getenv(var)]
        
        if missing_db:
            print(f"❌ Missing DB config: {missing_db}")
        else:
            fixes.append("Database configuration complete")
    
    print(f"✅ Applied {len(fixes)} fixes:")
    for fix in fixes:
        print(f"  - {fix}")
    
    print("=== FIXES COMPLETE ===")

if __name__ == "__main__":
    diagnose_broker_connection()
    fix_production_config()