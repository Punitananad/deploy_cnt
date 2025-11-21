@calculatentrade_bp.route('/real_broker_connect')
@subscription_required_journal
def real_broker_connect():
    """Debug route - show only connected brokers"""
    try:
        from multi_broker_system import USER_SESSIONS
        
        user_id = request.args.get('user_id', 'NES881')
        connected_brokers = []
        debug_info = []
        
        # Check each broker
        for broker in ['kite', 'dhan', 'angel']:
            sessions = USER_SESSIONS.get(broker, {})
            user_session = sessions.get(user_id)
            
            debug_info.append(f"{broker}: {bool(user_session)}")
            
            if user_session:
                connected_brokers.append({
                    'broker': broker,
                    'user_id': user_id,
                    'session_data': user_session
                })
        
        # Return debug info as JSON for production debugging
        return jsonify({
            'user_id': user_id,
            'connected_brokers': connected_brokers,
            'debug_info': debug_info,
            'total_sessions': {
                'kite': len(USER_SESSIONS.get('kite', {})),
                'dhan': len(USER_SESSIONS.get('dhan', {})),
                'angel': len(USER_SESSIONS.get('angel', {}))
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'user_id': 'NES881',
            'connected_brokers': [],
            'debug_info': ['Error occurred']
        })