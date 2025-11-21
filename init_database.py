#!/usr/bin/env python3
"""
Database initialization script for CalculatenTrade
This script ensures all database tables are created properly
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_instruments_table(db):
    """Initialize instruments table structure and indexes"""
    from sqlalchemy import text
    
    # Create instruments table if it doesn't exist
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS instruments (
            id SERIAL PRIMARY KEY,
            symbol_name VARCHAR(50) NOT NULL,
            display_name VARCHAR(100),
            security_id VARCHAR(20) NOT NULL,
            exch_id VARCHAR(10) NOT NULL,
            segment VARCHAR(10) NOT NULL,
            instrument_type VARCHAR(20) DEFAULT 'EQUITY',
            lot_size INTEGER DEFAULT 1,
            tick_size DECIMAL(10,4) DEFAULT 0.05,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """))
    
    # Create indexes for fast search
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments(symbol_name)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_instruments_display ON instruments(display_name)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_instruments_security_id ON instruments(security_id)"))
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_instruments_exch_segment ON instruments(exch_id, segment)"))
    
    db.session.commit()
    
    # Check existing count
    result = db.session.execute(text("SELECT COUNT(*) FROM instruments")).fetchone()
    print(f"✓ Instruments table ready with {result[0]} symbols")

def init_database():
    """Initialize all database tables"""
    try:
        # Import the Flask app
        from app import app, db
        
        with app.app_context():
            print("Starting database initialization...")
            
            # Create all tables
            db.create_all()
            print("✓ Core database tables created")
            
            # Initialize admin database
            try:
                from admin_blueprint import init_admin_db
                init_admin_db(db)
                print("✓ Admin database initialized")
            except Exception as e:
                print(f"⚠ Admin database initialization failed: {e}")
            
            # Initialize employee dashboard
            try:
                from employee_dashboard_bp import init_employee_dashboard_db
                init_employee_dashboard_db(db)
                print("✓ Employee dashboard initialized")
            except Exception as e:
                print(f"⚠ Employee dashboard initialization failed: {e}")
            
            # Initialize mentor database
            try:
                from mentor import init_mentor_db
                init_mentor_db(db)
                print("✓ Mentor database initialized")
            except Exception as e:
                print(f"⚠ Mentor database initialization failed: {e}")
            
            # Initialize subscription plans
            try:
                from subscription_models import init_subscription_plans
                init_subscription_plans()
                print("✓ Subscription plans initialized")
            except Exception as e:
                print(f"⚠ Subscription plans initialization failed: {e}")
            
            # Initialize instruments table structure
            try:
                init_instruments_table(db)
                print("✓ Instruments table structure initialized")
            except Exception as e:
                print(f"⚠ Instruments table initialization failed: {e}")
            
            # Check if mentor table exists and has the required columns
            try:
                from sqlalchemy import text
                result = db.session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'mentor'
                        )
                    """)
                ).fetchone()
                
                if result[0]:
                    print("✓ Mentor table exists")
                    
                    # Check for commission_pct column
                    try:
                        db.session.execute(text("SELECT commission_pct FROM mentor LIMIT 1"))
                        print("✓ Mentor table has commission_pct column")
                    except Exception:
                        print("⚠ Adding commission_pct column to mentor table...")
                        try:
                            db.session.execute(text("ALTER TABLE mentor ADD COLUMN commission_pct REAL DEFAULT 40.0"))
                            db.session.commit()
                            print("✓ Added commission_pct column")
                        except Exception as e:
                            print(f"⚠ Failed to add commission_pct column: {e}")
                            db.session.rollback()
                else:
                    print("⚠ Mentor table does not exist")
                    
            except Exception as e:
                print(f"⚠ Error checking mentor table: {e}")
            
            # List all tables
            try:
                from sqlalchemy import text
                result = db.session.execute(
                    text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        ORDER BY table_name
                    """)
                ).fetchall()
                
                tables = [row[0] for row in result]
                print(f"\n📋 Database has {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
                    
            except Exception as e:
                print(f"⚠ Error listing tables: {e}")
            
            print("\nDatabase initialization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)