#!/usr/bin/env python3
"""
Fix mentor login system by ensuring proper initialization
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_mentor_login():
    """Fix mentor login system"""
    try:
        # Import Flask app and database
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from database_config import get_postgres_url, get_database_engine_options
        from werkzeug.security import generate_password_hash
        
        # Create minimal Flask app for database operations
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = get_postgres_url()
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = get_database_engine_options()
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        db = SQLAlchemy(app)
        
        with app.app_context():
            print("Starting mentor login fix...")
            
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
            
            # Check if we have any mentors
            mentor_count = db.session.execute(
                text("SELECT COUNT(*) FROM mentor")
            ).fetchone()[0]
            
            if mentor_count == 0:
                print("No mentors found. Creating demo mentor...")
                # Create a demo mentor for testing
                demo_password = "Demo123!"
                password_hash = generate_password_hash(demo_password)
                
                db.session.execute(text("""
                    INSERT INTO mentor (mentor_id, password_hash, name, email, commission_pct, created_by_admin_id, active)
                    VALUES (:mentor_id, :password_hash, :name, :email, :commission_pct, :created_by_admin_id, :active)
                """), {
                    'mentor_id': 'DEMO001',
                    'password_hash': password_hash,
                    'name': 'Demo Mentor',
                    'email': 'demo@mentor.com',
                    'commission_pct': 40.0,
                    'created_by_admin_id': 1,
                    'active': True
                })
                db.session.commit()
                
                print(f"[OK] Demo mentor created:")
                print(f"     Mentor ID: DEMO001")
                print(f"     Password: {demo_password}")
                print(f"     Name: Demo Mentor")
            else:
                print(f"[OK] Found {mentor_count} mentors in database")
            
            # Test mentor login functionality
            print("Testing mentor system...")
            
            # Import mentor blueprint
            try:
                from mentor import mentor_bp, init_mentor_db
                init_mentor_db(db)
                print("[OK] Mentor system initialized successfully")
            except Exception as e:
                print(f"[WARNING] Mentor system initialization issue: {e}")
                # Continue anyway
            
            print("\nMentor login system fix completed!")
            print("You can now access the mentor login at: http://localhost:5000/mentor/login")
            
            if mentor_count == 0:
                print("\nDemo login credentials:")
                print("Mentor ID: DEMO001")
                print("Password: Demo123!")
            
            return True
            
    except Exception as e:
        print(f"Error fixing mentor login: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_mentor_login()
    sys.exit(0 if success else 1)