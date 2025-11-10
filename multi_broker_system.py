import os
import json
import requests
from flask import Flask, request, redirect, session, jsonify, render_template, Blueprint
from dotenv import load_dotenv
from datetime import datetime
import pyotp

# KiteConnect SDK
from kiteconnect import KiteConnect

# DhanHQ SDK (handles both old and new versions)
try:
    from dhanhq import DhanHQ
    def make_dhan_client(client_id: str, access_token: str):
        return DhanHQ(client_id=client_id, access_token=access_token)
except ImportError:
    from dhanhq import dhanhq as _dhan_factory
    def make_dhan_client(client_id: str, access_token: str):
        return _dhan_factory(client_id, access_token)

# Angel One SmartAPI SDK
try:
    from SmartApi import SmartConnect
except ImportError:
    print("Warning: SmartAPI not available. Angel One integration disabled.")
    SmartConnect = None

load_dotenv()

# Blueprint for multi-broker routes
multi_broker_bp = Blueprint('multi_broker', __name__, url_prefix='/api/multi_broker')
broker_api_bp = Blueprint('broker_api', __name__, url_prefix='/api/broker')

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")

# In-memory stores (replace with DB in production)
USER_APPS = {
    "kite": {},
    "dhan": {},
    "angel": {}
}
USER_SESSIONS = {
    "kite": {},
    "dhan": {},
    "angel": {}
}

# ===================== KITE HELPERS =====================
def get_kite_for_user(user_id, access_token=None):
    creds = USER_APPS["kite"].get(user_id)
    if not creds:
        raise ValueError("No app credentials for this user")
    kite = KiteConnect(api_key=creds["api_key"])
    if access_token:
        kite.set_access_token(access_token)
    return kite

# ===================== DHAN HELPERS =====================
DHAN_AUTH_BASE = "https://auth.dhan.co"

def _dhan_headers(partner_id, partner_secret):
    return {
        "partner_id": partner_id,
        "partner_secret": partner_secret,
        "Content-Type": "application/json"
    }

def _dhan_generate_consent(partner_id, partner_secret):
    url = f"{DHAN_AUTH_BASE}/partner/generate-consent"
    r = requests.post(url, headers=_dhan_headers(partner_id, partner_secret), json={})
    r.raise_for_status()
    data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
    consent_id = data.get("consentId") or data.get("consent_id")
    if not consent_id:
        raise RuntimeError(f"generate-consent missing consentId: {data}")
    return consent_id

def _dhan_consume_consent(partner_id, partner_secret, token_id):
    url = f"{DHAN_AUTH_BASE}/partner/consume-consent"
    r = requests.get(url, headers=_dhan_headers(partner_id, partner_secret), params={"tokenId": token_id})
    r.raise_for_status()
    return r.json()

def _dhan_client_from_session(user_id):
    sess = USER_SESSIONS["dhan"].get(user_id)
    if not sess:
        return None, jsonify({"ok": False, "message": "Not connected"}), 401
    client_id = sess.get("dhan_client_id") or user_id
    access_token = sess.get("access_token")
    if not access_token:
        return None, jsonify({"ok": False, "message": "Missing Dhan access token"}), 500
    return make_dhan_client(client_id, access_token), None, None

# ===================== ANGEL ONE HELPERS =====================
def _angel_sdk_login(api_key: str, client_code: str, password: str, totp: str):
    if SmartConnect is None:
        raise RuntimeError("SmartAPI not available")
    smart = SmartConnect(api_key=api_key)
    data = smart.generateSession(clientCode=client_code, password=password, totp=totp)
    if data.get('errorcode'):
        raise RuntimeError(f"Angel login failed: {data.get('message')}")
    jwt = data['data'].get("jwtToken")
    if not jwt:
        raise RuntimeError(f"SmartAPI login ok but token missing: {data}")
    return {
        "jwt_token": jwt,
        "refresh_token": data['data'].get("refreshToken"),
        "feed_token": data['data'].get("feedToken"),
        "smart_api": smart
    }

