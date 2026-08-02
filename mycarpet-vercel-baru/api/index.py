import sys
import os
import json
import os
import json
import base64
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

def sambung_google_sheets():
    skop_akses = [
        "https://google.com",
        "https://googleapis.com"
    ]
    
    # 🌟 CARA KALIS RALAT: Membaca terus kunci daripada tetapan fail config kamu!
    # Sila pastikan fail config.py kamu mengandungi maklumat kunci yang betul.
    try:
        # Jika config kamu menggunakan fail JSON luaran:
        kredential = Credentials.from_service_account_file("config.py", scopes=skop_akses)
    except Exception:
        # Jika config kamu menyimpan json_info di dalam pembolehubah:
        if hasattr(config, 'json_info'):
            kredential = Credentials.from_service_account_info(config.json_info, scopes=skop_akses)
        else:
            return None
            
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
        helaian_tempahan = buku_data.worksheet("Tempahan")

        
        # Ambil semua data tempahan karpet
        semua_data = helaian_tempahan.get_all_records()
        
        # Ekstrak nama pelanggan atau no invois sahaja untuk dipaparkan pada menu phone
        senarai_nama = [rekod.get("Nama Pelanggan", "Tiada Nama") for rekod in semua_data if rekod.get("Nama Pelanggan")]
        
        return {"status": "berjaya", "data": senarai_nama}
        
    except Exception as ralat:
        return {"status": "ralat", "mesej": str(ralat)}


@app.get("/api/dashboard")
def ambil_data_dashboard():
    try:
        client = sambung_google_sheets()
        if not client:
            return {"status": "ralat", "mesej": "Kunci GOOGLE_CREDENTIALS tidak dijumpai!"}
            
        # Membuka Google Sheets menggunakan config
        if hasattr(config, 'SHEET_URL'):
            buku_data = client.open_by_url(config.SHEET_URL)
        elif hasattr(config, 'SPREADSHEET_URL'):
            buku_data = client.open_by_url(config.SPREADSHEET_URL)
        else:
            buku_data = client.open("MYCARPET_PRO_DATA")
            
        helaian_tempahan = buku_data.get_worksheet(0) 
        semua_data = helaian_tempahan.get_all_records()
        
        # 1. Hitung Status Operasi Karpet Semasa
        dalam_proses = 0
        pengeringan = 0
        ready_deliver = 0
        selesai = 0
        
        for rekod in semua_data:
            # Ganti kata "Status" di bawah sesuai dengan nama kolom status di Google Sheets kamu
            status_karpet = str(rekod.get("Status", "")).lower()
            if "proses" in status_karpet:
                dalam_proses += 1
            elif "pengeringan" in status_karpet or "kering" in status_karpet:
                pengeringan += 1
            elif "ready" in status_karpet or "hantar" in status_karpet:
                ready_deliver += 1
            elif "selesai" in status_karpet or "hantar" in status_karpet:

                selesai += 1
                
        # 2. Ringkasan Basuhan Karpet
        total_pelanggan = len(semua_data)
        
        return {
            "status": "berjaya",
            "dalam_proses": dalam_proses,
            "pengeringan": pengeringan,
            "ready_deliver": ready_deliver,
            "selesai": selesai,
            "sepanjang_waktu": total_pelanggan
        }
    except Exception as ralat:
        return {"status": "ralat", "mesej": str(ralat)}
