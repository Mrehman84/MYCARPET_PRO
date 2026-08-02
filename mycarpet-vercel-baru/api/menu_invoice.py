from http.server import BaseHTTPRequestHandler
import json
import os
import gspread
from google.oauth2.service_account import Credentials

# 🚀 LINK GOOGLE SHEETS OPERASI KAMU
URL_OPERASI_SHEET = "https://google.com"

def hubung_google():
    scope = ["https://googleapis.com", "https://googleapis.com"]
    kunci_raw = os.environ.get("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n')
    info_kunci = {
        "type": "service_account",
        "project_id": "mycarpetpro-finance",
        "private_key": kunci_raw,
        "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL", ""),
        "token_uri": "https://googleapis.com"
    }
    creds = Credentials.from_service_account_info(info_kunci, scopes=scope)
    return gspread.authorize(creds)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Isyarat selamat (CORS) supaya frontend boleh baca data tanpa ralat
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            client = hubung_google()
            sheet = client.open_by_url(URL_OPERASI_SHEET)
            
            # Membuka tab "Tempahan" dan "Pelanggan"
            ws_tempahan = sheet.worksheet("Tempahan")
            ws_pelanggan = sheet.worksheet("Pelanggan")
            
            data_tempahan = ws_tempahan.get_all_records()
            data_pelanggan = ws_pelanggan.get_all_records()
            
            pilihan_options = []
            
            # Buat kamus alamat pelanggan
            pemetaan_alamat = {}
            for p in data_pelanggan:
                c_id = str(p.get("CUSTOMER ID", p.get("CUSTOMER_ID", ""))).strip().upper()
                alamat = str(p.get("ALAMAT", "")).strip()
                if c_id:
                    pemetaan_alamat[c_id] = alamat
            
            # Cantumkan No Invois + Alamat untuk kegunaan dropdown web kamu
            for t in data_tempahan:
                inv_no = str(t.get("INV NO", t.get("INV_NO", ""))).strip()
                cust_id = str(t.get("CUSTOMER ID", t.get("CUSTOMER_ID", ""))).strip().upper()
                if inv_no:
                    alamat_padan = pemetaan_alamat.get(cust_id, "-")
                    pilihan_options.append(f"{inv_no} | {alamat_padan}")
            
            # Hantar senarai data yang bersih balik ke web kamu!
            self.wfile.write(json.dumps({"status": "berjaya", "pilihan": pilihan_options}).encode('utf-8'))
            
        except Exception as e:
            # Jika Google Sheets menyekat, ralat sebenar dihantar ke web
            self.wfile.write(json.dumps({"status": "gagal", "mesej": str(e)}).encode('utf-8'))
        return