# ===================== REGISTRATION =====================
@multi_broker_bp.route('/register_app/<broker>', methods=["POST"])
def register_app_broker(broker):
    if broker not in USER_APPS:
        return jsonify({"ok": False, "message": "unknown broker"}), 400
    
    data = request.get_json(force=True)
    user_id = data.get("user_id", "").strip()
    api_key = data.get("api_key")
    api_secret = data.get("api_secret")
    client_id = data.get("client_id")
    access_token = data.get("access_token")
    totp_secret = data.get("totp_secret")

    if not user_id:
        return jsonify({"ok": False, "message": "user_id required"}), 400

    USER_APPS[broker][user_id] = {
        "api_key": api_key,
        "api_secret": api_secret,
        "client_id": client_id,
        "access_token": access_token,
        "totp_secret": totp_secret
    }
    return jsonify({"ok": True, "message": f"Registered {user_id} for {broker}"}), 200

# ===================== KITE LOGIN FLOW =====================
@multi_broker_bp.route('/kite/login')
def kite_login():
    user_id = request.args.get("user_id", "").strip()
    if not user_id or user_id not in USER_APPS["kite"]:
        return jsonify({"ok": False, "message": "Unknown user_id or app not registered"}), 400
    session["oauth_user_id"] = user_id
    kite = get_kite_for_user(user_id)
    login_url = kite.login_url()
    sep = "&" if "?" in login_url else "?"
    return redirect(f"{login_url}{sep}state={user_id}")

@multi_broker_bp.route('/kite/callback')
def kite_callback():
    request_token = request.args.get("request_token")
    user_id = session.get("oauth_user_id") or request.args.get("state")
    
    # If no user_id from session or state, try to get from URL params
    if not user_id:
        user_id = request.args.get("user_id")
    
    if not request_token:
        return "Missing request_token in callback", 400
    
    if not user_id:
        return "Missing user_id - session lost or state parameter missing", 400
    
    creds = USER_APPS["kite"].get(user_id)
    if not creds:
        return f"No stored credentials for user {user_id}. Please register Kite app first.", 400
    
    kite = KiteConnect(api_key=creds["api_key"])
    try:
        data = kite.generate_session(request_token, api_secret=creds["api_secret"])
        USER_SESSIONS["kite"][user_id] = {
            "access_token": data["access_token"],
            "kite_user_id": data.get("user_id"),
            "session_id": data["access_token"][:10] + "..."
        }
        # Clear session data
        session.pop("oauth_user_id", None)
        return redirect(f"/calculatentrade_journal/real_broker_connect?login_success=kite&user_id={user_id}")
    except Exception as e:
        return f"Kite authentication error: {str(e)}", 400

# ===================== DHAN LOGIN FLOW =====================
@multi_broker_bp.route('/dhan/login')
def dhan_login():
    user_id = request.args.get("user_id", "").strip()
    if not user_id:
        return jsonify({"ok": False, "message": "user_id required"}), 400

    creds = USER_APPS["dhan"].get(user_id)
    if not creds:
        return jsonify({"ok": False, "message": "No Dhan registration found for this user"}), 400

    # Direct token mode
    if creds.get("client_id") and creds.get("access_token"):
        USER_SESSIONS["dhan"][user_id] = {
            "access_token": creds["access_token"],
            "dhan_client_id": creds["client_id"],
            "mode": "direct"
        }
        return redirect(f"/calculatentrade_journal/real_broker_connect?login_success=dhan&user_id={user_id}")

    # Partner consent mode
    partner_id = creds.get("api_key")
    partner_secret = creds.get("api_secret")
    if partner_id and partner_secret:
        try:
            consent_id = _dhan_generate_consent(partner_id, partner_secret)
        except Exception as e:
            return jsonify({"ok": False, "message": f"generate-consent failed: {e}"}), 400
        session["dhan_user_id"] = user_id
        session["dhan_consent_id"] = consent_id
        consent_url = f"{DHAN_AUTH_BASE}/consent-login?consentId={consent_id}"
        return redirect(consent_url)

    return jsonify({"ok": False, "message": "Provide either client_id+access_token or partner_id+partner_secret"}), 400

