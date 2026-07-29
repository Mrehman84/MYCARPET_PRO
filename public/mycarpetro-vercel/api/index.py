import sys
import os
from flask import Flask, jsonify, request

# Mengarah Python untuk keluar 2 tingkat ke folder Root utama
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    import menu_harga
    import menu_payment
    import menu_temujanji
except ImportError:
    menu_harga = None
    menu_payment = None
    menu_temujanji = None

app = Flask(__name__)

@app.route('/api/status', methods=['GET'])
def semak_status():
    return jsonify({
        "status": "Sistem MYCARPET PRO Aktif",
        "mesej": "Hubungan Backend Python Berjaya!"
    })

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

if __name__ == '__main__':
    app.run(debug=True)
