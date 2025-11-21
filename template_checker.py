# Template checker for production environment
import os
from flask import current_app

def check_template_exists(template_name):
    """Check if a template file exists in the templates directory"""
    try:
        # Get template folder path
        if current_app:
            template_folder = current_app.template_folder
        else:
            # Fallback to default templates folder
            template_folder = os.path.join(os.path.dirname(__file__), 'templates')
        
        template_path = os.path.join(template_folder, template_name)
        return os.path.exists(template_path)
    except Exception:
        return False

def get_fallback_template_content(template_name):
    """Get fallback HTML content for missing templates"""
    if template_name == 'multi_broker_connect.html':
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Broker Connection - CalculatenTrade</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .broker-card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .connected { background-color: #d4edda; border-color: #c3e6cb; }
        .btn { padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }
        .btn:hover { background-color: #0056b3; }
        .success { color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .error { color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Broker Connection</h1>
            <p>Connect your trading accounts to import live data</p>
        </div>
        
        {% if success_message %}
        <div class="success">{{ success_message }}</div>
        {% endif %}
        
        {% if has_connected_brokers %}
        <h2>Connected Brokers</h2>
        {% for broker in connected_brokers %}
        <div class="broker-card connected">
            <h3>{{ broker.broker|title }} - Connected</h3>
            <p>User ID: {{ broker.user_id }}</p>
            <a href="/api/multi_broker/{{ broker.broker }}/orders?user_id={{ broker.user_id }}" class="btn">View Orders</a>
            <a href="/api/multi_broker/{{ broker.broker }}/positions?user_id={{ broker.user_id }}" class="btn">View Positions</a>
            <a href="/api/multi_broker/{{ broker.broker }}/trades?user_id={{ broker.user_id }}" class="btn">View Trades</a>
        </div>
        {% endfor %}
        {% else %}
        <div class="broker-card">
            <h3>No Connected Brokers</h3>
            <p>Connect your trading accounts to start importing live data.</p>
        </div>
        {% endif %}
        
        <div style="margin-top: 30px; text-align: center;">
            <a href="/calculatentrade_journal/dashboard" class="btn">Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
        """
    
    return """
<!DOCTYPE html>
<html>
<head><title>Template Not Found</title></head>
<body>
    <h1>Template Not Found</h1>
    <p>The requested template could not be loaded.</p>
    <p><a href="/calculatentrade_journal/dashboard">Back to Dashboard</a></p>
</body>
</html>
    """