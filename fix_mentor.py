#!/usr/bin/env python3
"""
Simple script to fix mentor system database issues
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_mentor_system():
    """Fix mentor system database issues"""
    try:
        # Import Flask app and database
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from database_config import get_postgres_url, get_database_engine_options
        
        # Create minimal Flask app for database operations
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = get_postgres_url()
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = get_database_engine_options()
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        db = SQLAlchemy(app)
        
        with app.app_context():
            print("Starting mentor system fix...")
            
            # Check if mentor table exists
            from sqlalchemy import text
            result = db.session.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'mentor'
                    )
                """)
            ).fetchone()
            
            if not result[0]:
                print("Creating mentor table...")
                # Create mentor table manually
                db.session.execute(text("""
                    CREATE TABLE mentor (
                        id SERIAL PRIMARY KEY,
                        mentor_id VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(128) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(120) NOT NULL,
                        commission_pct REAL DEFAULT 40.0,
                        created_by_admin_id INTEGER NOT NULL,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.session.commit()
                print("[OK] Mentor table created")
            else:
                print("[OK] Mentor table exists")
                
                # Check if commission_pct column exists
                try:
                    db.session.execute(text("SELECT commission_pct FROM mentor LIMIT 1"))
                    print("[OK] commission_pct column exists")
                except Exception:
                    print("Adding commission_pct column...")
                    db.session.execute(text("ALTER TABLE mentor ADD COLUMN commission_pct REAL DEFAULT 40.0"))
                    db.session.commit()
                    print("[OK] commission_pct column added")
            
            # Check if coupon table exists
            result = db.session.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'coupon'
                    )
                """)
            ).fetchone()
            
            if not result[0]:
                print("Creating coupon table...")
                db.session.execute(text("""
                    CREATE TABLE coupon (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(50) UNIQUE NOT NULL,
                        discount_percent INTEGER NOT NULL DEFAULT 10,
                        active BOOLEAN DEFAULT TRUE,
                        mentor_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.session.commit()
                print("[OK] Coupon table created")
            else:
                print("[OK] Coupon table exists")
            
            print("\nMentor system fix completed successfully!")
            print("You can now access the mentor system without errors.")
            return True
            
    except Exception as e:
        print(f"Error fixing mentor system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_mentor_system()
    sys.exit(0 if success else 1)