@multi_broker_bp.route('/dhan/callback')
def dhan_callback():
    token_id = request.args.get("tokenid") or request.args.get("tokenId")
    user_id = session.get("dhan_user_id")
    consent_id = session.get("dhan_consent_id")
    if not token_id or not user_id:
        return "Missing tokenId or session lost", 400

    creds = USER_APPS["dhan"].get(user_id)
    if not creds:
        return f"No stored Dhan credentials for user {user_id}", 400

    partner_id = creds.get("api_key")
    partner_secret = creds.get("api_secret")
    if not partner_id or not partner_secret:
        return "Partner credentials missing for consent consume", 400

    try:
        consume = _dhan_consume_consent(partner_id, partner_secret, token_id)
        client_id = consume.get("clientId") or consume.get("client_id") or user_id
        access_token = (
            consume.get("accessToken")
            or consume.get("access_token")
            or consume.get("jwt")
            or consume.get("JWT")
        )
        if not access_token:
            return f"Consume consent ok, but token missing. Payload: {json.dumps(consume)}", 400

        USER_SESSIONS["dhan"][user_id] = {
            "access_token": access_token,
            "dhan_client_id": client_id,
            "consent_id": consent_id,
            "mode": "partner"
        }
        return redirect(f"/calculatentrade_journal/real_broker_connect?login_success=dhan&user_id={user_id}")
    except Exception as e:
        return f"Dhan consume-consent error: {str(e)}", 400

# ===================== ANGEL ONE LOGIN FLOW =====================
@multi_broker_bp.route('/angel/login')
def angel_login():
    user_id = request.args.get("user_id", "").strip()
    if not user_id:
        return jsonify({"ok": False, "message": "user_id required"}), 400

    creds = USER_APPS["angel"].get(user_id)
    if not creds or not creds.get("api_key"):
        return jsonify({"ok": False, "message": "Register Angel credentials first"}), 400

    # Generate TOTP if secret is available
    totp_value = ""
    if creds.get("totp_secret"):
        try:
            totp = pyotp.TOTP(creds["totp_secret"])
            totp_value = totp.now()
        except Exception as e:
            return jsonify({"ok": False, "message": f"TOTP generation failed: {str(e)}"}), 400

    return render_template("angel_login.html", 
                         user_id=user_id,
                         totp_value=totp_value,
                         totp_secret=creds.get("totp_secret", ""))

