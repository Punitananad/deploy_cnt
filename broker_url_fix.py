# Quick fix for broker connection URLs in production

import os

def fix_broker_urls():
    """Fix broker callback URLs for production"""
    
    # Update your production .env file with this:
    production_env_additions = """
# Broker Connection URLs - Production
APP_BASE_URL=https://www.calculatentrade.com

# Ensure HTTPS for OAuth callbacks
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
"""
    
    print("Add these to your production .env file:")
    print(production_env_additions)
    
    # Also update broker app registrations
    print("\nUpdate your broker app callback URLs to:")
    print("Kite: https://www.calculatentrade.com/api/multi_broker/kite/callback")
    print("Dhan: https://www.calculatentrade.com/api/multi_broker/dhan/callback") 
    print("Angel: https://www.calculatentrade.com/api/multi_broker/angel/callback")

if __name__ == "__main__":
    fix_broker_urls()