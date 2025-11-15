#!/usr/bin/env python3
"""
Check available mentors in the database
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_mentors():
    """Check available mentors"""
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
            print("Checking available mentors...")
            
            # Get all mentors
            from sqlalchemy import text
            mentors = db.session.execute(
                text("""
                    SELECT mentor_id, name, email, active, created_at
                    FROM mentor
                    ORDER BY created_at DESC
                """)
            ).fetchall()
            
            if mentors:
                print(f"\nFound {len(mentors)} mentors:")
                print("-" * 80)
                print(f"{'Mentor ID':<12} {'Name':<20} {'Email':<25} {'Active':<8} {'Created'}")
                print("-" * 80)
                
                for mentor in mentors:
                    mentor_id, name, email, active, created_at = mentor
                    status = "Yes" if active else "No"
                    created_str = created_at.strftime("%Y-%m-%d") if created_at else "Unknown"
                    print(f"{mentor_id:<12} {name:<20} {email:<25} {status:<8} {created_str}")
                
                print("-" * 80)
                print("\nYou can use any of the above Mentor IDs to login.")
                print("If you don't know the password, contact the admin who created the mentor account.")
                
            else:
                print("No mentors found in database.")
            
            return True
            
    except Exception as e:
        print(f"Error checking mentors: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_mentors()
    sys.exit(0 if success else 1)