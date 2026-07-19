import streamlit as st
import pandas as pd
import re
from database import inisial_database_segar




def papar_menu_katalog_harga():
    st.title("📋 Katalog Harga")
    st.caption("Pusat kawalan tetapan kod, jenis permaidani, dan kos cucian semasa.")
    
    # 1. Hubungkan database segar Google Sheets (Tab Harga)
    tab_harga, _, _, _ = inisial_database_segar()
    
    # Tarik data semasa untuk paparan rujukan
    data_mentah = tab_harga.get_all_values() if tab_harga else []
    df_harga = pd.DataFrame()
    
    if len(data_mentah) > 1:
        # KOD ASAL ABANG: Sangat rapat dan tiada ralat (Jangan diubah!)
        df_harga = pd.DataFrame(data_mentah[1:], columns=data_mentah[0])
        df_harga.columns = [str(c).upper().strip() for c in df_harga.columns]

    # --- BAHAGIAN TAB NAVIGASI DI DALAM MENU ---
    tab1, tab2, tab3 = st.tabs(["🔍 Senarai Katalog", "➕ Tambah Kod Baru", "🧮 Formula Pukal"])

    # ==========================================
    # TAB 1: VIEW SENARAI HARGA SEMASA
    # ==========================================
    with tab1:
        st.markdown("### 🗂️ Senarai Kos Cucian Semasa dalam Database")
        if not df_harga.empty:
            df_paparan = df_harga.copy()
            if 'HARGA OPEN' in df_paparan.columns:
                df_paparan['HARGA OPEN'] = df_paparan['HARGA OPEN'].apply(lambda x: f"RM {str(x).replace('RM', '').strip()}")
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
                elif not df_harga.empty and kod_baru in df_harga['KOD'].values:
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
                darab_cs = st.number_input("Prefix CS:", min_value=0.0, value=0.50, step=0.10, format="%.2f")
            with col_f4:
                darab_hp = st.number_input("Prefix HP:", min_value=0.0, value=1.30, step=0.10, format="%.2f")
            with col_f5:
                darab_lp = st.number_input("Prefix LP:", min_value=0.0, value=1.00, step=0.10, format="%.2f")
            with col_f6:
                darab_csg = st.number_input("Prefix CSG:", min_value=0.0, value=1.30, step=0.10, format="%.2f")

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
                # KOD ASAL ABANG: Dipulihkan sepenuhnya supaya kalis ralat KeyError
                kod = str(row.get('KOD', '')).strip().upper()
                
                # Cari nilai darab gandaan mengikut urutan peta_darab
                nilai_darab_semasa = 1.00
                for prefix, nilai in peta_darab.items():
                    if kod.startswith(prefix):
                        nilai_darab_semasa = nilai
                        break
                
                # --- LOGIK EKSTRAK SAIZ PINTAR MENGGUNAKAN REGEX NOMBOR ---
                luas_sqft = 0.0
                try:
                    padanan = re.search(r'(\d+)\s*X\s*(\d+)', kod)
                    if padanan:
                        lebar = float(padanan.group(1))
                        panjang = float(padanan.group(2))
                        luas_sqft = lebar * panjang
                    else:
                        luas_sqft = 24.0 if kod == "TEBAL" else 0.0
                except:
                    luas_sqft = 0.0

                harga_kiraan_final = luas_sqft * nilai_darab_semasa
                senarai_harga_cadangan.append(harga_kiraan_final)

            # Masukkan lajur simulasi pengiraan baharu ke dalam jadual
            df_kalkulator['HARGA BARU (DIKIRA)'] = senarai_harga_cadangan

            st.markdown("---")
            st.markdown("##### 📊 Pratonton Hasil Pengiraan Sebelum Disimpan (Boleh Klik & Edit Lajur Kanan Sekali):")
            
            # --- EDIT YANG SALAH SAHAJA DI SINI ---
            # Menukar st.dataframe kepada st.data_editor supaya lajur kanan boleh diedit manual, 
            # tetapi mengekalkan struktur jadual asal yang rapat dan bersih.
            jadual_diedit = st.data_editor(df_kalkulator, use_container_width=True, hide_index=True)

            st.markdown("---")
            
            if st.button("🚀 Sahkan & Kemas Kini Semua Harga ke Google Sheets", use_container_width=True):
                with st.spinner("Sedang memindahkan semua hasil pengiraan formula secara pukal..."):
                    try:
                        # 1. Sediakan senarai kosong untuk kumpul semua data harga baharu
                        senarai_kemaskini = []
                        senarai_harga_akhir = jadual_diedit['HARGA BARU (DIKIRA)'].tolist()
                        
                        for indeks, harga_final in enumerate(senarai_harga_akhir):
                            baris_sheets = indeks + 2
                            harga_hantar = f"{float(harga_final):.2f}"
                            
                            senarai_kemaskini.append({
                                'range': f'C{baris_sheets}',
                                'values': [[harga_hantar]]
                            })
                        
                        # 2. Hantar data secara pukal ke Sheets
                        tab_harga.batch_update(senarai_kemaskini)
                        
                        # 3. Simpan status berjaya ke dalam memori supaya teks tidak hilang selepas refresh
                        st.session_state["mesej_jaya_harga"] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ralat sistem: {e}")

            # --- PAPARAN KOTAK TEKS BERJAYA (MUNCUL SELEPAS BUTTON DIKLIK) ---
            if st.session_state.get("mesej_jaya_harga", False):
                st.success("🎉 Berjaya! Semua kos katalog baharu (gandingan formula & edit manual) telah dikemas kini ke dalam Google Sheets.")
                
                # Sediakan butang kecil untuk tutup mesej jika abang mahu hilangkan teks tersebut
                if st.button("✖️ Tutup Makluman"):
                    st.session_state["mesej_jaya_harga"] = False
                    st.rerun()

