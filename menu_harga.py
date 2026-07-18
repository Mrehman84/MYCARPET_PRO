import streamlit as st
import pandas as pd
from app import inisial_database_segar

def papar_menu_katalog_harga():
    st.title("📋 Katalog Harga")
    st.caption("Pusat kawalan tetapan kod, jenis permaidani, dan kos cucian semasa.")
    
    # 1. Hubungkan database segar Google Sheets (Tab Harga)
    tab_harga, _, _, _ = inisial_database_segar()
    
    # Tarik data semasa untuk paparan rujukan
    data_mentah = tab_harga.get_all_values() if tab_harga else []
    df_harga = pd.DataFrame()
    
    if len(data_mentah) > 1:
        # Guna baris pertama sebagai nama header lajur yang asal
        df_harga = pd.DataFrame(data_mentah[1:], columns=data_mentah[0])

    # --- BAHAGIAN TAB NAVIGASI DI DALAM MENU ---
    tab1, tab2, tab3 = st.tabs(["🔍 Senarai Katalog", "➕ Tambah Kod Baru", "🧮 Formula Pukal"])

    # ==========================================
    # TAB 1: VIEW SENARAI HARGA SEMASA
    # ==========================================
    with tab1:
        st.markdown("### 🗂️ Senarai Kos Cucian Semasa dalam Database")
        if not df_harga.empty:
            df_paparan = df_harga.copy()
            st.dataframe(df_paparan, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Tiada data dijumpai dalam tab 'Harga' Google Sheets anda.")

    # ==========================================
    # TAB 2: TAMBAH KOD/JENIS BARU
    # ==========================================
    with tab2:
        st.markdown("### ➕ Pendaftaran Gred/Jenis Karpet Baru")
        
        with st.form("borang_tambah_harga", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                kod_baru = st.text_input("Kod Karpet Baru (Contoh: CK 5X7):").strip().upper()
            with c2:
                jenis_baru = st.text_input("Nama/Jenis Karpet (Contoh: Carpet Bulu Tebal):").strip()
                
            harga_baru = st.number_input("Harga Seunit / Per Sqft (RM):", min_value=0.0, step=0.50, value=15.00)
            hantar_tambah = st.form_submit_button("💾 Daftarkan Ke Dalam Katalog", use_container_width=True)
            
            if hantar_tambah:
                if not kod_baru or not jenis_baru:
                    st.error("❌ Sila isi ruangan Kod Baru dan Jenis Karpet terlebih dahulu!")
                elif not df_harga.empty and kod_baru in df_harga.iloc[:, 0].values:
                    st.error(f"❌ Kod `{kod_baru}` sudah wujud! Sila guna Tab 'Formula Pukal' jika mahu ubah harga.")
                else:
                    tab_harga.append_row([kod_baru, jenis_baru, f"{harga_baru:.2f}"])
                    st.success(f"🎉 Berjaya! Kod `{kod_baru}` telah ditambah ke dalam database.")
                    st.rerun()

    # ==========================================
    # TAB 3: EDIT HARGA FORMULA PUKAL (DYNAMIC MULTIPLIER)
    # ==========================================
    with tab3:
        st.markdown("### 🧮 Formula Pengiraan Kos Per Sqft")
        st.caption("Masukkan harga darab (RM) bagi setiap kumpulan kod di bawah. Sistem akan mengira luas secara automatik.")

        if not df_harga.empty:
            st.markdown("##### ⚙️ Tetapkan Harga Darab (Per Sqft) mengikut Kumpulan:")
            
            col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns(6)
            with col_f1:
                darab_ck = st.number_input("Prefix CK:", min_value=0.0, value=1.20, step=0.10, format="%.2f")
            with col_f2:
                darab_cn = st.number_input("Prefix CN:", min_value=0.0, value=0.50, step=0.10, format="%.2f")
            with col_f3:
                darab_cs = st.number_input("Prefix CS:", min_value=0.0, value=0.80, step=0.10, format="%.2f")
            with col_f4:
                darab_hp = st.number_input("Prefix HP:", min_value=0.0, value=1.50, step=0.10, format="%.2f")
            with col_f5:
                darab_lp = st.number_input("Prefix LP:", min_value=0.0, value=1.00, step=0.10, format="%.2f")
            with col_f6:
                darab_csg = st.number_input("Prefix CSG:", min_value=0.0, value=1.50, step=0.10, format="%.2f")

            # TURUTAN UTAMA: CSG diletakkan sebelum CS supaya pengiraan tidak bertembung
            peta_darab = {
                "CSG": darab_csg,
                "CK": darab_ck,
                "CN": darab_cn,
                "CS": darab_cs,
                "HP": darab_hp,
                "LP": darab_lp
            }

            df_kalkulator = df_harga.copy()
            senarai_harga_cadangan = []

            for idx, row in df_kalkulator.iterrows():
                # Ambil nilai dari kolom pertama (KOD) secara index kedudukan
                kod = str(row.iloc[0]).strip().upper()
                
                # Cari nilai darab gandaan mengikut urutan peta_darab
                nilai_darab_semasa = 1.00
                for prefix, nilai in peta_darab.items():
                    if kod.startswith(prefix):
                        nilai_darab_semasa = nilai
                        break
                
                # Logik Ekstrak Saiz Pintar
                luas_sqft = 0.0
                try:
                    kod_bersih = kod.upper().strip()
                    bahagian_kod = kod_bersih.split(" ")
                    teks_saiz = ""
                    
                    for perkataan in bahagian_kod:
                        if "X" in perkataan:
                            teks_saiz = perkataan
                            break
                    
                    if not teks_saiz and "X" in kod_bersih:
                        teks_saiz = kod_bersih

                    if teks_saiz:
                        for char in ['CSG', 'CK', 'CN', 'CS', 'HP', 'LP']:
                            teks_saiz = teks_saiz.replace(char, '')
                        
                        panjang_lebar = teks_saiz.split("X")
                        lebar = float(panjang_lebar[0].strip())
                        panjang = float(panjang_lebar[1].strip())
                        luas_sqft = lebar * panjang
                    else:
                        luas_sqft = 24.0
                except:
                    luas_sqft = 24.0

                harga_kiraan_final = luas_sqft * nilai_darab_semasa
                senarai_harga_cadangan.append(harga_kiraan_final)

            # Masukkan lajur simulasi pengiraan ke dalam jadual paparan secara paksa
            df_kalkulator['HARGA BARU (DIKIRA)'] = senarai_harga_cadangan

            st.markdown("---")
            st.markdown("##### 📊 Pratonton Hasil Pengiraan Sebelum Disimpan:")
            
            # Guna paparan asas tanpa menyekat konfigurasi nama kolom suapaya lajur baharu tidak hilang
            st.dataframe(df_kalkulator, use_container_width=True, hide_index=True)

            st.markdown("---")
            
            if st.button("🚀 Sahkan & Kemas Kini Semua Harga ke Google Sheets", use_container_width=True):
                with st.spinner("Sedang memindahkan semua hasil pengiraan formula..."):
                    try:
                        for indeks, row in df_kalkulator.iterrows():
                            baris_sheets = indeks + 2
                            harga_hantar = f"{float(row['HARGA BARU (DIKIRA)']):.2f}"
                            # Update terus ke lajur ke-3 (HARGA OPEN) di Google Sheets
                            tab_harga.update_cell(baris_sheets, 3, harga_hantar)
                            
                        st.success("🎉 Berjaya! Semua harga baru telah disimpan dengan selamat ke Google Sheets.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ralat sistem: {e}")
        else:
            st.warning("⚠️ Pangkalan data tab 'Harga' kosong.")
