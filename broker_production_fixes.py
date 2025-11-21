# Production fixes for broker connection route
# This file contains production-safe implementations

from flask import render_template, request, current_app, render_template_string
from datetime import datetime
import traceback

def safe_log_error(message):
    """Safely log errors with fallback to print"""
    try:
        if current_app and hasattr(current_app, 'logger'):
            current_app.logger.error(message)
        else:
            print(f"ERROR: {message}")
    except Exception:
        print(f"ERROR: {message}")

def production_safe_real_broker_connect():
    """Production-safe version of real_broker_connect route"""
    try:
        # Get user_id from request args with fallback
        user_id = request.args.get('user_id', 'NES881')
        connected_broker = request.args.get('connected')  # Check if just connected
        connected_brokers = []
        
        # Try to import multi-broker functions with fallback
        try:
            from multi_broker_system import get_broker_session_status, USER_SESSIONS
            
            # Check all brokers for existing connections
            for broker in ['kite', 'dhan', 'angel']:
                try:
                    status = get_broker_session_status(broker, user_id)
                    if status.get('connected'):
                        connected_brokers.append({
                            'broker': broker,
                            'user_id': user_id,
                            'session_data': status.get('session_data', {})
                        })
                except Exception as e:
                    safe_log_error(f"Error checking {broker} status: {e}")
                    continue
                    
        except ImportError as e:
            safe_log_error(f"Multi-broker system not available: {e}")
            # Fallback: return empty connected brokers list
            connected_brokers = []
        except Exception as e:
            safe_log_error(f"Error importing multi-broker system: {e}")
            connected_brokers = []
        
        # If we just connected, show success message
        success_message = None
        if connected_broker:
            success_message = f"Successfully connected to {connected_broker.upper()}! You can now view your portfolio data."
        
        # Render template with error handling
        try:
            # Check if template exists
            from template_checker import check_template_exists, get_fallback_template_content
            
            if check_template_exists('multi_broker_connect.html'):
                return render_template('multi_broker_connect.html',
                                     connected_brokers=connected_brokers,
                                     has_connected_brokers=len(connected_brokers) > 0,
                                     user_id=user_id,
                                     success_message=success_message,
                                     now=datetime.now())
            else:
                # Use fallback template content
                safe_log_error("Template multi_broker_connect.html not found, using fallback")
                from flask import render_template_string
                fallback_content = get_fallback_template_content('multi_broker_connect.html')
                return render_template_string(fallback_content,
                                            connected_brokers=connected_brokers,
                                            has_connected_brokers=len(connected_brokers) > 0,
                                            user_id=user_id,
                                            success_message=success_message,
                                            now=datetime.now())
        except Exception as template_error:
            safe_log_error(f"Template rendering error: {template_error}")
            # Return minimal HTML response as fallback
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Broker Connect</title></head>
            <body>
                <h1>Broker Connection</h1>
                <p>Connected Brokers: {len(connected_brokers)}</p>
                <p>User ID: {user_id}</p>
                {f'<p style="color: green;">{success_message}</p>' if success_message else ''}
                <p><a href="/calculatentrade_journal/dashboard">Back to Dashboard</a></p>
            </body>
            </html>
            """
            
    except Exception as e:
        safe_log_error(f"Critical error in real_broker_connect: {e}")
        safe_log_error(f"Traceback: {traceback.format_exc()}")
        
        # Return error page
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Broker Connect - Error</title></head>
        <body>
            <h1>Broker Connection Error</h1>
            <p>Sorry, there was an error loading the broker connection page.</p>
            <p>Error: {str(e)}</p>
            <p><a href="/calculatentrade_journal/dashboard">Back to Dashboard</a></p>
        </body>
        </html>
        """, 500

def get_production_safe_broker_status(broker, user_id):
    """Production-safe broker status check"""
    try:
        from multi_broker_system import get_broker_session_status
        return get_broker_session_status(broker, user_id)
    except ImportError:
        return {'connected': False, 'error': 'Multi-broker system not available'}
    except Exception as e:
        safe_log_error(f"Error checking broker status: {e}")
        return {'connected': False, 'error': str(e)}