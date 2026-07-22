import os
import time
import datetime
from datetime import datetime
import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import menu_invoice
from streamlit_cookies_controller import CookieController
import menu_temujanji
import menu_cetak_barcode
import menu_harga
import menu_kewangan


# TENTUKAN KONFIGURASI HALAMAN UTAMA STREAMLIT
st.set_page_config(page_title="MYCARPET PRO v2.0",
                   page_icon="🧺", layout="wide")

# Pastikan bilangan_karpet sentiasa wujud untuk mengelakkan ralat di semua menu
if "bilangan_karpet" not in st.session_state:
    st.session_state.bilangan_karpet = 1


# Inisialisasi pengontrol cookie di luar fungsi
controller = CookieController()

# ===================================================================
# FUNGSI CACHE UNTUK MENYELAMATKAN KUOTA GOOGLE SHEETS API (KALIS ERROR 429)
# ===================================================================
@st.cache_data(ttl=60) # Data disimpan selama 60 saat sebelum dibenarkan tarik baru
def tarik_data_sheets_selamat(_worksheet_obj):
    if _worksheet_obj:
        return _worksheet_obj.get_all_values()
    return []

# Fungsi pembersihan cache jika abang mahu paksa data segar masuk serta-merta
def clear_cache_sheets():
    st.cache_data.clear()

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



   

        # --- SAMBUNGAN UTAMA GOOGLE SHEETS (Wajib rapat ke kiri sepenuhnya, tanpa def) ---
try:
    info_kredensial = dict(st.secrets["gspread"])
    gc = gspread.service_account_from_dict(info_kredensial)
    
    url_sheet = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=205062829#gid=205062829"
    buka_fail = gc.open_by_url(url_sheet)
    
    # Pembolehubah ini sekarang aktif secara global untuk baris 622 dan menu lain
    tab_harga = buka_fail.worksheet("SENARAI_HARGA")
    t_pelanggan = buka_fail.worksheet("Pelanggan")
    t_tempahan = buka_fail.worksheet("Tempahan")
    t_karpet = buka_fail.worksheet("Karpet")
except Exception as e:
    st.error(f"❌ Gagal menyambung ke Google Sheets: {e}")
    tab_harga, t_pelanggan, t_tempahan, t_karpet = None, None, None, None


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
            "📋 Pengurusan Katalog Harga",
            "🖨️ Cetak Barcode Carpet",
            "📊 Kewangan"
        ],
        key="navigasi_utama_system"
    )
    


# ==========================================
# === MENU 1: DASHBOARD UTAMA & Temujanji===
# ==========================================
    if pilihan == "📊 Dashboard Utama":
        st.title("📊 Pusat Kawalan Operasi")

       
    
        
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
            # GANTIKAN BARIS 160 DENGAN KOD INI:
            skarp_cuci = senarai_status.count('PENGERINGAN') + senarai_status.count('SEDANG DICUCI') + senarai_status.count('CUCI')

            skarp_siap = senarai_status.count('SIAP CUCI') + senarai_status.count('SIAP')
            skarp_deliver = senarai_status.count('READY TO DELIVER') + senarai_status.count('SIAP DIHANTAR')
            skarp_selesai = senarai_status.count('SELESAI') + senarai_status.count('DONE') + senarai_status.count('SELESAI DIHANTAR')

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
            st.subheader("🔄 Status Operasi Karpet Semasa")
            # UBAH BARIS 188 MENJADI SEPERTI INI (Ganti angka 5 kepada 4):
            col_s1, col_s2, col_s4, col_s5 = st.columns(4)

            with col_s1:
                st.metric(label="⏳ Dalam Proses", value=f"{skarp_proses} Pcs")
            with col_s2:
                st.metric(label="☀️ Pengeringan", value=f"{skarp_cuci} Pcs")
            #with col_s3:
                #st.metric(label="✨ Siap Cuci", value=f"{skarp_siap} Pcs")
            with col_s4:
                st.metric(label="🚚 Ready to Deliver", value=f"{skarp_deliver} Pcs")
            with col_s5:
                st.metric(label="✅ Selesai", value=f"{skarp_selesai} Pcs")
                
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
   # ==========================================
