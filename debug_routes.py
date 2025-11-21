# Debug routes for production troubleshooting
from flask import Blueprint, jsonify, request
import sys
import os
import traceback

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/broker_status')
def debug_broker_status():
    """Debug route to check broker system status"""
    try:
        debug_info = {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'imports': {},
            'templates': {},
            'errors': []
        }
        
        # Test imports
        try:
            import multi_broker_system
            debug_info['imports']['multi_broker_system'] = 'OK'
        except ImportError as e:
            debug_info['imports']['multi_broker_system'] = f'FAILED: {str(e)}'
            debug_info['errors'].append(f'multi_broker_system import failed: {str(e)}')
        
        try:
            import broker_production_fixes
            debug_info['imports']['broker_production_fixes'] = 'OK'
        except ImportError as e:
            debug_info['imports']['broker_production_fixes'] = f'FAILED: {str(e)}'
            debug_info['errors'].append(f'broker_production_fixes import failed: {str(e)}')
        
        # Check template existence
        template_paths = [
            'templates/multi_broker_connect.html',
            'multi_broker_connect.html'
        ]
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                debug_info['templates'][template_path] = 'EXISTS'
            else:
                debug_info['templates'][template_path] = 'NOT FOUND'
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@debug_bp.route('/test_route')
def test_route():
    """Simple test route to verify Flask is working"""
    return jsonify({
        'status': 'OK',
        'message': 'Debug route is working',
        'user_id': request.args.get('user_id', 'not_provided')
    })