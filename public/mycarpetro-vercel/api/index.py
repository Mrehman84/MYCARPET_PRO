import sys
import os
from flask import Flask, jsonify, request

# Logik Penting: Benarkan Vercel membaca fail Python asal anda yang berada di folder root luar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    # Mengimport fail-fail Python asal anda yang ada di luar
    import menu_harga
    import menu_payment
    import menu_temujanji
except ImportError as e:
    # Fail pelindung jika import gagal semasa awal setup
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
    
    # Membaca input dari borang HTML
    saiz = data.get('saiz', 'M')
    kuantiti = int(data.get('kuantiti', 1))
    
    # 1. JALAN PYTHON ASAL (Jika fail menu_harga anda ada fungsi bernama 'kira_kos')
    if menu_harga and hasattr(menu_harga, 'kira_kos'):
        total_harga = menu_harga.kira_kos(saiz, kuantiti)
    else:
        # 2. JALAN KESELAMATAN (Kira guna kod sandaran jika fail luar belum disambung penuh)
        kadar = {"S": 15, "M": 35, "L": 55}
        total_harga = kadar.get(saiz, 35) * kuantiti
        
    return jsonify({"total": total_harga})

@app.route('/api/bayar', methods=['POST'])
def proses_bayaran():
    # Menghubungkan logik dari menu_payment.py anda pada masa hadapan
    return jsonify({"status": "Invois Sedia", "pautan": "Guna QR Bank"})

# Keperluan Vercel Serverless
if __name__ == '__main__':
    app.run(debug=True)
