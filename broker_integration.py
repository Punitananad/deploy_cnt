"""
Broker Integration Module
Integrates multi-broker system with the main Flask app
"""

from multi_broker_system import init_multi_broker_system, create_multi_broker_blueprint
from flask import Flask

def setup_broker_integration(app: Flask):
    """Setup broker integration with the Flask app"""
    
    # Initialize the multi-broker system
    init_multi_broker_system(app)
    
    # Register the multi-broker blueprint
    multi_broker_bp = create_multi_broker_blueprint()
    app.register_blueprint(multi_broker_bp, url_prefix='/api/multi_broker')
    
    print("✓ Multi-broker system initialized successfully")
    
    return app

def get_connected_brokers(user_id: str = 'default_user'):
    """Get list of connected brokers for a user"""
    from multi_broker_system import USER_SESSIONS, get_user_session
    
    connected = []
    for broker in ['kite', 'dhan', 'angel']:
        # Check both memory and database
        session_data = get_user_session(broker, user_id) or USER_SESSIONS[broker].get(user_id)
        if session_data:
            connected.append({
                'broker': broker,
                'user_id': user_id,
                'status': 'connected'
            })
    
    return connected

def is_broker_connected(broker: str, user_id: str = 'default_user'):
    """Check if a specific broker is connected"""
    from multi_broker_system import USER_SESSIONS, get_user_session
    
    session_data = get_user_session(broker, user_id) or USER_SESSIONS[broker].get(user_id)
    return session_data is not None