import sys
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials

# 1. Ketuk dinding folder supaya Python boleh nampak fail config.py di luar folder api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 2. Hidupkan aplikasi FastAPI (Otak Backend Vercel)
app = FastAPI()

# Benarkan frontend HTML bersembang dengan backend Python ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Fungsi khas untuk masuk ke Google Sheets guna kod rahsia
def sambung_google_sheets():
    # Ambil data JSON rahsia dari Environment Variable Vercel
    info_kunci = os.environ.get("GOOGLE_CREDENTIALS")
    if not info_kunci:
        return None
        
    skop_akses = [
        "https://google.com",
        "https://googleapis.com"
    ]
    
    kunci_json = json.loads(info_kunci)
    
    # KOD RAHSIA PENYELAMAT: Membetulkan ralat \n yang tersilap ditukar oleh Vercel
    if "private_key" in kunci_json:
        kunci_json["private_key"] = kunci_json["private_key"].replace("\\n", "\n")
        
    kredential = Credentials.from_service_account_info(kunci_json, scopes=skop_akses)
    client = gspread.authorize(kredential)
    return client


# 4. Jalan pintas (API Route) untuk ambil data pelanggan bagi Invois
@app.get("/api/pelanggan")
def ambil_senarai_pelanggan():
    try:
        client = sambung_google_sheets()
        if not client:
            return {"status": "ralat", "mesej": "Kunci GOOGLE_CREDENTIALS tidak dijumpai di Vercel!"}
            
        # Membuka Google Sheets menggunakan pautan URL atau Nama yang ada di dalam fail config.py kamu
        # Di bawah ini adalah contoh jika fail config kamu menggunakan pautan URL (contoh: SHEET_URL atau SPREADSHEET_URL)
        if hasattr(config, 'SHEET_URL'):
            buku_data = client.open_by_url(config.SHEET_URL)
        elif hasattr(config, 'SPREADSHEET_URL'):
            buku_data = client.open_by_url(config.SPREADSHEET_URL)
        elif hasattr(config, 'SPREADSHEET_NAME'):
            buku_data = client.open(config.SPREADSHEET_NAME)
        else:
            # Jika nama pembolehubah dalam config kamu berbeza, ia akan cuba buka mengikut nama fail asal
            buku_data = client.open("MYCARPET_PRO_DATA")
            
        # Ambil helaian pertama (sheet pertama tempat simpan data tempahan karpet)
        helaian_tempahan = buku_data.get_worksheet(0) 
        
        # Ambil semua data tempahan karpet
        semua_data = helaian_tempahan.get_all_records()
        
        # Ekstrak nama pelanggan atau no invois sahaja untuk dipaparkan pada menu phone
        senarai_nama = [rekod.get("Nama Pelanggan", "Tiada Nama") for rekod in semua_data if rekod.get("Nama Pelanggan")]
        
        return {"status": "berjaya", "data": senarai_nama}
        
    except Exception as ralat:
        return {"status": "ralat", "mesej": str(ralat)}
