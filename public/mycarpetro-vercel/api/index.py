import sys 
import os 
from flask import Flask, jsonify, request
from flask_cors import CORS  # Membenarkan frontend akses API ini

# Memastikan path ke folder utama root adalah tepat di server Vercel
# api/index.py berada 1 tingkat di bawah root, jadi kita undur 1 tingkat sahaja
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import menu_harga 
    import menu_payment 
    import menu_temujanji 
    import menu_kewangan
except ImportError:
    menu_harga = None
    menu_payment = None
    menu_temujanji = None
    menu_kewangan = None

app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk seluruh aplikasi

# Root Endpoint untuk semakan status
@app.route('/api', methods=['GET'])
def home():
    return jsonify({
        "status": "online", 
        "project": "MYCARPET PRO Backend",
        "modules_loaded": {
            "menu_harga": menu_harga is not None,
            "menu_payment": menu_payment is not None,
            "menu_temujanji": menu_temujanji is not None,
            "menu_kewangan": menu_kewangan is not None
        }
    })

# 1. API UNTUK MENU HARGA
@app.route('/api/kira', methods=['POST'])
def proses_kira_harga():
    data = request.get_json() or {}
    saiz = data.get('saiz', 'M')
    kuantiti = int(data.get('kuantiti', 1))
    
    if menu_harga and hasattr(menu_harga, 'kira_kos'):
        total_harga = menu_harga.kira_kos(saiz, kuantiti)
    else:
        kadar = {"S": 15, "M": 35, "L": 55}
        total_harga = kadar.get(saiz, 35) * kuantiti
        
    return jsonify({"total": total_harga})

# 2. API UNTUK MENU TEMUJANJI
@app.route('/api/temujanji', methods=['POST'])
def proses_temujanji():
    data = request.get_json() or {}
    nama = data.get('nama', '')
    tarikh = data.get('tarikh', '')
    slot = data.get('slot', '')
    
    return jsonify({
        "status": "Success",
        "mesej": f"Slot {slot} pada {tarikh} untuk {nama} berjaya direkodkan!"
    })

# 3. API UNTUK MENU INVOIS & PAYMENT
@app.route('/api/invois', methods=['POST'])
def jana_invois():
    data = request.get_json() or {}
    return jsonify({
        "status": "Invois Dijana",
        "no_invois": "INV-2026-001",
        "qr_link": "/qr_bank.jpeg" 
    })

# 4. API UNTUK MENU KEWANGAAN
@app.route('/api/kewangan', methods=['GET'])
def dapatkan_data_kewangan():
    return jsonify({
        "jumlah_pendapatan": 2500.00,
        "jumlah_perbelanjaan": 800.00,
        "untung_bersih": 1700.00
    })

# NOTA VERCEL: Buang app.run() supaya fungsi serverless berjalan lancar
