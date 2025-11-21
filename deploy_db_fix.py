#!/usr/bin/env python3
"""
Production Database Fix Script
Run this on your production server to create missing tables.
"""

import os
import sys
from datetime import datetime, timezone

def main():
    print("🚀 Production Database Fix")
    print("=" * 40)
    print(f"Started at: {datetime.now()}")
    
    # Check environment
    if not os.getenv('DATABASE_URL') and not os.getenv('POSTGRES_URL'):
        print("❌ No database URL found in environment variables")
        print("Make sure DATABASE_URL or POSTGRES_URL is set")
        return False
    
    try:
        # Import and run the fix
        from fix_missing_tables import create_missing_tables, initialize_default_data
        
        print("\n🔧 Step 1: Creating missing tables...")
        if not create_missing_tables():
            print("❌ Failed to create tables")
            return False
        
        print("\n🔧 Step 2: Initializing default data...")
        initialize_default_data()
        
        print("\n✅ Database fix completed successfully!")
        print("\n📋 Summary:")
        print("- All missing tables have been created")
        print("- Default data has been initialized")
        print("- Your application should now work properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)