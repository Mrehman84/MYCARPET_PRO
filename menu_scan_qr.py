import streamlit as st
import pandas as pd
from database import inisial_database_segar


# --- MENU 3: SCAN & TRACKING QR ---

def papar_menu_scan_qr(t_karpet, t_pelanggan):
            st.subheader("🔍 Scan & Tracking QR")
            
            # # 1. AMBIL DATA DI BELAKANG TABIR (Karpet & Pelanggan)
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
                        if status_badge in ["DALAM PROSES", "SEDANG DICUCI"]:
                            # Latar belakang biru lembut (Kalis ralat teks mentah)
                            st.markdown(f"""
                            <div style="background-color: #1e293b; color: #38bdf8; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #0ea5e9; margin-bottom: 4px; font-family: sans-serif;">
                                <span style="font-size: 13px;">🆔 <b>{qr_id_badge}</b> | 📝 Jenis: <i>{jenis_badge}</i> | 🔄 Status: <b style="color: #0ea5e9;">{status_badge}</b></span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif status_badge in ["SIAP CUCIH", "READY TO DELIVER"]:
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

                # --- 📝 BAHAGIAN 2: KOTAK EDIT & KEMASKINI STATUS ---
                if not df_hasil_tapis.empty:
                    st.markdown("---")
                    st.markdown("### 📝 Bahagian 2: Kemaskini Status Karpet")
                    
                    lajur_qr_real = 'QR ID' if 'QR ID' in df_hasil_tapis.columns else ""
                    if lajur_qr_real:
                        senarai_qr_wujud = df_hasil_tapis[lajur_qr_real].dropna().unique().tolist()
                        qr_pilihan = st.selectbox("3. Pilih QR ID Karpet Yang Mahu Ditukar Status:", senarai_qr_wujud)
                        
                        if qr_pilihan:
                            row_filtered = df_hasil_tapis[df_hasil_tapis[lajur_qr_real] == qr_pilihan]
                            if not row_filtered.empty:
                                val_status = row_filtered[lajur_status_asal].values[0] if lajur_status_asal else "N/A"
                                val_jenis = row_filtered['JENIS'].values[0] if 'JENIS' in row_filtered.columns else "N/A"
                                
                                st.markdown(f"📍 Karpet Terpilih: **{val_jenis}** | Status Semasa: `{val_status}`")
                            
                            status_baru = st.selectbox(
                                "4. Pilih Status Baharu:",
                                ["DALAM PROSES", "SEDANG DICUCI", "SIAP CUCI", "READY TO DELIVER", "SELESAI DIHANTAR"]
                            )
                            
                            if st.button("💾 Simpan & Hantar Status Baharu Ke Google Sheets", use_container_width=True):
                                lajur_qr_index = [str(c).upper().strip() for c in data_k_raw[0]].index('QR ID')
                                semua_qr_id_mentah = [str(r[lajur_qr_index]).strip() for r in data_k_raw[1:]]
                                
                                try:
                                    indeks_baris_sheets = semua_qr_id_mentah.index(str(qr_pilihan)) + 2
                                    lajur_status_index_sheets = [str(c).upper().strip() for c in data_k_raw[0]].index('STATUS') + 1
                                    
                                    t_karpet.update_cell(indeks_baris_sheets, lajur_status_index_sheets, status_baru)
                                    st.success(f"🎉 Sukses! Status bagi QR ID {qr_pilihan} telah ditukar kepada {status_baru}!")
                                    st.rerun()
                                except ValueError:
                                    st.error("❌ Ralat: Gagal mencari baris QR ID tersebut di dalam fail Google Sheets.")
                    
                    # --- PALING BAWAH: JADUAL JAWAPAN RUJUKAN VISUAL ---
                    st.markdown("---")
                    st.write(f"📋 **Senarai Maklumat Karpet Untuk Rujukan ({len(df_hasil_tapis)} rekod):**")
                    lajur_papar = [c for c in df_hasil_tapis.columns if not c.endswith('UPPER')]
                    st.dataframe(df_hasil_tapis[lajur_papar])
                else:
                    st.info("ℹ️ Tiada data karpet ditemui untuk tapisan pilihan ini.")
            else:
                st.error("❌ **Gagal Memuatkan Data!** Fail Google Sheets Karpet abang didapati kosong.")