@multi_broker_bp.route('/angel/refresh_totp', methods=["POST"])
def angel_refresh_totp():
    """Refresh TOTP for Angel One login"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        totp_secret = data.get('totp_secret')
        
        if not totp_secret:
            return jsonify({"ok": False, "message": "TOTP secret required"}), 400
        
        clean_secret = totp_secret.replace(" ", "").upper()
        totp = pyotp.TOTP(clean_secret)
        new_totp = totp.now()
        
        return jsonify({
            "ok": True,
            "totp": new_totp,
            "message": "TOTP refreshed successfully"
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Failed to refresh TOTP: {str(e)}"
        }), 500

@multi_broker_bp.route('/angel/login/password', methods=["POST"])
def angel_login_password():
    if SmartConnect is None:
        return "SmartAPI not available", 500
    
    user_id = request.form.get("user_id", "").strip()
    client_code = request.form.get("client_code", "").strip()
    password = request.form.get("password", "").strip()
    totp = request.form.get("totp", "").strip()
    
    if not all([user_id, client_code, password, totp]):
        return "All fields are required", 400

    creds = USER_APPS["angel"].get(user_id)
    if not creds:
        return f"No Angel credentials found for user {user_id}", 400

    try:
        result = _angel_sdk_login(creds["api_key"], client_code, password, totp)
        
        USER_SESSIONS["angel"][user_id] = {
            "access_token": result["jwt_token"],
            "refresh_token": result["refresh_token"],
            "feed_token": result["feed_token"],
            "angel_client_id": creds["api_key"],
            "client_code": client_code,
            "connected": True
        }
        
        # Store SmartConnect object separately (not in session)
        if not hasattr(USER_SESSIONS["angel"], "_smart_apis"):
            USER_SESSIONS["angel"]["_smart_apis"] = {}
        USER_SESSIONS["angel"]["_smart_apis"][user_id] = result["smart_api"]
        # Redirect to calculatentrade_journal real_broker_connect page
        return redirect("/calculatentrade_journal/real_broker_connect?login_success=angel&user_id=" + user_id)
    except Exception as e:
        return f"Angel login failed: {str(e)}", 400

# ===================== DATA ENDPOINTS =====================

# ----- Kite Connect Endpoints -----
@multi_broker_bp.route('/kite/orders')
def kite_orders():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["kite"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    kite = get_kite_for_user(user_id, sess["access_token"])
    try:
        orders = kite.orders()
        return jsonify({"ok": True, "data": orders})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/kite/positions')
def kite_positions():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["kite"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    kite = get_kite_for_user(user_id, sess["access_token"])
    try:
        return jsonify({"ok": True, "data": kite.positions()})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/kite/trades')
def kite_trades():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["kite"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    kite = get_kite_for_user(user_id, sess["access_token"])
    try:
        return jsonify({"ok": True, "data": kite.trades()})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

# ----- DhanHQ Endpoints -----
@multi_broker_bp.route('/dhan/orders')
def dhan_orders():
    user_id = request.args.get("user_id")
    client, resp, code = _dhan_client_from_session(user_id)
    if client is None:
        return resp, code
    try:
        orders = client.get_order_list()
        return jsonify({"ok": True, "data": orders})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/dhan/positions')
def dhan_positions():
    user_id = request.args.get("user_id")
    client, resp, code = _dhan_client_from_session(user_id)
    if client is None:
        return resp, code
    try:
        positions = client.get_positions()
        return jsonify({"ok": True, "data": positions})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/dhan/trades')
def dhan_trades():
    user_id = request.args.get("user_id")
    client, resp, code = _dhan_client_from_session(user_id)
    if client is None:
        return resp, code
    try:
        if hasattr(client, "get_trade_book"):
            trades = client.get_trade_book()
        elif hasattr(client, "get_trade_history"):
            trades = client.get_trade_history(from_date=None, to_date=None, page_number=0)
        else:
            trades = []
        return jsonify({"ok": True, "data": trades})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

# ----- Angel One Endpoints -----
@multi_broker_bp.route('/angel/orders')
def angel_orders():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["angel"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    
    # Get SmartConnect object from separate storage
    smart_api = USER_SESSIONS["angel"].get("_smart_apis", {}).get(user_id)
    if not smart_api:
        return jsonify({"ok": False, "message": "SmartAPI object not found"}), 401
    
    try:
        orders_response = smart_api.orderBook()
        print(f"Angel orders raw response: {orders_response}")
        
        # Handle different response formats
        if isinstance(orders_response, dict):
            if 'data' in orders_response:
                orders = orders_response['data']
            elif 'result' in orders_response:
                orders = orders_response['result']
            else:
                orders = orders_response
        else:
            orders = orders_response
            
        # Ensure orders is a list
        if not isinstance(orders, list):
            orders = []
            
        print(f"Angel orders processed: {len(orders)} orders found")
        return jsonify({"ok": True, "data": orders})
    except Exception as e:
        print(f"Angel orders error: {str(e)}")
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/angel/positions')
def angel_positions():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["angel"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    
    # Get SmartConnect object from separate storage
    smart_api = USER_SESSIONS["angel"].get("_smart_apis", {}).get(user_id)
    if not smart_api:
        return jsonify({"ok": False, "message": "SmartAPI object not found"}), 401
    
    try:
        positions_response = smart_api.position()
        print(f"Angel positions raw response: {positions_response}")
        
        # Handle different response formats
        if isinstance(positions_response, dict):
            if 'data' in positions_response:
                positions = positions_response['data']
            elif 'result' in positions_response:
                positions = positions_response['result']
            else:
                positions = positions_response
        else:
            positions = positions_response
            
        # Ensure positions is a list
        if not isinstance(positions, list):
            positions = []
            
        print(f"Angel positions processed: {len(positions)} positions found")
        return jsonify({"ok": True, "data": positions})
    except Exception as e:
        print(f"Angel positions error: {str(e)}")
        return jsonify({"ok": False, "message": str(e)}), 400

@multi_broker_bp.route('/angel/trades')
def angel_trades():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["angel"].get(user_id)
    if not sess:
        return jsonify({"ok": False, "message": "Not connected"}), 401
    
    # Get SmartConnect object from separate storage
    smart_api = USER_SESSIONS["angel"].get("_smart_apis", {}).get(user_id)
    if not smart_api:
        return jsonify({"ok": False, "message": "SmartAPI object not found"}), 401
    
    try:
        trades_response = smart_api.tradeBook()
        print(f"Angel trades raw response: {trades_response}")
        
        # Handle different response formats
        if isinstance(trades_response, dict):
            if 'data' in trades_response:
                trades = trades_response['data']
            elif 'result' in trades_response:
                trades = trades_response['result']
            else:
                trades = trades_response
        else:
            trades = trades_response
            
        # Ensure trades is a list
        if not isinstance(trades, list):
            trades = []
            
        print(f"Angel trades processed: {len(trades)} trades found")
        return jsonify({"ok": True, "data": trades})
    except Exception as e:
        print(f"Angel trades error: {str(e)}")
        return jsonify({"ok": False, "message": str(e)}), 400

# ===================== STATUS ENDPOINTS =====================
@multi_broker_bp.route('/kite/status')
def kite_status():
    user_id = request.args.get("user_id")
    return jsonify(USER_SESSIONS["kite"].get(user_id) or {"msg": "no session"})

@multi_broker_bp.route('/dhan/status')
def dhan_status():
    user_id = request.args.get("user_id")
    return jsonify(USER_SESSIONS["dhan"].get(user_id) or {"msg": "no session"})

@multi_broker_bp.route('/angel/status')
def angel_status():
    user_id = request.args.get("user_id")
    sess = USER_SESSIONS["angel"].get(user_id)
    if not sess:
        return jsonify({"msg": "no session"})
    
    # Check if SmartConnect object exists in separate storage
    has_smart_api = user_id in USER_SESSIONS["angel"].get("_smart_apis", {})
    smart_api = USER_SESSIONS["angel"].get("_smart_apis", {}).get(user_id)
    
    # Test API call if SmartConnect object exists
    api_test_result = None
    if smart_api:
        try:
            # Try a simple API call to test connection
            profile = smart_api.getProfile()
            api_test_result = "success"
            print(f"Angel API test successful for user {user_id}: {profile}")
        except Exception as e:
            api_test_result = f"failed: {str(e)}"
            print(f"Angel API test failed for user {user_id}: {str(e)}")
    
    return jsonify({
        "angel_client_id": sess.get("angel_client_id"),
        "client_code": sess.get("client_code"),
        "has_smart_api": has_smart_api,
        "connected": sess.get("connected", False),
        "api_test": api_test_result,
        "session_keys": list(sess.keys())
    })

# ===================== BROKER API ENDPOINTS =====================
@broker_api_bp.route('/get-all-data', methods=['GET'])
def api_get_all_data():
    """Get all broker data via /api/broker/get-all-data"""
    broker = request.args.get('broker')
    user_id = request.args.get('user_id')
    
    if not broker or not user_id:
        return jsonify({"success": False, "message": "broker and user_id required"}), 400
    
    if broker not in ['kite', 'dhan', 'angel']:
        return jsonify({"success": False, "message": "Invalid broker"}), 400
    
    try:
        if broker == 'kite':
            sess = USER_SESSIONS["kite"].get(user_id)
            if not sess:
                return jsonify({"success": False, "message": "Kite not connected"}), 401
            
            kite = get_kite_for_user(user_id, sess["access_token"])
            return jsonify({
                "success": True,
                "data": {
                    "orders": kite.orders(),
                    "positions": kite.positions(),
                    "trades": kite.trades()
                }
            })
            
        elif broker == 'dhan':
            client, resp, code = _dhan_client_from_session(user_id)
            if client is None:
                return jsonify({"success": False, "message": "Dhan not connected"}), 401
            
            return jsonify({
                "success": True,
                "data": {
                    "orders": client.get_order_list(),
                    "positions": client.get_positions(),
                    "trades": client.get_trade_book() if hasattr(client, "get_trade_book") else []
                }
            })
            
        elif broker == 'angel':
            sess = USER_SESSIONS["angel"].get(user_id)
            if not sess:
                return jsonify({"success": False, "message": "Angel not connected"}), 401
            
            # Get SmartConnect object from separate storage
            smart_api = USER_SESSIONS["angel"].get("_smart_apis", {}).get(user_id)
            if not smart_api:
                return jsonify({"success": False, "message": "SmartAPI object not found"}), 401
            
            # Fetch all data with proper error handling
            try:
                orders_response = smart_api.orderBook()
                positions_response = smart_api.position()
                trades_response = smart_api.tradeBook()
                
                print(f"Angel get-all-data - Orders: {orders_response}")
                print(f"Angel get-all-data - Positions: {positions_response}")
                print(f"Angel get-all-data - Trades: {trades_response}")
                
                # Process orders
                if isinstance(orders_response, dict) and 'data' in orders_response:
                    orders = orders_response['data']
                elif isinstance(orders_response, list):
                    orders = orders_response
                else:
                    orders = []
                
                # Process positions
                if isinstance(positions_response, dict) and 'data' in positions_response:
                    positions = positions_response['data']
                elif isinstance(positions_response, list):
                    positions = positions_response
                else:
                    positions = []
                
                # Process trades
                if isinstance(trades_response, dict) and 'data' in trades_response:
                    trades = trades_response['data']
                elif isinstance(trades_response, list):
                    trades = trades_response
                else:
                    trades = []
                
                print(f"Angel processed data - Orders: {len(orders)}, Positions: {len(positions)}, Trades: {len(trades)}")
                
                return jsonify({
                    "success": True,
                    "data": {
                        "orders": orders,
                        "positions": positions,
                        "trades": trades
                    }
                })
            except Exception as e:
                print(f"Angel get-all-data error: {str(e)}")
                return jsonify({"success": False, "message": f"Angel API error: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@broker_api_bp.route('/check-multi', methods=['GET'])
def api_check_multi_broker_connections():
    """Check all broker connections for a user"""
    user_id = request.args.get('user_id', 'default_user')
    brokers = ['kite', 'dhan', 'angel']
    
    connected_brokers = []
    for broker in brokers:
        if USER_SESSIONS[broker].get(user_id):
            connected_brokers.append({
                'broker': broker,
                'user_id': user_id,
                'status': 'connected'
            })
    
    return jsonify({
        'connected_brokers': connected_brokers,
        'total_connected': len(connected_brokers)
    })

# ===================== SESSION VALIDATION =====================
@multi_broker_bp.route('/validate_session/<broker>/<user_id>')
def validate_session(broker, user_id):
    """Validate if a session is still active"""
    if broker not in ['kite', 'dhan', 'angel'] or not user_id:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    sess = USER_SESSIONS[broker].get(user_id)
    if sess:
        return jsonify({
            'connected': True,
            'broker': broker,
            'user_id': user_id,
            'session_data': sess
        })
    else:
        return jsonify({
            'connected': False,
            'broker': broker,
            'user_id': user_id
        })

@multi_broker_bp.route('/disconnect/<broker>/<user_id>', methods=['POST', 'GET'])
def disconnect_broker_session(broker, user_id):
    """Disconnect from a broker"""
    try:
        # Remove from memory
        if broker in USER_SESSIONS and user_id in USER_SESSIONS[broker]:
            del USER_SESSIONS[broker][user_id]
        
        # Also clean up SmartConnect objects for Angel One
        if broker == 'angel' and "_smart_apis" in USER_SESSIONS["angel"] and user_id in USER_SESSIONS["angel"]["_smart_apis"]:
            del USER_SESSIONS["angel"]["_smart_apis"][user_id]
        
        if request.method == 'GET':
            return redirect('/calculatentrade_journal/real_broker_connect')
        return jsonify({"ok": True, "message": f"Disconnected from {broker.upper()}"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})

@multi_broker_bp.route('/saved_sessions')
def saved_sessions():
    """Display saved broker sessions"""
    try:
        session_data = []
        
        for broker in ['kite', 'dhan', 'angel']:
            for user_id, sess in USER_SESSIONS[broker].items():
                # Skip _smart_apis entries for Angel One
                if broker == 'angel' and user_id == '_smart_apis':
                    continue
                    
                session_info = {
                    'broker': broker,
                    'user_id': user_id,
                    'client_code': sess.get('client_code', sess.get('kite_user_id', 'N/A')),
                    'updated_at': datetime.now(),
                    'expires_at': datetime.now(),
                    'is_active': True
                }
                session_data.append(session_info)
        
        return render_template('saved_sessions.html', sessions=session_data)
    except Exception as e:
        return f"Error loading sessions: {str(e)}", 500

@multi_broker_bp.route('/health')
def health():
    return "ok", 200

@multi_broker_bp.route('/debug/sessions')
def debug_sessions():
    """Debug endpoint to check all active sessions"""
    debug_info = {
        "angel_sessions": {},
        "angel_smart_apis": {}
    }
    
    # Show Angel sessions (without sensitive data)
    for user_id, sess in USER_SESSIONS["angel"].items():
        if user_id != "_smart_apis":
            debug_info["angel_sessions"][user_id] = {
                "has_access_token": bool(sess.get("access_token")),
                "client_code": sess.get("client_code"),
                "connected": sess.get("connected", False),
                "session_keys": list(sess.keys())
            }
    
    # Show SmartAPI objects
    smart_apis = USER_SESSIONS["angel"].get("_smart_apis", {})
    for user_id in smart_apis:
        debug_info["angel_smart_apis"][user_id] = "exists"
    
    return jsonify(debug_info)

# ===================== INTEGRATION FUNCTIONS =====================
def create_multi_broker_blueprint():
    """Create and return the multi-broker blueprint"""
    return multi_broker_bp

def get_broker_session_status(broker, user_id):
    """Get broker session status"""
    if broker not in USER_SESSIONS:
        return {'connected': False, 'error': 'Invalid broker'}
    
    sess = USER_SESSIONS[broker].get(user_id)
    if sess:
        return {
            'connected': True,
            'session_data': sess
        }
    else:
        return {'connected': False}

def save_broker_user_session(broker, user_id, session_data):
    """Save broker user session data"""
    if broker not in USER_SESSIONS:
        return False
    
    USER_SESSIONS[broker][user_id] = session_data
    return True

def integrate_with_calculatentrade(app):
    """Integrate multi-broker system with CalculatenTrade app"""
    app.register_blueprint(multi_broker_bp)
    app.register_blueprint(broker_api_bp)
    print("Multi-broker system integrated with CalculatenTrade")