#!/usr/bin/env python3
"""
Test mentor system functionality
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mentor_system():
    """Test mentor system"""
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
            print("Testing mentor system...")
            
            # Test mentor blueprint import
            try:
                from mentor import mentor_bp, init_mentor_db, Mentor
                print("[OK] Mentor blueprint imported successfully")
                
                # Initialize mentor database
                init_mentor_db(db)
                print("[OK] Mentor database initialized")
                
                # Test if we can query mentors
                if Mentor is not None:
                    mentor_count = Mentor.query.count()
                    print(f"[OK] Found {mentor_count} mentors in database")
                    
                    # Test mentor login functionality
                    test_mentor = Mentor.query.first()
                    if test_mentor:
                        print(f"[OK] Test mentor found: {test_mentor.mentor_id} ({test_mentor.name})")
                    else:
                        print("[WARNING] No mentors found for testing")
                else:
                    print("[ERROR] Mentor model is None")
                
            except Exception as e:
                print(f"[ERROR] Error testing mentor system: {e}")
                import traceback
                traceback.print_exc()
            
            print("\nMentor system test completed!")
            return True
            
    except Exception as e:
        print(f"Error in mentor system test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mentor_system()
    sys.exit(0 if success else 1)