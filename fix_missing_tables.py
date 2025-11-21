#!/usr/bin/env python3
"""
Fix Missing Database Tables
This script will create all missing tables in your production database.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database_config import get_postgres_url, get_database_engine_options

# Create Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_postgres_url()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = get_database_engine_options()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import all models to ensure they're registered
from app import (
    User, UserSettings, ResetOTP, EmailVerifyOTP, DeleteAccountOTP,
    PasswordResetToken, IntradayTrade, DeliveryTrade, SwingTrade, 
    MTFTrade, FOTrade, TradeSplit, PreviewTemplate, AIPlanTemplate,
    Payment, CouponUsage
)

# Import journal models
try:
    from journal import Trade, Strategy, Rule, Challenge, ChallengeTrade, ChallengeMood
    print("Journal models imported successfully")
except ImportError as e:
    print(f"Warning: Could not import journal models: {e}")

# Import subscription models
try:
    from subscription_models import SubscriptionPlan, UserSubscription, SubscriptionHistory
    print("Subscription models imported successfully")
except ImportError as e:
    print(f"Warning: Could not import subscription models: {e}")

# Import admin/mentor models
try:
    from admin_blueprint import Employee
    print("Admin models imported successfully")
except ImportError as e:
    print(f"Warning: Could not import admin models: {e}")

try:
    from mentor import Mentor, Coupon
    print("Mentor models imported successfully")
except ImportError as e:
    print(f"Warning: Could not import mentor models: {e}")

def create_missing_tables():
    """Create all missing database tables"""
    with app.app_context():
        try:
            print("Creating all database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # List all tables
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Current tables in database ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
        
        return True

def initialize_default_data():
    """Initialize default data for critical tables"""
    with app.app_context():
        try:
            # Initialize subscription plans
            try:
                from subscription_models import init_subscription_plans
                init_subscription_plans()
                print("✅ Subscription plans initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize subscription plans: {e}")
            
            # Initialize admin data
            try:
                from admin_blueprint import init_admin_db
                init_admin_db(db)
                print("✅ Admin system initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize admin system: {e}")
            
            # Initialize mentor system
            try:
                from mentor import init_mentor_db
                init_mentor_db(db)
                print("✅ Mentor system initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize mentor system: {e}")
                
            db.session.commit()
            print("✅ Default data initialization completed")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing default data: {e}")

if __name__ == "__main__":
    print("🔧 Fixing Missing Database Tables...")
    print("=" * 50)
    
    if create_missing_tables():
        print("\n🔧 Initializing default data...")
        initialize_default_data()
        print("\n✅ Database fix completed successfully!")
        print("\n📝 Next steps:")
        print("1. Deploy this script to your production server")
        print("2. Run: python fix_missing_tables.py")
        print("3. Restart your application")
    else:
        print("\n❌ Database fix failed!")