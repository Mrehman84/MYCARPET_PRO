# ==============================================================================
# ⚙️ FAIL KONFIGURASI UTAMA EKOSISTEM PERAKAUNAN MYCARPET PRO
# ==============================================================================
# ⚙️ FAIL KONFIGURASI & SAMBUNGAN UTAMA EKOSISTEM MYCARPET PRO (VERSI VERCEL)
# ==============================================================================
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# 1. Ketetapan Pautan URL & Fail Kunci API
NAMA_FAIL_KUNCI = "mycarpetpro-finance-f1efc8262e3d.json"
URL_FINANCE_SHEET = "https://docs.google.com/spreadsheets/d/1xCSGuFUQjSp33kRSSOJpYP2AIMKdTemg5wWi8jyPm_o/edit?gid=1490732956#gid=1490732956"
URL_OPERASI_SHEET = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=1251116694#gid=1251116694"

def hubung_google_sheets():
    """
    Fungsi Pusat untuk menghubungkan Python ke Google API.
    Boleh berjalan di komputer sendiri (Local) ATAU di pelayan Vercel Cloud secara automatik!
    """
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 🌟 LANGKAH 1: Jika berjalan di Vercel (Menggunakan Environment Variables)
    if os.environ.get("GOOGLE_PRIVATE_KEY") and os.environ.get("GOOGLE_CLIENT_EMAIL"):
        try:
            # Mengambil kunci rahsia dan membetulkan ralat baris baharu '\n'
            kunci_private_mentah = os.environ.get("GOOGLE_PRIVATE_KEY")
            kunci_private_betul = kunci_private_mentah.replace('\\n', '\n')
            
            info_kunci = {
                "type": "service_account",
                "project_id": "mycarpetpro-finance", # ID Projek Google Cloud kamu
                "private_key": kunci_private_betul,
                "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
                "token_uri": "https://googleapis.com"
            }
            
            creds = Credentials.from_service_account_info(info_kunci, scopes=scope)
            return gspread.authorize(creds)
            
        except Exception as e:
            print(f"❌ Ralat pembacaan kunci Vercel: {str(e)}")
            # Jika ralat Vercel gagal, sistem akan cuba cara fail komputer di bawah...
            
    # 🌟 LANGKAH 2: Jika berjalan di Komputer Sendiri (Menggunakan Fail .json)
    if os.path.exists(NAMA_FAIL_KUNCI):
        with open(NAMA_FAIL_KUNCI, 'r') as f:
            info_kunci = json.load(f)
        creds = Credentials.from_service_account_info(info_kunci, scopes=scope)
        return gspread.authorize(creds)
    else:
        raise FileNotFoundError(f"❌ Ralat: Fail kunci {NAMA_FAIL_KUNCI} tidak ditemui di komputer dan tiada tetapan di Vercel!")

