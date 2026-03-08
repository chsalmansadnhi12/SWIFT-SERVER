from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid
import logging
import json
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
ADMIN_KEY = "ADMIN-MASTER-KEY-2024"  # Key for the Admin Panel to connect
PORT = 5000
DATA_FILE = "server_data.json"

# --- Persistence Functions ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
    return None

def save_data():
    data = {
        "config": SERVER_CONFIG,
        "licenses": LICENSES
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save data: {e}")

# --- Server State (In-Memory) ---
SERVER_CONFIG = {
    "latest_version": "2.0.0",
    "update_url": "https://swifftbanksoftwares.com/downloads/update_latest.exe",
    "changelog": "Initial Release"
}

# --- Database (In-Memory for this version, can be upgraded to SQLite/MySQL) ---
# Format: {license_key: {"status": "ACTIVE", "expiry": "YYYY-MM-DD", "hwid": None, "type": "PRO"}}
LICENSES = {
    # Pre-populated with user provided keys
    "SWIFT-PRO-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    # ... (other default licenses will be merged/overwritten by load_data)
}

# Load saved data on startup
saved_data = load_data()
if saved_data:
    if "config" in saved_data:
        SERVER_CONFIG.update(saved_data["config"])
    if "licenses" in saved_data:
        LICENSES.update(saved_data["licenses"])

    "SWIFT-PRO-V5": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "MARGIN-WIRE-FLASHER": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "FLASHER"},
    "SWIFT-MARGIN-WIRE-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "UBS-VISA-NET-CRYPTO": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "CRYPTO"},
    "UBS-SWIFT-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "ADMIN-LICENSE": {"status": "ACTIVE", "expiry": "2030-12-31", "hwid": None, "type": "ADMIN"},
    "FLASHING-LICENSE": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "FLASHER"},
    "UBS-VISA-NET-SWIFT-CRYPTO-HOST": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "HOST"},
    "SWIFT-PRO-2024-X": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "SWIFT-2024-PRO-V5": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "SWIFT-UBS-VISA-NET-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "SWIFT-UBS-VISA-NET-PRO": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "SWIFT-UBS-VISA-NET-V5": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "MARGIN-FLASHER-PRO": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "FLASHER"},
    "SWIFT-TERMINAL-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "TERMINAL"},
    "UBS-LICENSE-KEY": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "PRO"},
    "SWIFT-UBS-VISA-NET-CRYPTO-HOST": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "HOST"},
    "UBS-VISA-NET-SWIFT-CRYPTO-HOST-SOFTWARE": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "HOST"},
    
    # Registration Keys
    "REG-1234-5678": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-ADMIN-001": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "ADMIN"},
    "REG-MARGIN-WIRE": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-SWIFT-PRO": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-UBS-VISA-NET": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-UBS-SWIFT-2024": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-2024-SWIFT": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-8888-9999": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-5555-6666": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-0000-1111": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-1111-2222": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-3333-4444": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-MARGIN-FLASHER": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
    "REG-SWIFT-TERMINAL": {"status": "ACTIVE", "expiry": "2025-12-31", "hwid": None, "type": "REG"},
}

# --- Routes ---

@app.route('/')
def home():
    return jsonify({"status": "ONLINE", "server": "SWIFT-AUTH-NODE-V2", "version": "2.0.0"})

@app.route('/verify', methods=['POST'])
def verify_license():
    """Endpoint for the main application to verify a license"""
    data = request.json
    key = data.get('license_key')
    hwid = data.get('hw_id')
    email = data.get('email')
    
    if not key or not hwid:
        return jsonify({"valid": False, "message": "Missing credentials"}), 400
        
    license_data = LICENSES.get(key)
    
    if not license_data:
        return jsonify({"valid": False, "message": "Invalid License Key"}), 401
        
    if license_data['status'] != 'ACTIVE':
        return jsonify({"valid": False, "message": f"License is {license_data['status']}"}), 403
        
    # HWID Locking Logic
    if license_data['hwid'] is None:
        # First time use - lock to this HWID
        license_data['hwid'] = hwid
        logging.info(f"License {key} locked to HWID: {hwid}")
        save_data() # Save changes
    elif license_data['hwid'] != hwid:
        return jsonify({"valid": False, "message": "License locked to another device"}), 403

    # Email Locking Logic (New)
    current_email_lock = license_data.get('email')
    if current_email_lock is None and email:
        license_data['email'] = email
        logging.info(f"License {key} locked to Email: {email}")
        save_data() # Save changes
    elif current_email_lock and email and current_email_lock != email:
        return jsonify({"valid": False, "message": "License locked to another email address"}), 403
        
    # Expiry Check
    expiry_date = datetime.strptime(license_data['expiry'], "%Y-%m-%d")
    if datetime.now() > expiry_date:
        license_data['status'] = "EXPIRED"
        return jsonify({"valid": False, "message": "License Expired"}), 403
        
    return jsonify({
        "valid": True, 
        "message": "Access Granted", 
        "type": license_data['type'],
        "expiry": license_data['expiry']
    })

@app.route('/update/check', methods=['GET'])
def check_update():
    """Check for latest version"""
    return jsonify({
        "version": SERVER_CONFIG["latest_version"],
        "url": SERVER_CONFIG["update_url"],
        "changelog": SERVER_CONFIG["changelog"]
    })

@app.route('/admin/update_config', methods=['POST'])
def update_config():
    """Update server configuration (version, url, etc.)"""
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    if 'version' in data:
        SERVER_CONFIG['latest_version'] = data['version']
    if 'url' in data:
        SERVER_CONFIG['update_url'] = data['url']
    if 'changelog' in data:
        SERVER_CONFIG['changelog'] = data['changelog']
        
    save_data() # Save configuration
    return jsonify({"success": True, "message": "Server configuration updated", "config": SERVER_CONFIG})

# --- Admin Routes (Protected) ---

@app.route('/admin/generate', methods=['POST'])
def generate_license():
    """Generate a new license key"""
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    license_type = data.get('type', 'PRO')
    days = data.get('days', 365)
    custom_key = data.get('custom_key')
    
    if custom_key:
        new_key = custom_key
    else:
        new_key = f"SWIFT-{uuid.uuid4().hex[:8].upper()}-{datetime.now().year}"
        
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    LICENSES[new_key] = {
        "status": "ACTIVE",
        "expiry": expiry,
        "hwid": None,
        "type": license_type
    }
    
    save_data() # Save new license
    return jsonify({"success": True, "key": new_key, "expiry": expiry})

@app.route('/admin/list', methods=['POST'])
def list_licenses():
    """List all licenses"""
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    return jsonify({"success": True, "licenses": LICENSES})

@app.route('/admin/disable', methods=['POST'])
def disable_license():
    """Disable/Ban a license"""
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    key = data.get('key')
    if key in LICENSES:
        LICENSES[key]['status'] = "BANNED"
        save_data()
        return jsonify({"success": True, "message": f"License {key} banned"})
    return jsonify({"success": False, "message": "License not found"})

@app.route('/admin/reset_hwid', methods=['POST'])
def reset_hwid():
    """Reset HWID lock for a license"""
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    key = data.get('key')
    if key in LICENSES:
        LICENSES[key]['hwid'] = None
        save_data()
        return jsonify({"success": True, "message": f"HWID reset for {key}"})
    return jsonify({"success": False, "message": "License not found"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000)) # Use Render's PORT or default to 5000
    print(f"[*] SWIFT Auth Server v2.0 Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
