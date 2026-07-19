import os
import time
import datetime
from datetime import datetime
import pandas as pd
import gspread
import streamlit as st
from database import inisial_database_segar
import menu_invoice
from streamlit_cookies_controller import CookieController
import menu_temujanji
import menu_scan_qr
import menu_tempahan
import menu_harga
import menu_cetak_barcode
from google.oauth2 import service_account




# TENTUKAN KONFIGURASI HALAMAN UTAMA STREAMLIT
st.set_page_config(page_title="MYCARPET PRO v2.0",
                   page_icon="🧺", layout="wide")

# Pastikan bilangan_karpet sentiasa wujud untuk mengelakkan ralat di semua menu
if "bilangan_karpet" not in st.session_state:
    st.session_state.bilangan_karpet = 1


# Inisialisasi pengontrol cookie di luar fungsi
controller = CookieController()

# 1. FUNGSI SAMBUNGAN UTAMA PANGKALAN DATA GOOGLE SHEETS

def semak_login():
    # Periksa sama ada cookie "ingat_user" wujud dalam browser
    user_saved = controller.get("ingat_user")
    
    # Jika ada cookie sah, terus set session_state sebagai True
    if user_saved == "cuci carpet":
        st.session_state["log_masuk"] = True
    
    if "log_masuk" not in st.session_state:
        st.session_state["log_masuk"] = False
        
    if not st.session_state["log_masuk"]:
        st.title("🔒 Sistem Pengurusan MyCarpet")
        st.subheader("Sila Log Masuk")
        
        # Menggunakan st.form supaya data input dihantar serentak dalam sekali klik
        with st.form("borang_login"):
            username = st.text_input("Nama Pengguna (Username)")
            password = st.text_input("Kata Laluan (Password)", type="password")
            
            # TAMBAHAN: Checkbox untuk pilihan Ingat Saya
            ingat_saya = st.checkbox("Ingat Saya (Remember Me)")
            
            butang_masuk = st.form_submit_button("Masuk")
            
            if butang_masuk:
                if username == "cuci carpet" and password == "Carpet2026":
                    st.session_state["log_masuk"] = True
                    
                    # TAMBAHAN: Jika ditanda, simpan cookie selama 30 hari (2,592,000 saat)
                    if ingat_saya:
                        controller.set("ingat_user", username, max_age=2592000)
                    
                    st.success("Log masuk berjaya! Memuatkan sistem...")
                    st.rerun() # Ini akan terus membuka dashboard utama
                else:
                    st.error("Username atau Password salah!")
                    
        return False
    return True

#cut database untuk percobaan

# MEMANGGIL SESI PANGKALAN DATA AWAL
if semak_login():


# 2. STRUKTUR MENU NAVIGASI UTAMA (SIDEBAR)
# Sila pastikan Baris 51 hingga Baris 61 digantikan dengan kod bersih ini:
    pilihan = st.sidebar.radio(
        "Navigasi Sistem",
        [
            "📊 Dashboard Utama",
            "📅 Slot Janji Temu & Mesej",
            "📝 Tempahan Baru",
            "🔍 Scan & Tracking QR",
            "💳 Pengurusan Pembayaran",
            "📄 Cetak Invois & Resit",
            "💸 Perbelanjaan Bisnes",
            "📸 Kamera Sebelum/Selepas",
            "📋 Pengurusan Katalog Harga",
            "🖨️ Cetak Barcode Carpet"
        ],
        key="navigasi_utama_system"
    )
    


# ==========================================
# === MENU 1: DASHBOARD UTAMA & Temujanji===
# ==========================================
    if pilihan == "📊 Dashboard Utama":
        st.title("📊 Pusat Kawalan Operasi")
        tab_harga, t_pelanggan, t_tempahan, t_karpet = inisial_database_segar()

        data_mentah_t = t_tempahan.get_all_values() if t_tempahan else []
        if len(data_mentah_t) > 1:
            df_t = pd.DataFrame(data_mentah_t[1:], columns=data_mentah_t[0])
            df_t.columns = [str(c).upper().strip() for c in df_t.columns]

            hari_ini = datetime.now().strftime('%Y-%m-%d')
            bulan_ini = datetime.now().strftime('%Y-%m')

            if 'TARIKH' in df_t.columns:
                df_t['TARIKH'] = df_t['TARIKH'].astype(str).str.strip()
                df_hari_ini = df_t[df_t['TARIKH'] == hari_ini]
                df_bulan_ini = df_t[df_t['TARIKH'].str.startswith(bulan_ini)]
            else:
                df_hari_ini = pd.DataFrame()
                df_bulan_ini = pd.DataFrame()

            jumlah_cucian_hari_ini = len(df_hari_ini)
            total_customer_bulan_ini = len(df_bulan_ini)
    
            # === HAPUS KOD LAMA & GANTIKAN DARI BARIS 132 HINGGA 202 DENGAN INI ===
        #TARIKH 17/7,DATA ASAL
