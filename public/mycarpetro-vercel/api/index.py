import sys
import os
from flask import Flask, jsonify, request

# Sambungan ke folder utama root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

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
    
    # Sini anda boleh panggil fungsi simpan database dari menu_temujanji.py anda
    # Contoh: menu_temujanji.simpan_slot(nama, tarikh, slot)
    
    return jsonify({
        "status": "Success",
        "mesej": f"Slot {slot} pada {tarikh} untuk {nama} berjaya direkodkan!"
    })

# 3. API UNTUK MENU INVOIS & PAYMENT
@app.route('/api/invois', methods=['POST'])
def jana_invois():
    data = request.get_json() or {}
    # Logik ambil data payment dari menu_payment.py anda
    return jsonify({
        "status": "Invois Dijana",
        "no_invois": "INV-2026-001",
        "qr_link": "/qr_bank.jpeg" # Memanggil imej qr dari root anda
    })

# 4. API UNTUK MENU KEWANGAAN
@app.route('/api/kewangan', methods=['GET'])
def dapatkan_data_kewangan():
    # Sini boleh panggil data untung rugi dari menu_kewangan.py anda
    return jsonify({
        "jumlah_pendapatan": 2500.00,
        "jumlah_perbelanjaan": 800.00,
        "untung_bersih": 1700.00
    })

if __name__ == '__main__':
    app.run(debug=True)
