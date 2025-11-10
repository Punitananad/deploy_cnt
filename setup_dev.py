#!/usr/bin/env python3
"""
Development Setup Script for CalculatenTrade
This script initializes the database and sets up the development environment.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

def create_app():
    """Create Flask app with proper configuration"""
    app = Flask(__name__)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Database configuration
    from database_config import get_postgres_url, get_database_engine_options
    app.config["SQLALCHEMY_DATABASE_URI"] = get_postgres_url()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = get_database_engine_options()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    
    # Secret key
    app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret-change-this')
    
    return app

def init_database():
    """Initialize database with all models"""
    print("🚀 Initializing CalculatenTrade Development Environment...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Import and initialize database
        from journal import db
        db.init_app(app)
        
        # Import all blueprints to register models
        try:
            from admin_blueprint import init_admin_db
            from employee_dashboard_bp import init_employee_dashboard_db
            from mentor import init_mentor_db
            from subscription_models import init_subscription_plans
            
            print("📊 Creating database tables...")
            db.create_all()
            
            print("🔧 Initializing blueprint databases...")
            init_admin_db(db)
            init_employee_dashboard_db(db)
            init_mentor_db(db)
            
            print("💳 Initializing subscription plans...")
            init_subscription_plans()
            
            print("✅ Database initialization completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during database initialization: {e}")
            return False
    
    return True

def check_requirements():
    """Check if all required packages are installed"""
    print("📦 Checking requirements...")
    
    required_packages = [
        'flask', 'flask-sqlalchemy', 'flask-migrate', 'flask-login',
        'flask-mail', 'werkzeug', 'psycopg2-binary', 'python-dotenv',
        'requests', 'pytz', 'razorpay', 'authlib', 'google-auth-oauthlib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def check_environment():
    """Check if environment variables are set"""
    print("🔧 Checking environment configuration...")
    
    required_env_vars = [
        'FLASK_SECRET',
        'DATABASE_URL',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please check your .env file")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🎯 CalculatenTrade Development Setup")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("⚠️  Some environment variables are missing, but continuing...")
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("📝 Next steps:")
    print("   1. Update your .env file with proper credentials")
    print("   2. Run: python app.py")
    print("   3. Open: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()