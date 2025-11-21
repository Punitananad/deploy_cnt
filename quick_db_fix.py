#!/usr/bin/env python3
"""
Quick Database Fix - Run this to create missing tables
"""

import os
import psycopg2
from urllib.parse import urlparse

def create_missing_tables():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    if not database_url:
        print("❌ No database URL found")
        return False
    
    try:
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        # Read and execute SQL script
        with open('create_missing_tables.sql', 'r') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ All missing tables created successfully!")
        
        # List current tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Current tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_missing_tables()