import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


def proses_migrasi_data_sejarah():
    """
    Fungsi khas sekali guna untuk membersihkan tab Raw_Revenue yang salah susun
    dan memindahkan data dari Sheet Lama (Tab Payment) ke Sheet Baru dengan format Lejar Penuh.
    """
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # 1. Buka kedua-dua Google Sheet
        sheet_lama = client.open_by_url("https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit")
        sheet_baru = client.open_by_url("https://docs.google.com/spreadsheets/d/1xCSGuFUQjSp33kRSSOJpYP2AIMKdTemg5wWi8jyPm_o/edit")
        
        tab_payment_lama = sheet_lama.worksheet("Payment")
        tab_revenue_baru = sheet_baru.worksheet("Raw_Revenue")
        
        # 2. Bersihkan sepenuhnya data salah susun lama di tab Raw_Revenue
        tab_revenue_baru.clear()
        
        # 3. Tulis semula baris tajuk (Header) Lejar yang betul
        headers = ["NO", "TARIKH", "ID_INVOIS", "PELANGGAN", "SALURAN_MASUK", "KATEGORI_SERVIS", "AMOUNT", "CATATAN", "GABUNGAN"]
        tab_revenue_baru.append_row(headers)
        
        # 4. Ambil semua data jualan lama
        data_lama = tab_payment_lama.get_all_records()
        
        baris_migrasi = []
        next_id = 1
        
        for row in data_lama:
            # Ambil nilai asal daripada header sheet lama anda
            id_inv = str(row.get("INV NO", "") or row.get("INV_NO", ""))
            nama = str(row.get("NAMA", "") or "-")
            kaedah = str(row.get("KAEDAH PEMBAYARAN", "") or row.get("KAEDAH_PEMBAYARAN", "")).upper()
            status_bayar = str(row.get("BAYARAN", "") or "PAID").upper()
            
            # Ambil nilai amaun yang betul-betul dibayar (bukan jumlah kasar invois)
            amount = row.get("AMAUN DIBAYAR", 0.0) or row.get("AMAUN_DIBAYAR", 0.0)
            try:
                amount_float = float(amount)
            except:
                amount_float = 0.0
                
            if amount_float <= 0:
                continue # Langgar jika tiada aliran wang tunai masuk sebenar
                
            # Pemetaan Saluran Bank mengikut keputusan anda
            if "TUNAI" in kaedah or "CASH" in kaedah:
                saluran_bersih = "TUNAI"
            else:
                saluran_bersih = "MAYBANK" # Semua QR PAY & TRANSFER BANK dipetakan ke MAYBANK
                
            # Pemprosesan Tarikh (Mengendalikan format timestamp 'YYYY-MM-DD HH:MM:SS')
            tarikh_mentah = str(row.get("TARIKH BAYARAN", "") or row.get("TARIKH_BAYARAN", ""))
            try:
                # Ambil bahagian tarikh sahaja (YYYY-MM-DD)
                tarikh_bersih = tarikh_mentah.split()[0]
                dt_obj = datetime.strptime(tarikh_bersih, "%Y-%m-%d")
                tarikh_paparan = dt_obj.strftime("%d/%m/%Y")
                bulan_tahun_str = dt_obj.strftime("%b%Y") # Hasil cth: Jul2026
            except:
                # Jika format tarikh tersilap, gunakan tarikh hari ini sebagai sandaran
                dt_obj = datetime.now()
                tarikh_paparan = dt_obj.strftime("%d/%m/%Y")
                bulan_tahun_str = dt_obj.strftime("%b%Y")
                
            # Penjanaan Kod Gabungan Lejar Automatik (cth: MAYBANKJul2026 atau TUNAIJul2026)
            kod_gabungan = f"{saluran_bersih}{bulan_tahun_str}"
            catatan_lejar = f"Migrasi Data Sejarah ({status_bayar}) - Invois {id_inv}"
            
            # Susun baris data lejar baru mengikut susunan A hingga I
            baris_lejar = [
                next_id,
                tarikh_paparan,
                id_inv,
                nama,
                saluran_bersih,
                "CUCI KARPET",
                amount_float,
                catatan_lejar,
                kod_gabungan
            ]
            baris_migrasi.append(baris_lejar)
            next_id += 1
            
        # 5. Masukkan semua kumpulan data secara pukal (Bulk insert) supaya laju
        if baris_migrasi:
            tab_revenue_baru.append_rows(baris_migrasi)
        return True, len(baris_migrasi)
    except Exception as e:
        return False, str(e)