# === MENU 2: TEMPAHAN BARU ===
# ==========================================
    elif pilihan == "📝 Tempahan Baru":

        # 1. Hubungkan sesi pangkalan data segar Google Sheets
        

        alamat_input = ""
        nama_input = ""
        telefon_input = ""
        daerah_input = ""

        # 2. Kotak pilihan jenis pendaftaran pelanggan
        status_pelanggan = st.radio("Status Pelanggan:", [
                                    "Pelanggan Sedia Ada", "Pelanggan Baru"], horizontal=True)

        # 3. Aliran logik untuk Pelanggan Sedia Ada
        data_p_mentah = t_pelanggan.get_all_values() if t_pelanggan else []
        df_p = pd.DataFrame()

        if status_pelanggan == "Pelanggan Sedia Ada":
            if len(data_p_mentah) > 1:
                df_p = pd.DataFrame(data_p_mentah[1:], columns=data_p_mentah[0])
                df_p.columns = [str(c).upper().strip() for c in df_p.columns]

            if not df_p.empty:
                # Cipta senarai paparan gabungan: "ID - Alamat" untuk memudahkan carian anda
                senarai_paparan = ["-- Sila Pilih Pelanggan --"]
                for idx, row in df_p.iterrows():
                    cus_id = str(row.get('CUSTOMER ID', '')).strip()
                    alamat_p = str(row.get('ALAMAT', '')).strip()
                    if cus_id and alamat_p:
                        senarai_paparan.append(f"{cus_id} - {alamat_p}")
                    else:
                        senarai_paparan.append(
                            cus_id if cus_id else f"Pelanggan {idx+1}")

                pilih_gabungan = st.selectbox(
                    "Pilih Pelanggan (ID - Alamat):", senarai_paparan)

                if pilih_gabungan != "-- Sila Pilih Pelanggan --":
                    id_asal = pilih_gabungan.split(" - ")[0].strip()
                    # Tapis mengikut ID yang sepadan
                    df_filtered = df_p[df_p['CUSTOMER ID'] == id_asal]
                    if not df_filtered.empty:
                        info_p = df_filtered.iloc[0]
                        nama_input = info_p.get('NAMA', '')
                        telefon_input = info_p.get('TELEFON', '')
                        alamat_input = info_p.get('ALAMAT', '')
                        daerah_input = info_p.get('DAERAH', '')

                        st.session_state["id_pelanggan_dipilih"] = id_asal
                        st.info(
                            f"👤 Pelanggan: {nama_input} | 📞 Tel: {telefon_input}")
        else:
            # Paparan Borang Input Manual untuk Pelanggan Baru
            nama_input = st.text_input("Nama Pelanggan Baru:")
            telefon_input = st.text_input("No. Telefon:")
            alamat_input = st.text_input("Alamat Rumah:")
            daerah_input = ""  # Dibiarkan kosong untuk manual kemudian mengikut permintaan

        st.markdown("---")
        st.subheader("🧺 Butiran Permaidani")

        # 4. Menguruskan penambahan/pengurangan bilangan borang permaidani secara dinamik
        if "bilangan_karpet" not in st.session_state:
            st.session_state.bilangan_karpet = 1

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("➕ Tambah Karpet", use_container_width=True):
                st.session_state.bilangan_karpet += 1
        with col_b2:
            if st.button("➖ Kurang Karpet", use_container_width=True) and st.session_state.bilangan_karpet > 1:
                st.session_state.bilangan_karpet -= 1

        # Tarik data senarai gred/kod karpet dari Google Sheets tab 'Harga' (SENARAI_HARGA)
        data_harga_mentah = tab_harga.get_all_values() if tab_harga else []
        df_harga_opt = pd.DataFrame()
        if len(data_harga_mentah) > 1:
            df_harga_opt = pd.DataFrame(
                data_harga_mentah[1:], columns=data_harga_mentah[0])
            df_harga_opt.columns = [str(c).upper().strip()
                                    for c in df_harga_opt.columns]

        data_karpet_borang = []
        total_harga_keseluruhan = 0.0

        # =========================================================================
        # 1. GELUNG (LOOPING) PEMBINAAN BARIS INPUT PERMAIDANI (VERSI PADANAN TEKSTUAL TEPAT)
        # =========================================================================
        # Pastikan bilangan_karpet sentiasa wujud dalam memori untuk mengelakkan ralat sistem kosong

        for i in range(st.session_state.bilangan_karpet):
            st.markdown(f"📊 **Karpet #{i+1}**")

            # Ambil senarai KOD dari tab Harga sebagai menu dropdown
            if not df_harga_opt.empty and 'KOD' in df_harga_opt.columns:
                senarai_kod_sheets = df_harga_opt['KOD'].dropna().tolist()
            else:
                senarai_kod_sheets = ["CK 4X6", "PELBAGAI"]

            # Kekalkan pilihan "CUSTOM (Saiz Sendiri)" di bahagian paling bawah senarai menu
            if "CUSTOM (Saiz Sendiri)" not in senarai_kod_sheets:
                senarai_kod_sheets.append("CUSTOM (Saiz Sendiri)")

            # Baris Pertama Lajur Input
            c1, c2, c3 = st.columns(3)
            with c1:
                kod_pilihan = st.selectbox(
                    f"Pilih Kod/Gred Karpet #{i+1}", senarai_kod_sheets, key=f"kod_{i}")

            # Semak jenis pilihan kod pengguna (Gunakan format huruf besar sepenuhnya untuk perbandingan)
            pilihan_clean = str(kod_pilihan).strip().upper()
            is_custom_manual = "CUSTOM (SAIZ SENDIRI)" in pilihan_clean

            # Tarik data padanan daripada database Google Sheets tab 'Harga'
            harga_default_sheets = 15.0
            jenis_default_sheets = "Cucian Carpet"

            if not df_harga_opt.empty and not is_custom_manual:
                # Lakukan padanan huruf secara selamat dengan menukar kedua-dua lajur kepada huruf besar sepenuhnya
                df_harga_opt['KOD_UPPER'] = df_harga_opt['KOD'].astype(
                    str).str.strip().str.upper()
                row_padan = df_harga_opt[df_harga_opt['KOD_UPPER']
                                        == pilihan_clean]

                if not row_padan.empty:
                    try:
                        # Ambil nilai lajur 'HARGA OPEN' dan bersihkan simbol RM
                        harga_raw = str(row_padan.iloc[0].get(
                            'HARGA OPEN', '15.0')).replace('RM', '').strip()
                        harga_default_sheets = float(harga_raw)
                        jenis_default_sheets = str(row_padan.iloc[0].get(
                            'JENIS CARPET', 'Carpet')).strip()
                    except Exception as e:
                        harga_default_sheets = 15.0
            elif is_custom_manual:
                harga_default_sheets = 2.50  # Harga asas per sqft untuk fungsi custom manual
                jenis_default_sheets = "CUSTOM"

            with c2:
                qty_k = st.number_input(
                    f"Kuantiti #{i+1}", min_value=1, value=1, step=1, key=f"qty_{i}")

            with c3:
                # Label bertukar dinamik tetapi kotak HARGA KEKAL BOLEH DIEDIT MANUAL
                label_harga = "Harga Per Sqft (RM) #" if is_custom_manual else "Harga Seunit (RM) #"
                harga_seunit = st.number_input(f"{label_harga}{i+1}", min_value=0.0, value=float(
                    harga_default_sheets), step=0.50, key=f"harga_base_{i}")

            # Aliran Logik Pengiraan Bersyarat & Kemunculan 5 Kotak Input Custom Manual
            if is_custom_manual:
                st.markdown(f"⚙️ *Konfigurasi Karpet Custom #{i+1}*")

                c_cust1, c_cust2 = st.columns(2)
                with c_cust1:
                    kod_custom_input = st.text_input(
                        f"Masukkan Kod Baru #{i+1} (Contoh: CT 4X6)", value="CUSTOM-KOD", key=f"custom_kod_{i}")
                with c_cust2:
                    jenis_custom_input = st.text_input(
                        f"Masukkan Jenis Karpet #{i+1} (Contoh: Carpet Tenun)", value="Carpet Tenun", key=f"custom_jenis_{i}")

                c_sz1, c_sz2, c_sz3 = st.columns(3)
                with c_sz1:
                    lebar_f = st.number_input(
                        f"Lebar (Kaki) #{i+1}", min_value=1.0, value=4.0, step=0.5, key=f"lebar_{i}")
                with c_sz2:
                    panjang_f = st.number_input(
                        f"Panjang (Kaki) #{i+1}", min_value=1.0, value=6.0, step=0.5, key=f"panjang_{i}")

                    # Formula Kira Luas dan Subtotal Harga Custom
                    luas_kaki = lebar_f * panjang_f
                    harga_seunit_kiraan = luas_kaki * harga_seunit
                    subtotal_harga = harga_seunit_kiraan * qty_k

                    with c_sz3:
                        st.text_input(
                            f"Jumlah Luas #{i+1}", value=f"{luas_kaki} sqft", disabled=True, key=f"luas_view_{i}")

                    kod_final = kod_custom_input
                    jenis_final = f"{jenis_custom_input.upper()} SAIZ {int(lebar_f)}X{int(panjang_f)}"
                    saiz_teks = f"{lebar_f}' x {panjang_f}' ({luas_kaki} sqft)"
                    harga_simpanan = harga_seunit_kiraan

            elif "PELBAGAI" in pilihan_clean:
                c_sz1, c_sz2, c_sz3 = st.columns(3)
                with c_sz1:
                    lebar_f = st.number_input(
                        f"Lebar (Kaki) #{i+1}", min_value=1.0, value=4.0, step=0.5, key=f"lebar_{i}")
                with c_sz2:
                    panjang_f = st.number_input(
                        f"Panjang (Kaki) #{i+1}", min_value=1.0, value=6.0, step=0.5, key=f"panjang_{i}")

                luas_kaki = lebar_f * panjang_f
                subtotal_harga = (luas_kaki * harga_seunit) * qty_k

                with c_sz3:
                    st.text_input(
                        f"Jumlah Luas (sqft) #{i+1}", value=f"{luas_kaki} sqft", disabled=True, key=f"luas_view_{i}")

                saiz_teks = f"{lebar_f}' x {panjang_f}' ({luas_kaki} sqft)"
                kod_final = kod_pilihan
                jenis_final = jenis_default_sheets
                harga_simpanan = luas_kaki * harga_seunit
            else:
                # Kategori Gred Standard (Dicantumkan semula supaya tiada ralat sintaks terputus)
                subtotal_harga = harga_seunit * qty_k
                saiz_teks = str(kod_pilihan).split(
                )[-1] if "X" in pilihan_clean else "Standard"

                kod_final = kod_pilihan
                jenis_final = jenis_default_sheets
                harga_simpanan = harga_seunit

                # Paparan maklumat ringkasan dinamik di bawah kotak input (Kini Membaca Data Dengan Betul)
                st.caption(f"ℹ️ **Jenis:** {jenis_final}")
                st.caption(
                    f"🌲 **Greenwood (Anggaran Asal Sheets):** RM {harga_default_sheets:.2f}")

            # Pastikan formula darab harga_seunit x qty_k digunakan untuk gred standard
                harga_paparan_sub = harga_seunit * \
                    qty_k if not is_custom_manual else subtotal_harga

                st.text_input(
                    f"Subtotal Harga Karpet #{i+1}",
                    value=f"RM {harga_paparan_sub:.2f}",
                    disabled=True,
                    key=f"sub_view_{i}_{kod_pilihan}_{qty_k}_{harga_seunit}"
                )

                total_harga_keseluruhan += subtotal_harga

                # Memasukkan data ke dalam senarai borang
                data_karpet_borang.append({
                    "kod": kod_final,
                    "jenis": jenis_final,
                    "qty": qty_k,
                    "harga": harga_simpanan,
                    "saiz": saiz_teks
                })

        st.markdown("---")
        st.metric("💰 Jumlah Keseluruhan Tempahan",
                f"RM {total_harga_keseluruhan:.2f}")

        # =========================================================================
        # 2. BUTANG SIMPAN TEMPAHAN (DI LUAR GELUNG KARPET - 100% STABIL & AMAN)
        # =========================================================================
        if st.button("💾 Sahkan & Simpan Tempahan Baru", use_container_width=True):
            data_t_semasa = t_tempahan.get_all_values() if t_tempahan else []
            # Mengira nombor turutan berdasarkan bilangan data sedia ada
            if len(data_t_semasa) > 1:
                # Contoh: Jika ada 1 data (tidak termasuk header), nombor bermula dari 70001 + 1 = 70002
                nombor_turutan = 70000 + len(data_t_semasa)
                next_inv = f"INV26{nombor_turutan:05d}"
            else:
                # Invois pertama yang akan disimpan jika pangkalan data kosong
                next_inv = "INV2670001"


            tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
            harga_formatted = f"RM {total_harga_keseluruhan:.2f}"

            if status_pelanggan == "Pelanggan Sedia Ada":
                current_cus_id = st.session_state.get(
                    "id_pelanggan_dipilih", "CUS0001")
            else:
                data_p_semasa = t_pelanggan.get_all_values() if t_pelanggan else []
                if len(data_p_semasa) > 1:
                    current_cus_id = f"CUS{len(data_p_semasa):04d}"
                else:
                    current_cus_id = "CUS0001"
                if nama_input and telefon_input:
                    t_pelanggan.append_row(
                        [current_cus_id, nama_input, telefon_input, alamat_input, ""])

            baris_tempahan = [next_inv, tarikh_hari_ini,
                            current_cus_id, harga_formatted, "Pending"]
            t_tempahan.append_row(baris_tempahan)

            # 4. Simpan data per helai karpet ke tab Karpet beserta FORMAT QR ID BAHARU
            counter_item = 1  # Bermula dari helai ke-1 untuk invois semasa

            for item in data_karpet_borang:
                try:
                    qty_int = int(item["qty"])
                except:
                    qty_int = 1

                for _ in range(qty_int):
                    # Menjana QR ID mengikut format permintaan abang (Contoh: INV0021-1)
                    qr_id = f"{next_inv}-{counter_item}"

                    baris_karpet = [
                        qr_id,
                        next_inv,
                        item["kod"],
                        item["jenis"],
                        f"RM {item['harga']:.2f}",
                        tarikh_hari_ini,
                        "DALAM PROSES"
                    ]
                    t_karpet.append_row(baris_karpet)
                    counter_item += 1  # Tambah nombor turutan untuk helai karpet seterusnya

            teks_senarai_karpet = ""
            jumlah_keping_karpet = 0
            for idx, item in enumerate(data_karpet_borang):
                try:
                    qty_item = int(item["qty"])
                except:
                    qty_item = 1
                jumlah_keping_karpet += qty_item
                teks_senarai_karpet += f" {idx+1}. {item['jenis'].upper()} ({item['saiz']})\n"

            from datetime import timedelta
            tarikh_siap_anggaran = (datetime.strptime(
                tarikh_hari_ini, "%Y-%m-%d") + timedelta(days=7)).strftime("%d-%m-%Y")
            tarikh_ambil_format = datetime.strptime(
                tarikh_hari_ini, "%Y-%m-%d").strftime("%d-%m-%Y")

            mesej_wa = (
                f"🧺 *MYCARPET PRO v2.0*\n"
                f"Assalamualaikum / Salam Sejahtera,\n\n"
                f"Pelanggan yang dihormati, kami ingin memaklumkan bahawa karpet anda telah selamat diambil dan akan diproses untuk cucian. Berikut adalah maklumat pesanan anda:\n\n"
                f"🧾 *No Invoice:* {next_inv} - {alamat_input[:30]}...\n"
                f"📅 *Tarikh Ambil:* {tarikh_ambil_format}\n"
                f"📆 *Tarikh Siap (Anggaran):* {tarikh_siap_anggaran}\n"
                f"🔢 *Jumlah Karpet:* {jumlah_keping_karpet} keping\n\n"
                f"📝 *Butiran Jenis Karpet:*\n{teks_senarai_karpet}\n"
                f"💰 *Jumlah Harga:* {harga_formatted}\n"
                f"🚚 *Status:* Pickup & Proses Cucian\n\n"
                f"Sila hubungi kami jika anda mempunyai sebarang arahan khas atau ingin menjadualkan masa penghantaran yang sesuai nanti. Terima kasih kerana mempercayai perkhidmatan kami! 🙏✨"
            )

            # Kunci data di dalam memori session state supaya borang tidak padam secara automatik
            st.session_state["data_tersimpan_state"] = True
            st.session_state["teks_resit_salinan"] = mesej_wa
            st.session_state["nota_sukses"] = f"🎉 Tempahan {next_inv} berjaya disimpan ke Google Sheets!"
            st.rerun()

        # -------------------------------------------------------------------------
        # Paparan Komponen Mesej Rasmi (Jarak Tepi 8 Spacebar Dari Dinding Kiri)
        # -------------------------------------------------------------------------
        if st.session_state.get("data_tersimpan_state", False):
            # Paparkan notifikasi kejayaan berwarna hijau di atas kotak teks
            st.success(st.session_state.get("nota_sukses", "🎉 Simpanan Berjaya!"))

            st.markdown("### 📋 Salinan Mesej WhatsApp Resit")
            st.info("💡 Sila klik butang ikon salin (Copy) di penjuru kanan atas kotak teks di bawah ini, kemudian buka aplikasi WhatsApp di laptop abang dan tekan 'Ctrl + V' untuk hantar kepada pelanggan.")

            # KOTAK TEKS BESAR UNTUK ABANG COPY MANUAL (Mempunyai butang salin otomatis di penjuru kanan kotak)
            st.write("Butiran teks resit pesanan pelanggan sedia untuk disalin:")
            st.code(st.session_state.get("teks_resit_salinan", ""), language="text")

            

            st.markdown("---")
            # Sediakan butang reset borang manual untuk diklik apabila urusan salinan selesai
            if st.button("🔄 Buka Borang Baru (Reset Skrin)", use_container_width=True):
                st.session_state.bilangan_karpet = 1
                st.session_state["data_tersimpan_state"] = False
                if "id_pelanggan_dipilih" in st.session_state:
                    del st.session_state["id_pelanggan_dipilih"]
                st.rerun()


