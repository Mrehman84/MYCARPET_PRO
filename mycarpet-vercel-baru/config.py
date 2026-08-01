# ==============================================================================
# ⚙️ FAIL KONFIGURASI UTAMA EKOSISTEM PERAKAUNAN MYCARPET PRO
# ==============================================================================
# ==============================================================================
# ⚙️ FAIL KONFIGURASI & SAMBUNGAN UTAMA EKOSISTEM MYCARPET PRO
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
    Fungsi Pusat untuk menghubungkan Python ke Google API (Mod Teks Murni Windows).
    Fungsi ini dipanggil oleh mana-mana fail skrip perisian anda.
    """
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    if os.path.exists(NAMA_FAIL_KUNCI):
        with open(NAMA_FAIL_KUNCI, 'r') as f:
            info_kunci = json.load(f)
        creds = Credentials.from_service_account_info(info_kunci, scopes=scope)
    else:
        raise FileNotFoundError(f"❌ Ralat: Fail kunci {NAMA_FAIL_KUNCI} tidak ditemui!")
        
    return gspread.authorize(creds)

# 1. Nama Fail Kunci Rahsia Google Cloud API
NAMA_FAIL_KUNCI = "mycarpetpro-finance-f1efc8262e3d.json"


