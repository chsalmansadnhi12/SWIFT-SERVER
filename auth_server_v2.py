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
    "latest_version": "7.0.1",
    "update_url": "https://swifftbanksoftwares.com/downloads/update_latest.exe",
    "changelog": "Enterprise Edition 7.0.1 - Security & Performance Upgrade"
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

# --- Default Hardcoded Licenses (REMOVED as per request) ---
DEFAULT_LICENSES = {} 

# Merge defaults if not present
for k, v in DEFAULT_LICENSES.items():
    if k not in LICENSES:
        LICENSES[k] = v

# --- Routes ---

@app.route('/')
def home():
    return jsonify({"status": "ONLINE", "server": "SWIFT-AUTH-NODE-V2", "version": "2.0.0"})

@app.route('/verify', methods=['POST'])
def verify_license():
    """Endpoint for the main application to verify a license (Smart Check)"""
    data = request.json
    
    # Inputs from client (might be swapped or mixed)
    input_1 = data.get('license_key', '').strip()
    input_2 = data.get('email', '').strip() # This is the "Registration ID" field in UI
    hwid = data.get('hw_id')
    
    if not hwid:
        return jsonify({"valid": False, "message": "Missing HWID"}), 400
        
    # --- SMART LOOKUP LOGIC ---
    # We want to find a valid license entry that matches EITHER input_1 or input_2
    
    found_key = None
    
    # Check 1: Is input_1 a valid License Key?
    if input_1 in LICENSES:
        found_key = input_1
    # Check 2: Is input_2 a valid License Key?
    elif input_2 in LICENSES:
        found_key = input_2
        
    if not found_key:
        return jsonify({"valid": False, "message": "Invalid License Key or Registration ID"}), 401
        
    license_data = LICENSES[found_key]
    
    # --- CHECK PAIRING ---
    # If this license is linked to a Registration ID, verify the OTHER input matches it
    linked_reg = license_data.get('linked_reg_id')
    linked_lic = license_data.get('linked_license')
    
    # Identify which input was the key we found, and which is the 'other' one provided
    other_input = input_2 if found_key == input_1 else input_1
    
    # Case A: found_key is the Main License Key
    if linked_reg:
        if linked_reg != other_input:
             return jsonify({"valid": False, "message": "Registration ID does not match License Key"}), 401

    # Case B: found_key is the Registration ID (treated as a license entry)
    if linked_lic:
        if linked_lic != other_input:
             return jsonify({"valid": False, "message": "License Key does not match Registration ID"}), 401

    # --- STATUS CHECKS ---
    if license_data['status'] != 'ACTIVE':
        return jsonify({"valid": False, "message": f"License is {license_data['status']}"}), 403
        
    # --- HWID LOCKING ---
    # Lock BOTH the License Key AND the Registration ID entry to the same HWID
    
    # Update current found entry
    if license_data['hwid'] is None:
        license_data['hwid'] = hwid
        logging.info(f"License {found_key} locked to HWID: {hwid}")
        save_data() 
    elif license_data['hwid'] != hwid:
        return jsonify({"valid": False, "message": "License locked to another device"}), 403
        
    # Also update the linked entry (to keep them in sync)
    linked_key = linked_reg or linked_lic
    if linked_key and linked_key in LICENSES:
        if LICENSES[linked_key]['hwid'] is None:
            LICENSES[linked_key]['hwid'] = hwid
            save_data()
        elif LICENSES[linked_key]['hwid'] != hwid:
             return jsonify({"valid": False, "message": "Linked credential locked to another device"}), 403

    # --- EXPIRY CHECK ---
    expiry_date = datetime.strptime(license_data['expiry'], "%Y-%m-%d")
    if datetime.now() > expiry_date:
        license_data['status'] = "EXPIRED"
        save_data()
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
    """Generate a new license key AND a matching Registration ID"""
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != ADMIN_KEY:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    license_type = data.get('type', 'PRO')
    days = data.get('days', 365)
    
    # Custom inputs
    custom_lic = data.get('custom_key')
    custom_reg = data.get('custom_reg')
    
    # Generate License Key if not provided
    if custom_lic:
        new_lic_key = custom_lic
    else:
        new_lic_key = f"SWIFT-{uuid.uuid4().hex[:8].upper()}-{datetime.now().year}"
        
    # Generate Registration ID if not provided
    if custom_reg:
        new_reg_id = custom_reg
    else:
        new_reg_id = f"REG-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
        
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Store BOTH as separate entries but linked by logic (or just store both as valid)
    # Storing License
    LICENSES[new_lic_key] = {
        "status": "ACTIVE",
        "expiry": expiry,
        "hwid": None,
        "type": license_type,
        "linked_reg_id": new_reg_id  # Link them for reference
    }
    
    # Storing Registration ID (as a type of license, or just valid entry)
    LICENSES[new_reg_id] = {
        "status": "ACTIVE",
        "expiry": expiry,
        "hwid": None,
        "type": "REGISTRATION",
        "linked_license": new_lic_key
    }
    
    save_data() # Save new data
    return jsonify({
        "success": True, 
        "license_key": new_lic_key, 
        "registration_id": new_reg_id,
        "expiry": expiry
    })

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