#MASUKKAN BAHAGIAN PROSES DAN STATUS KARPET

            # 1. AMBIL DATA DARI TAB KARPET (MENGGUNAKAN INDEKS TETAP JALUR G)
            data_mentah_karpet = t_karpet.get_all_values() if 't_karpet' in locals() or 't_karpet' in globals() else []

            # Ekstrak teks dari Kolom G (Indeks 6) sahaja untuk setiap baris data (Lompat baris Table1 & Header)
            senarai_status = [str(baris[6]).strip().upper() for baris in data_mentah_karpet[1:] if len(baris) > 6]

            # # 2. PENGIRAAN TOTAL SECARA TERUS MENGGUNAKAN .count() (KATA YANG SAMA DIKUMPULKAN)
            skarp_proses = senarai_status.count('DALAM PROSES') + senarai_status.count('PENDING')
            skarp_cuci = senarai_status.count('PENGERINGAN') # Disatukan membaca status PENGERINGAN sahaja
            skarp_siap = 0 # Dibersihkan jadi 0 kerana kategori ini sudah dibuang
            skarp_deliver = senarai_status.count('READY TO DELIVER')
            skarp_selesai = senarai_status.count('SELESAI') + senarai_status.count('DONE')


            # Hitung jumlah baris keseluruhan yang aktif
            total_keseluruhan = len(senarai_status)

            # 3. KIRA JUMLAH TEMPOH MASA (DARI TAB TEMPAHAN)
            bulan_ini_str = datetime.now().strftime('%Y-%m')
            tahun_ini_str = datetime.now().strftime('%Y')

            # MENGHADIRKAN SEMULA DF_T SUPAYA BARIS BAWAH TIDAK MERAH
            data_mentah_tempahan = t_tempahan.get_all_values() if 't_tempahan' in locals() or 't_tempahan' in globals() else []
            df_t = pd.DataFrame(data_mentah_tempahan[1:], columns=data_mentah_tempahan[0]) if len(data_mentah_tempahan) > 1 else pd.DataFrame()

            
            if 'INV NO' in df_t.columns and 'TARIKH' in df_t.columns:
                df_t['TARIKH'] = df_t['TARIKH'].astype(str).str.strip()
                total_bulan_ini = int(df_t[df_t['TARIKH'].str.startswith(bulan_ini_str)]['INV NO'].count())
                total_tahun_ini = int(df_t[df_t['TARIKH'].str.startswith(tahun_ini_str)]['INV NO'].count())
            else:
                total_bulan_ini = total_customer_bulan_ini
                total_tahun_ini = total_customer_bulan_ini

            # 4. PAPARKAN GRID MATRIK DI DASHBOARD UTAMA
            st.markdown("---")
            st.markdown("### 🔄 Status Operasi Karpet Semasa")
            
            # Ditukar kepada 4 lajur yang sepadan dengan kitaran status baharu
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("⏳ Dalam Proses", f"{skarp_proses} Pcs")
            with c2:
                st.metric("☀️ Pengeringan", f"{skarp_cuci} Pcs")
            with c3:
                st.metric("📦 Ready to Deliver", f"{skarp_deliver} Pcs")
            with c4:
                st.metric("✅ Selesai", f"{skarp_selesai} Pcs")

                
            st.markdown("---")
            st.subheader("📈 Ringkasan Basuhan Karpet")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric(label="🗓️ Bulan Ini", value=f"{total_bulan_ini} Pelanggan")
            with col_t2:
                st.metric(label="📅 Tahun Ini", value=f"{total_tahun_ini} Pelanggan")
            with col_t3:
                st.metric(label="🌍 Sepanjang Waktu", value=f"{total_keseluruhan} Pelanggan")
            st.markdown("---")


            if 'JUMLAH HARGA' in df_t.columns and not df_bulan_ini.empty:
                siri_harga = df_bulan_ini['JUMLAH HARGA'].astype(str).str.replace(
                    'RM', '', case=False).str.replace(',', '').str.strip()
                total_jualan = pd.to_numeric(
                    siri_harga, errors='coerce').fillna(0).sum()
            else:
                total_jualan = 0.0

            col_kiri, col_kanan = st.columns(2)
                
            with col_kiri:
                st.metric("Jumlah Cucian Hari Ini",
                        f"{jumlah_cucian_hari_ini} Karpet")
            with col_kanan:
                st.metric("Total Customer Bulan Ini",
                        f"{total_customer_bulan_ini} Pelanggan")

            st.markdown("---")
            st.metric("Jumlah Jualan Bulan Ini", f"RM {total_jualan:,.2f}")

            
    elif pilihan == "📅 Slot Janji Temu & Mesej":  
           menu_temujanji.papar_menu_temujanji()


# ==========================================
# === MENU 2: TEMPAHAN BARU ===
# ==========================================
    elif pilihan == "📝 Tempahan Baru":
        # Memanggil fungsi menu asing yang kita buat tadi
        menu_tempahan.papar_menu_tempahan_baru()

#===================================
#menu 3 scan dan qr
#=======================

    elif pilihan == "🔍 Scan & Tracking QR":
        tab_harga, t_pelanggan, t_tempahan, t_karpet = inisial_database_segar() # <--- TAMBAH BARIS INI
        # Masukkan pemboleh ubah gspread/Google Sheets anda ke dalam kurungan:
        menu_scan_qr.papar_menu_scan_qr(t_karpet, t_pelanggan)



               

    # ==============================================================================
    # ---  MENU 4 (PAYMENT) ---
    # ==============================================================================
    elif pilihan == "💳 Pengurusan Pembayaran":
        with open("menu_payment.py", "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, globals())
            papar_menu_payment()

#menu 5 invoice

    elif pilihan == "📄 Cetak Invois & Resit":
        _, _, t_tempahan, _ = inisial_database_segar()
        buka_fail_aktif = t_tempahan.spreadsheet
        with open("menu_invoice.py", "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, globals())
            paparan_menu_invoice(buka_fail_aktif)


#=================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#MENU EDIT HARGA 
#==============================================================================
    elif pilihan == "📋 Pengurusan Katalog Harga":
        menu_harga.papar_menu_katalog_harga()


#=============================================================
#MENU LOGISTIK CETAK BARCODE

    elif pilihan == "🖨️ Cetak Barcode Carpet":
        menu_cetak_barcode.papar_menu_cetak_barcode()


 