#===================================
#menu 3 scan dan qr
#=======================

    elif pilihan == "🔍 Scan & Tracking QR":
        st.subheader("🔍 Scan & Tracking QR")
        
        # Membaca data karpet dan pelanggan menggunakan pembolehubah global di atas
        data_k_raw = t_karpet.get_all_values() if t_karpet else []
        data_p_raw = t_pelanggan.get_all_values() if t_pelanggan else []
        
              
        if len(data_k_raw) > 1:
            # Ambil baris indeks 0 sahaja untuk nama lajur (9 Lajur Utama)
            nama_lajur_k = [str(c).upper().strip() for c in data_k_raw[0]]
            
            # Bina DataFrame Karpet menggunakan data dari baris kedua ke bawah
            df_k = pd.DataFrame(data_k_raw[1:], columns=nama_lajur_k)
            
            # Standardkan nama lajur utama Tab Karpet ke Huruf Besar untuk carian selamat
            for col in df_k.columns:
                df_k[f'{col.upper().strip()} UPPER'] = df_k[col].astype(str).str.upper().str.strip()
                
            # Cari nama asal lajur STATUS dalam Sheets secara fleksibel
            lajur_status_asal = ""
            for col in df_k.columns:
                if col.upper().strip() == 'STATUS':
                    lajur_status_asal = col
                    break
            
            # --- 📊 BAHAGIAN 1: SISTEM CARIAN ---
            st.markdown("### 📊 Bahagian 1: Cari & Semak Status")
            
            mode_carian = st.selectbox(
                "1. Pilih Kaedah Carian Utama:",
                ["No Invois (Contoh: TNV0022)", "Alamat Rumah (Contoh: 35)", "Jenis/Gred Karpet (Contoh: CK)", "QR ID Karpet (Contoh: TNV0022-1)"]
            )
            
            # Logik penapisan sumber data awal (Kekalkan semua jika carian Invois/Alamat)
            if mode_carian in ["No Invois (Contoh: TNV0022)", "Alamat Rumah (Contoh: 35)"]:
                df_sumber = df_k.copy()
            else:
                if lajur_status_asal:
                    df_sumber = df_k[df_k[lajur_status_asal].astype(str).str.upper().str.strip() != "SELESAI DIHANTAR"].copy()
                else:
                    df_sumber = df_k.copy()

            # Ekstrak data unik untuk Dropdown Kata Kunci
            senarai_dropdown = []
            lajur_rujukan = ""
            
            if mode_carian == "No Invois (Contoh: TNV0022)":
                lajur_rujukan = 'NO TNV UPPER' if 'NO TNV UPPER' in df_sumber.columns else ('INV NO UPPER' if 'INV NO UPPER' in df_sumber.columns else "")
                if lajur_rujukan:
                    senarai_dropdown = df_sumber[lajur_rujukan].replace('', None).dropna().unique().tolist()
                    
            elif mode_carian == "Alamat Rumah (Contoh: 35)":
                # Ambil senarai alamat pelanggan secara segar dan terus dari Tab Pelanggan (Kalis Ralat)
                if len(data_p_raw) > 1:
                    nama_lajur_p = [str(c).upper().strip() for c in data_p_raw[0]]
                    df_p = pd.DataFrame(data_p_raw[1:], columns=nama_lajur_p)
                    if 'ALAMAT' in df_p.columns:
                        senarai_dropdown = df_p['ALAMAT'].astype(str).str.upper().str.strip().replace('', None).dropna().unique().tolist()
                        
            elif mode_carian == "Jenis/Gred Karpet (Contoh: CK)":
                lajur_rujukan = 'JENIS UPPER' if 'JENIS UPPER' in df_sumber.columns else ""
                if lajur_rujukan:
                    senarai_dropdown = df_sumber[lajur_rujukan].replace('', None).dropna().unique().tolist()
                    
            elif mode_carian == "QR ID Karpet (Contoh: TNV0022-1)":
                lajur_rujukan = 'QR ID UPPER' if 'QR ID UPPER' in df_sumber.columns else ""
                if lajur_rujukan:
                    senarai_dropdown = df_sumber[lajur_rujukan].replace('', None).dropna().unique().tolist()

            senarai_dropdown = [x for x in senarai_dropdown if x is not None]
            senarai_dropdown.sort()

            kata_kunci = st.selectbox(
                "2. Pilih Kata Kunci Rekod Pelanggan:", 
                ["-- Tampilkan Semua Karpet Aktif --"] + senarai_dropdown
            )

            # Jalankan tapisan jadual mengikut pilihan dropdown kata kunci
            df_hasil_tapis = df_sumber.copy()
            if kata_kunci and kata_kunci != "-- Tampilkan Semua Karpet Aktif --":
                if mode_carian == "Alamat Rumah (Contoh: 35)":
                    nama_lajur_p = [str(c).upper().strip() for c in data_p_raw[0]]
                    df_p = pd.DataFrame(data_p_raw[1:], columns=nama_lajur_p)
                    df_p['ALAMAT_UPPER'] = df_p['ALAMAT'].astype(str).str.upper().str.strip()
                    
                    lajur_cust_p = 'CUSTOMER ID' if 'CUSTOMER ID' in df_p.columns else ""
                    lajur_cust_k = 'CUSTOMER ID UPPER' if 'CUSTOMER ID UPPER' in df_k.columns else ('CUSTOMER ID' if 'CUSTOMER ID' in df_k.columns else "")
                    
                    if lajur_cust_p and lajur_cust_k:
                        senarai_cust_sepadan = df_p[df_p['ALAMAT_UPPER'] == kata_kunci][lajur_cust_p].tolist()
                        df_hasil_tapis = df_sumber[df_sumber[lajur_cust_k].isin(senarai_cust_sepadan)]
                else:
                    df_hasil_tapis = df_sumber[df_sumber[lajur_rujukan] == kata_kunci]

            # --- 🌟 PAPAR KAD WARNA STATUS TERKINI DENGAN TULISAN KECIL (FONT 13PX) 🌟 ---
            if kata_kunci and kata_kunci != "-- Tampilkan Semua Karpet Aktif --" and not df_hasil_tapis.empty:
                st.markdown("### 🔔 Ringkasan Status Karpet Terkini:")
                
                for idx, r in df_hasil_tapis.iterrows():
                    qr_id_badge = r.get('QR ID', 'N/A')
                    jenis_badge = r.get('JENIS', 'Karpet')
                    status_badge = str(r.get(lajur_status_asal, '')).upper().strip() if lajur_status_asal else ""
                    
                    # Format HTML untuk mengecilkan tulisan dan merapatkan baris
                    pesanan_html = f"""
                    <div style="font-size: 13px; line-height: 1.2; margin-bottom: 2px;">
                        🆔 <b>{qr_id_badge}</b> | 📝 Jenis: <i>{jenis_badge}</i> | 🔄 Status: <b>{status_badge}</b>
                    </div>
                    """
                    
                    # --- PAPAR KOTAK WARNA KUSTOM DENGAN HTML AMAN (REPLACEMENT FOR LINES 587-595) ---
                    if status_badge in ["DALAM PROSES"]:
                        # Latar belakang biru lembut (Kalis ralat teks mentah)
                        st.markdown(f"""
                        <div style="background-color: #1e293b; color: #38bdf8; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #0ea5e9; margin-bottom: 4px; font-family: sans-serif;">
                            <span style="font-size: 13px;">🆔 <b>{qr_id_badge}</b> | 📝 Jenis: <i>{jenis_badge}</i> | 🔄 Status: <b style="color: #0ea5e9;">{status_badge}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif status_badge in ["PENGERINGAN", "READY TO DELIVER"]:
                        # Latar belakang kuning lembut
                        st.markdown(f"""
                        <div style="background-color: #2e2511; color: #fbbf24; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #eab308; margin-bottom: 4px; font-family: sans-serif;">
                            <span style="font-size: 13px;">🆔 <b>{qr_id_badge}</b> | 📝 Jenis: <i>{jenis_badge}</i> | 🔄 Status: <b style="color: #eab308;">{status_badge}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    elif status_badge == "SELESAI DIHANTAR":
                        # Latar belakang hijau lembut
                        st.markdown(f"""
                        <div style="background-color: #14281d; color: #4ade80; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #22c55e; margin-bottom: 4px; font-family: sans-serif;">
                            <span style="font-size: 13px;">🆔 <b>{qr_id_badge}</b> | 📝 Jenis: <i>{jenis_badge}</i> | 🔄 Status: <b style="color: #22c55e;">{status_badge}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.code(f"{qr_id_badge} | {jenis_badge} | {status_badge}")

                  # --- 🛠️ BAHAGIAN 2: KOTAK EDIT & KEMASKINI STATUS (DENGAN MULTI-CARPET & st.form) ---
        # Logik Asal: Hanya tunjuk Bahagian 2 jika pengguna sudah MEMILIH No Invois/Pelanggan tertentu (bukan "Semua Karpet Aktif")
        if not df_hasil_tapis.empty and kata_kunci != "-- Tampilkan Semua Karpet Aktif --":
            st.markdown("---")
            st.markdown("### 🛠️ Bahagian 2: Kemaskini Status Karpet")

            lajur_qr_real = 'QR ID' if 'QR ID' in df_hasil_tapis.columns else ""
            
            if lajur_qr_real and lajur_status_asal:
                # 🔍 TAPISAN KETAT: Ambil karpet bagi No Invois terpilih SAHAJA yang BELUM selesai dihantar
                df_aktif_sahaja = df_hasil_tapis[
                    ~df_hasil_tapis[lajur_status_asal].str.upper().str.strip().isin(["SELESAI", "SELESAI DIHANTAR"])
                ]
                senarai_qr_wujud = df_aktif_sahaja[lajur_qr_real].dropna().unique().tolist()
                
                if senarai_qr_wujud:
                    # 💡 Membuka Borang Tempatan (Form) untuk Menjimatkan Kuota Google API
                    with st.form(key='borang_kemaskini_status'):
                        st.write(f"📝 *Ditemui **{len(senarai_qr_wujud)}** karpet aktif untuk No Invois / Rekod ini.*")
                        
                        # 🔄 PILIHAN PUKAL: Mengandungi QR ID untuk Invois terpilih sahaja
                        qr_terpilih = st.multiselect(
                            "3. Pilih QR ID Karpet Yang Mahu Ditukar Status:",
                            options=senarai_qr_wujud,
                            default=senarai_qr_wujud
                        )
                        
                        status_baru = st.selectbox(
                            "4. Pilih Status Baharu:",
                            ["DALAM PROSES", "PENGERINGAN", "READY TO DELIVER", "SELESAI DIHANTAR"]
                        )
                        
                        # Butang hantar borang (wajib di dalam st.form)
                        butang_simpan = st.form_submit_button("💾 Simpan & Hantar Status Baharu", use_container_width=True)
                        
                        if butang_simpan:
                            if not qr_terpilih:
                                st.warning("⚠️ Sila pilih sekurang-kurangnya satu QR ID Karpet sebelum menghantar.")
                            else:
                                kemas_kini_berjaya = 0
                                # Ambil senarai semua QR ID dari baris Google Sheets untuk cari indeks baris asal
                                semua_qr_id_mentah = [str(r[nama_lajur_k.index('QR ID')]).upper().strip() for r in data_k_raw[1:]]
                              # BAIKI RALAT 22/7 TENTANG STATUS PROSES KARPET
                                lajur_status_index_sheets = [str(c).upper().strip() for c in nama_lajur_k].index('STATUS') + 1

                                
                                with st.spinner("Sedang mengemaskini data ke Google Sheets..."):
                                    for q_id in qr_terpilih:
                                        try:
                                            indeks_baris_sheets = semua_qr_id_mentah.index(str(q_id).upper().strip()) + 2
                                            t_karpet.update_cell(indeks_baris_sheets, lajur_status_index_sheets, status_baru)
                                            kemas_kini_berjaya += 1
                                        except ValueError:
                                            st.error(f"❌ Ralat: Gagal mencari baris untuk QR ID {q_id} di Google Sheets.")
                                
                                if kemas_kini_berjaya > 0:
                                    st.success(f"🎉 Sukses! Status bagi {kemas_kini_berjaya} karpet telah ditukar kepada '{status_baru}'!")
                                    st.rerun()
                else:
                    st.info("ℹ️ Semua karpet di bawah No Invois / Rekod ini telah berstatus 'SELESAI' atau 'SELESAI DIHANTAR'.")
            else:
                st.error("❌ Lajur 'QR ID' atau 'STATUS' tidak ditemui dalam fail Google Sheets anda.")

        # --- 📊 PALING BAWAH: JADUAL RUJUKAN VISUAL ---
        st.markdown("---")
        st.write(f"📊 **Senarai Maklumat Karpet Untuk Rujukan ({len(df_hasil_tapis)} rekod):**")
        lajur_papar = [c for c in df_hasil_tapis.columns if not c.endswith('UPPER')]
        st.dataframe(df_hasil_tapis[lajur_papar])


               

    # ==============================================================================
    # ---  MENU 4 (PAYMENT) ---
    # ==============================================================================
    elif pilihan == "💳 Pengurusan Pembayaran":
        with open("menu_payment.py", "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, globals())
            papar_menu_payment()

#menu 5 invoice

  # DI DALAM APP.PY (MENU CETAK INVOIS):
    elif pilihan == "📄 Cetak Invois & Resit":
        # Kita hantar objek 'buka_fail' global yang ada di atas masuk ke dalam fungsi menu
        menu_invoice.paparan_menu_invoice(buka_fail)


#=================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#MENU EDIT HARGA 
#==============================================================================
    elif pilihan == "📋 Pengurusan Katalog Harga":
        menu_harga.papar_menu_katalog_harga(tab_harga)



#=============================================================
#MENU LOGISTIK CETAK BARCODE

    elif pilihan == "🖨️ Cetak Barcode Carpet":
        menu_cetak_barcode.papar_menu_cetak_barcode(t_tempahan, t_karpet, t_pelanggan)



 #==============================================================================
 #MENU KEWANGAN BERMULA DARI BAWAH INI
 #================================================================================================================================

    if pilihan == "📊 Kewangan":
        menu_kewangan.app()
