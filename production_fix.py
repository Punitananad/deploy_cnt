#!/usr/bin/env python3
"""
Production Fix Script for CalculatenTrade
Fixes common production deployment issues causing 500 errors
"""

import os
import sys
from pathlib import Path

def check_environment_variables():
    """Check critical environment variables"""
    print("🔍 Checking Environment Variables...")
    
    critical_vars = [
        'FLASK_SECRET',
        'GOOGLE_CLIENT_ID', 
        'GOOGLE_CLIENT_SECRET',
        'DB_PASSWORD',
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET'
    ]
    
    missing_vars = []
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing critical environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All critical environment variables are set")
        return True

def fix_flask_env():
    """Fix Flask environment configuration"""
    print("🔧 Fixing Flask Environment...")
    
    # Check if FLASK_ENV is set correctly
    flask_env = os.getenv('FLASK_ENV')
    if flask_env != 'production':
        print(f"⚠️  FLASK_ENV is set to '{flask_env}', should be 'production'")
        print("   Add this to your .env file: FLASK_ENV=production")
        return False
    else:
        print("✅ FLASK_ENV is correctly set to production")
        return True

def check_database_config():
    """Check database configuration"""
    print("🗄️  Checking Database Configuration...")
    
    db_type = os.getenv('DATABASE_TYPE', 'sqlite')
    if db_type != 'postgres':
        print(f"⚠️  DATABASE_TYPE is '{db_type}', should be 'postgres' for production")
        return False
    
    # Check if we have either DATABASE_URL or individual DB components
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("✅ DATABASE_URL is configured")
        return True
    
    # Check individual components
    db_components = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_components = [comp for comp in db_components if not os.getenv(comp)]
    
    if missing_components:
        print(f"❌ Missing database components: {', '.join(missing_components)}")
        return False
    else:
        print("✅ Database components are configured")
        return True

def check_google_oauth():
    """Check Google OAuth configuration"""
    print("🔐 Checking Google OAuth Configuration...")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Google OAuth credentials are missing")
        return False
    
    # Check if client_secret.json exists
    client_secret_path = Path('client_secret.json')
    if not client_secret_path.exists():
        print("⚠️  client_secret.json file is missing")
        print("   This file is required for Google OAuth to work")
        return False
    
    print("✅ Google OAuth configuration looks good")
    return True

def create_production_env_template():
    """Create a production .env template"""
    print("📝 Creating production .env template...")
    
    template = """# PRODUCTION ENVIRONMENT CONFIGURATION
# Replace placeholder values with your actual production values

# Flask Configuration
FLASK_SECRET=your-secret-key-here
FLASK_ENV=production
SESSION_PERMANENT_LIFETIME=2592000

# Production Security
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_DOMAIN=.calculatentrade.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration
ADMIN_MAIL_USERNAME=your-admin-email@gmail.com
ADMIN_MAIL_PASSWORD=your-admin-app-password
USER_MAIL_USERNAME=your-user-email@gmail.com
USER_MAIL_PASSWORD=your-user-app-password

# Database - Use either DATABASE_URL or individual components
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# OR use individual components:
# DB_HOST=your-db-host
# DB_PORT=5432
# DB_NAME=calculatentrade_db
# DB_USER=your-db-user
# DB_PASSWORD=your-db-password

# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Dhan API
DHAN_CLIENT_ID=your-dhan-client-id
DHAN_ACCESS_TOKEN=your-dhan-access-token

# Admin Key
ADMIN_KEY=your-admin-key
"""
    
    with open('.env.production.template', 'w') as f:
        f.write(template)
    
    print("✅ Created .env.production.template")
    print("   Copy this file to .env and fill in your actual values")

def main():
    """Main function to run all checks and fixes"""
    print("🚀 CalculatenTrade Production Fix Script")
    print("=" * 50)
    
    # Load environment variables from .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  No .env file found")
    
    issues_found = []
    
    # Run all checks
    if not check_environment_variables():
        issues_found.append("Missing environment variables")
    
    if not fix_flask_env():
        issues_found.append("Flask environment configuration")
    
    if not check_database_config():
        issues_found.append("Database configuration")
    
    if not check_google_oauth():
        issues_found.append("Google OAuth configuration")
    
    print("\n" + "=" * 50)
    
    if issues_found:
        print("❌ Issues found:")
        for issue in issues_found:
            print(f"   • {issue}")
        print("\n🔧 Recommended fixes:")
        print("   1. Copy .env.production.template to .env")
        print("   2. Fill in all placeholder values with your actual production values")
        print("   3. Ensure your production database is accessible")
        print("   4. Verify Google OAuth redirect URIs include your production domain")
        print("   5. Check that client_secret.json exists and is valid")
        
        create_production_env_template()
    else:
        print("✅ All checks passed! Your production configuration looks good.")
    
    print("\n🌐 Production URL Configuration:")
    print("   Make sure your Google OAuth redirect URIs include:")
    print("   • https://calculatentrade.com/auth/google/callback")
    print("   • https://www.calculatentrade.com/auth/google/callback")

if __name__ == "__main__":
    main()