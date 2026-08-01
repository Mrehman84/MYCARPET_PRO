import sys 
import os 
import re
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Membenarkan komunikasi dengan public/index.html

# --- LOGIK ASAL ANDA (DIPINDAHKAN DARI STREAMLIT KE FLASK) ---
def kira_kos_karpet_asal(kod_karpet):
    kod = str(kod_karpet).strip().upper()
    
    # 1. Peta darab asal abang
    peta_darab = {
        "CSG": 1.30,
        "CK": 1.20,
        "CN": 0.50,
        "CS": 0.50,
        "HP": 1.30,
        "LP": 1.00
    }
    
    # 2. Cari nilai darab mengikut prefix
    nilai_darab_semasa = 1.00
    for prefix, nilai in peta_darab.items():
        if kod.startswith(prefix):
            nilai_darab_semasa = nilai
            break
            
    # 3. Logik ekstrak saiz pintar menggunakan REGEX asal abang
    luas_sqft = 0.0
    try:
        padanan = re.search(r'(\d+)\s*X\s*(\d+)', kod)
        if padanan:
            lebar = float(padanan.group(1))
            panjang = float(padanan.group(2))
            luas_sqft = lebar * panjang
        else:
            luas_sqft = 24.0 if kod == "TEBAL" else 0.0
    except:
        luas_sqft = 0.0
        
    harga_kiraan_final = luas_sqft * nilai_darab_semasa
    return harga_kiraan_final

# --- ENDPOINT API UNTUK FRONTEND ---
@app.route('/api/kira', methods=['POST'])
def proses_kira_harga():
    data = request.get_json() or {}
    
    # Mengambil kod karpet yang dihantar oleh borang HTML (Contoh: "CK 5X7")
    kod_karpet = data.get('kod_karpet', '').strip().upper()
    kuantiti = int(data.get('kuantiti', 1))
    
    if not kod_karpet:
        return jsonify({"error": "Kod karpet tidak disediakan"}), 400
        
    # Jalankan formula asal anda
    harga_seunit = kira_kos_karpet_asal(kod_karpet)
    total_harga = harga_seunit * kuantiti
    
    return jsonify({
        "status": "success",
        "kod": kod_karpet,
        "harga_seunit": harga_seunit,
        "kuantiti": kuantiti,
        "total": total_harga
    })

@app.route('/api', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "Logik Formula Karpet sedia digunakan!"})
