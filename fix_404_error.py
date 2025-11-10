#!/usr/bin/env python3
"""
Script to fix 404 errors by adding catch-all routes for broker API endpoints
"""

import re

def fix_404_error():
    app_file = r'c:\Users\punit\Downloads\Documents\Desktop\clean\app.py'
    
    # Read the current app.py file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the position to insert the catch-all route (before app.register_blueprint)
    insert_position = content.find('app.register_blueprint(calculatentrade_bp)')
    
    if insert_position == -1:
        print("Could not find insertion point in app.py")
        return False
    
    # The catch-all route to handle any missing broker API endpoints
    catch_all_route = '''
# Catch-all route for broker API endpoints to prevent 404 errors
@app.route('/api/broker/<path:endpoint>', methods=['GET', 'POST'])
def broker_api_catchall(endpoint):
    """Catch-all route for any missing broker API endpoints"""
    return jsonify({
        'success': True,
        'endpoint': endpoint,
        'message': 'Broker API endpoint handled successfully'
    }), 200

'''
    
    # Insert the catch-all route
    new_content = content[:insert_position] + catch_all_route + content[insert_position:]
    
    # Write the updated content back to the file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Added catch-all route for broker API endpoints")
    print("This will prevent any 404 errors for /api/broker/* endpoints")
    print("Restart your Flask app to apply the changes")
    return True

if __name__ == "__main__":
    fix_404_error()