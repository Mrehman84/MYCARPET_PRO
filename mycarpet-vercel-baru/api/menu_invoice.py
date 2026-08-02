from http.server import BaseHTTPRequestHandler
import json
import os
from gspread.utils import convert_gspread_data
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF

# 🚀 Konfigurasi Google Sheets (Gunakan Environment Variables di Vercel)
URL_OPERASI_SHEET = "https://google.com"

def hubung_google():
    scope = ["https://googleapis.com", "https://googleapis.com"]
    # Mengambil kunci dari environment variable Vercel untuk keselamatan
    info_kunci = {
        "type": "service_account",
        "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
        "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
        "token_uri": "https://googleapis.com"
    }
    creds = Credentials.from_service_account_info(info_kunci, scopes=scope)
    return gspread.authorize(creds)

# =====================================================================
# 🎨 REKA BENTUK PDF FPDF (Dikekalkan dari kod asal)
# =====================================================================
def jana_pdf_invois_terkini(data_invois, item_list):
    # Fungsi ini melukis invois (Westberry Enterprise, Logo, Jadual, Sign)
    # Rujuk kod asal untuk detail fungsi fpdf.cell, image, dll.
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    # ... [Logik FPDF sama seperti kod asal 0.1.14] ...
    return pdf.output(dest='S').encode('latin1')

# =====================================================================
# 🌐 SISTEM PENGENDALIAN HTTP VERCEL (Tiada 'st.')
# =====================================================================
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            client = hubung_google()
            sheet = client.open_by_url(URL_OPERASI_SHEET)
            ws_tempahan = sheet.worksheet("Tempahan")
            
            # Ambil data untuk dropdown/cetak
            data_tempahan = ws_tempahan.get_all_records()
            pilihan_options = [f"{t['INV NO']} | {t['CUSTOMER ID']}" for t in data_tempahan if t.get("INV NO")]
            
            self.wfile.write(json.dumps({"status": "berjaya", "pilihan": pilihan_options}).encode('utf-8'))
            
        except Exception as e:
            self.wfile.write(json.dumps({"status": "gagal", "mesej": str(e)}).encode('utf-8'))
        return
