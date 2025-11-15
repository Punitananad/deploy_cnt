#!/usr/bin/env python3
"""
Restart the Flask app with proper mentor system initialization
"""

import os
import sys
import subprocess
import time

def restart_app():
    """Restart the Flask application"""
    try:
        print("Restarting Flask application with mentor system...")
        
        # Kill any existing Flask processes
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, check=False)
            time.sleep(2)
        except:
            pass
        
        # Initialize the mentor system first
        print("Initializing mentor system...")
        result = subprocess.run([sys.executable, 'fix_mentor_login.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Mentor system initialized successfully")
        else:
            print(f"⚠ Mentor initialization warning: {result.stderr}")
        
        # Start the Flask app
        print("Starting Flask application...")
        print("Access the app at: http://localhost:5000")
        print("Mentor login at: http://localhost:5000/mentor/login")
        print("\nPress Ctrl+C to stop the server")
        
        # Run the Flask app
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\nShutting down Flask application...")
    except Exception as e:
        print(f"Error restarting app: {e}")

if __name__ == "__main__":
    restart_app()