def get_gsheet_client():
    # Mengambil kredensial Google API daripada streamlit secrets
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

def app():
    # UI Mobile-First: Dioptimumkan menegak untuk telefon Android
    st.title("📊 Lejar Kewangan My Carpet Pro")
    st.markdown("---")
    
    try:
        client = get_gsheet_client()
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xCSGuFUQjSp33kRSSOJpYP2AIMKdTemg5wWi8jyPm_o/edit?gid=314909126#gid=314909126")
        
        tetapan_sheet = sheet.worksheet("Tetapan_Sistem")
        data_tetapan = tetapan_sheet.get_all_records()
        df_tetapan = pd.DataFrame(data_tetapan)
        
        senarai_bank = [x for x in df_tetapan["Akaun_Bank"].tolist() if x]
        senarai_belanja = [x for x in df_tetapan["Kod_Belanja"].tolist() if x]
        
    except Exception as e:
        st.error(f"Gagal menyambung ke Google Sheet: {e}")
        return

    st.subheader("Borang Kemasukan Lejar Perbelanjaan")
    
    # 📱 INPUT FORM MENEGAK (MESRA ANDROID)
    tarikh = st.date_input("1. Tarikh Perbelanjaan", datetime.now())
    akaun_pilihan = st.selectbox("2. Bayar Melalui (Akaun Dipotong)", senarai_bank)
    kod_pilihan = st.selectbox("3. Kod Perbelanjaan Standard", senarai_belanja)
    butiran = st.text_input("4. Butiran Ringkas Perbelanjaan", placeholder="cth: Beli sabun carpet bulu 5L")
    supplier = st.text_input("5. Nama Pembekal / Kedai (Supplier)", placeholder="cth: Kedai Kimia Jaya")
    amount = st.number_input("6. Jumlah Amaun Perbelanjaan (RM)", min_value=0.0, format="%.2f")
    catatan = st.text_area("7. Catatan / Rujukan Resit (Opsional)")
    
    st.markdown("---")
    
    if st.button("🚀 SIMPAN PERBELANJAAN KE LEJAR", use_container_width=True):
        if amount <= 0:
            st.warning("Sila masukkan jumlah amaun yang sah (Lebih RM0.00).")
        elif not butiran:
            st.warning("Sila isi bahagian butiran ringkas perbelanjaan.")
        elif not supplier:
            st.warning("Sila isi nama pembekal/kedai untuk memudahkan rujukan.")
        else:
            with st.spinner("Sistem sedang menulis ke Google Sheet..."):
                try:
                    expenses_sheet = sheet.worksheet("Raw_Expenses")
                    all_values = expenses_sheet.get_all_values()
                    
                    if len(all_values) == 0:
                        headers = ["NO", "TARIKH", "BAYAR_MELALUI", "BUTIRAN", "KOD_PERBELANJAAN", "AMOUNT", "PEMBEKAL", "CATATAN", "COGS_ESTIMATE", "GABUNGAN"]
                        expenses_sheet.append_row(headers)
                        next_id = 1
                    else:
                        next_id = len(all_values)
                    
                    bulan_tahun_str = tarikh.strftime("%b%Y")
                    kod_gabungan = f"{akaun_pilihan}{bulan_tahun_str}"
                    
                    # 🎯 SUSUNAN DATA INPUT BERSIH SEBENAR
                    row_data = [
                        next_id,
                        tarikh.strftime("%d/%m/%Y"),
                        akaun_pilihan,
                        butiran,
                        kod_pilihan, # Memastikan hanya teks kod bersih yang dihantar (cth: '5-1000 SABUN DAN PEWANGI')
                        amount,
                        supplier.upper(),
                        catatan,
                        "", 
                        kod_gabungan
                    ]
                    
                    expenses_sheet.append_row(row_data)
                    st.success(f"Berjaya! Perbelanjaan direkodkan di lejar: {kod_gabungan}")
                    
                except Exception as err:
                    st.error(f"Gagal menyimpan transaksi: {err}")
