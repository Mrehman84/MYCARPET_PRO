from http.server import BaseHTTPRequestHandler
import json
import os
import traceback  # 🔍 Modul khas untuk mengintai ralat komputer
import gspread
from google.oauth2.service_account import Credentials

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
        # Mengaktifkan mod teks biasa supaya ralat Python boleh dicetak terus ke skrin web
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # 🕵️‍♂️ LANGKAH UJIAN 1: Cuba hubung ke Google
            client = hubung_google()
            sheet = client.open_by_url(URL_OPERASI_SHEET)
            
            # 🕵️‍♂️ LANGKAH UJIAN 2: Cuba buka tab lembaran kerja
            ws_tempahan = sheet.worksheet("Tempahan")
            data_tempahan = ws_tempahan.get_all_records()
            
            # Jika kod berjaya tanpa ralat, ia akan tulis ini:
            laporan = "✅ TAHNIAH: Backend Python Berjaya Berhubung Dengan Google Sheets!\n"
            laporan += f"Jumlah rekod dijumpai: {len(data_tempahan)} baris."
            self.wfile.write(laporan.encode('utf-8'))
            
        except Exception as e:
            # 🚨 JIKA GAGAL, KOD INI AKAN MENANGKAP PUNCA UTAMA DAN MENULISNYA DI SKRIN
            laporan_ralat = "❌ DETEKTIF BACKEND: MENANGKAP RALAT PYTHON\n"
            laporan_ralat += f"Mesej Masalah: {str(e)}\n\n"
            laporan_ralat += "--- LAPORAN KEROSAKAN PENH (TRACEBACK) ---\n"
            laporan_ralat += traceback.format_exc()  # Ini fungsi cetak baris rosak
            
            self.wfile.write(laporan_ralat.encode('utf-8'))
        return
