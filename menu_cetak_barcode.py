import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
import io
import base64
import re



def jana_gambar_barcode_128(teks_id):
    """
    Fungsi menukarkan teks QR ID Karpet menjadi gambar 
    garisan barcode Code 128.
    """
    try:
        kod_bar_kelas = barcode.get_by_name('code128')
        kod_bar = kod_bar_kelas(teks_id, writer=ImageWriter())
        
        buffer_memori = io.BytesIO()
        kod_bar.write(buffer_memori, options={"write_text": False, "quiet_zone": 2})
        
        kod_imej_digital = base64.b64encode(buffer_memori.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{kod_imej_digital}"
    except:
        return ""

def papar_menu_cetak_barcode(t_tempahan, t_karpet, t_pelanggan):

    st.title("🖨️ Cetak Barcode Carpet")
    st.caption("Menu pengurusan cetakan tag kod bar karpet secara pukal (Format Ujian Kertas A6).")

    

    # Tarik data dari 3 tab Sheets untuk proses 'Teknik Jambatan'
    data_t = t_tempahan.get_all_values() if t_tempahan else []
    data_k = t_karpet.get_all_values() if t_karpet else []
    data_p = t_pelanggan.get_all_values() if t_pelanggan else []

    df_t = pd.DataFrame(data_t[1:], columns=data_t) if len(data_t) > 1 else pd.DataFrame()
    df_k = pd.DataFrame(data_k[1:], columns=data_k) if len(data_k) > 1 else pd.DataFrame()
    df_p = pd.DataFrame(data_p[1:], columns=data_p) if len(data_p) > 1 else pd.DataFrame()

    # Seragamkan nama lajur kepada huruf besar
    if not df_t.empty: df_t.columns = [str(c).upper().strip() for c in df_t.columns]
    if not df_k.empty: df_k.columns = [str(c).upper().strip() for c in df_k.columns]
    if not df_p.empty: df_p.columns = [str(c).upper().strip() for c in df_p.columns]

    if df_t.empty or df_k.empty or df_p.empty:
        st.warning("⚠️ Pangkalan data kosong atau sedang dimuatkan.")
        return

    # =========================================================================
    # 2. LOGIK PENAPISAN: BUANG INVOIS YANG SEMUA CARPETNYA SUDAH "SELESAI"
    # =========================================================================
    df_karpet_aktif = df_k[df_k.iloc[:, 6].astype(str).str.upper().str.strip() != "SELESAI"]
    senarai_invois_aktif = df_karpet_aktif.iloc[:, 1].dropna().unique().tolist()

    df_tempahan_aktif = df_t[df_t.iloc[:, 0].isin(senarai_invois_aktif)]

    if df_tempahan_aktif.empty:
        st.info("✨ Tiada tempahan aktif yang memerlukan cetakan stiker buat masa ini.")
        return

    # =========================================================================
    # 3. KOTAK DROPDOWN GABUNGAN (NO INVOICE + ALAMAT PELANGGAN)
    # =========================================================================
    pilihan_dropdown_gabungan = ["-- Sila Pilih Invoice --"]
    peta_rujukan_invois = {}

    for idx, row in df_tempahan_aktif.iterrows():
        inv_no = str(row.iloc[0]).strip()
        cus_id_t = str(row.iloc[2]).strip()
        
        row_p = df_p[df_p.iloc[:, 0] == cus_id_t]
        alamat_p = str(row_p.iloc[0, 3]).strip() if not row_p.empty else "Tiada Alamat"
        
        alamat_pendek = alamat_p[:40] + "..." if len(alamat_p) > 40 else alamat_p
        teks_paparan_box = f"{inv_no} - {alamat_pendek.upper()}"
        
        pilihan_dropdown_gabungan.append(teks_paparan_box)
        peta_rujukan_invois[teks_paparan_box] = inv_no

    st.markdown("### 🔍 1. Pilih Tempahan Aktif")
    pilihan_user = st.selectbox("Cari Nombor Invoice & Alamat Rumah Pelanggan:", pilihan_dropdown_gabungan)

    if pilihan_user != "-- Sila Pilih Invoice --":
        inv_sebenar = peta_rujukan_invois[pilihan_user]
        
        row_t_final = df_t[df_t.iloc[:, 0] == inv_sebenar]
        cus_id_final = str(row_t_final.iloc[0, 2]).strip() if not row_t_final.empty else "CUS-0000"
        
        row_p_final = df_p[df_p.iloc[:, 0] == cus_id_final]
        no_tel_final = str(row_p_final.iloc[0, 2]).strip() if not row_p_final.empty else "000-0000000"
        
        df_pecahan_karpet = df_k[df_k.iloc[:, 1] == inv_sebenar]

        if not df_pecahan_karpet.empty:
            st.markdown("---")
            st.markdown("### 📋 2. Senarai Karpet Dalam Invois Ini")
            
            # Paparkan jadual rujukan yang bersih untuk semakan abang
            df_view_clean = df_pecahan_karpet.copy()
            st.dataframe(df_view_clean, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown(f"### 📄 3. Pratonton Halaman Cetakan A6 ({len(df_pecahan_karpet)} Stiker)")
            
            # --- MEMBINA REKA BENTUK STIKER GRID KERTAS A6 (HTML & CSS) ---
            html_semua_stiker = ""
            for idx, row_k in df_pecahan_karpet.iterrows():
                qr_id_karpet = str(row_k.iloc[0]).strip()
                kod_saiz = str(row_k.iloc[2]).strip()
                
                imej_barcode_base64 = jana_gambar_barcode_128(qr_id_karpet)
                
                html_semua_stiker += f"""
                <div class="stiker-box">
                    <div class="header-tag">MYCARPET PRO v2.0</div>
                    <div class="barcode-zone">
                        <img src="{imej_barcode_base64}"/>
                    </div>
                    <div class="id-text">{qr_id_karpet}</div>
                    <div class="footer-text">
                        KOD: {kod_saiz} | {cus_id_final} | {no_tel_final}
                    </div>
                </div>
                """

            # Bekas pembungkus saiz halaman kertas tepat A6 berserta KUASA PRINT ISOLASI (Sembunyi bahagian luar)
            html_kertas_a6_lengkap = f"""
            <div id="print-area-box" class="halaman-a6-container">
                <div class="grid-layout">
                    {html_semua_stiker}
                </div>
            </div>

            <style>
                .halaman-a6-container {{
                    width: 100mm;
                    height: 150mm;
                    background-color: #ffffff;
                    padding: 4mm;
                    border: 1px solid #ccc;
                    box-sizing: border-box;
                    margin: 0 auto;
                }}
                .grid-layout {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    grid-gap: 3mm;
                }}
                .stiker-box {{
                    border: 1px dashed #000000;
                    padding: 4px;
                    text-align: center;
                    background-color: #ffffff;
                    color: #000000;
                    font-family: Arial, sans-serif;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    height: 27mm;
                }}
                .header-tag {{ font-size: 10px; font-weight: bold; letter-spacing: 0.5px; }}
                .barcode-zone img {{ width: 100%; height: 11mm; object-fit: contain; }}
                .id-text {{ font-size: 11px; font-weight: bold; font-family: monospace; margin: 1px 0; }}
                .footer-text {{ font-size: 8px; border-top: 1px solid #000000; padding-top: 2px; font-weight: bold; font-family: monospace; }}

                /* 🚨 FORMULA MATIKAN SIDEBAR APABILA BUTANG PRINT DIKLIK 🚨 */
                @media print {{
                    body * {{
                        visibility: hidden;
                    }}
                    #print-area-box, #print-area-box * {{
                        visibility: visible;
                    }}
                    #print-area-box {{
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100mm;
                        height: 150mm;
                        border: none;
                        margin: 0;
                        padding: 0;
                    }}
                    @page {{
                        size: 100mm 150mm;
                        margin: 0;
                    }}
                }}
            </style>

            <script>
                // Fungsi pencetus buka window printer automatik
                function jalankanAksiCetak() {{
                    window.print();
                }}
            </script>
            """
            
            # 1. Tampilkan kotak pratonton A6 yang cantik di skrin
            st.components.v1.html(html_kertas_a6_lengkap, height=580)
            
            st.markdown("---")
            
            # 2. ✨ PENAMBAHAN BUTANG PRINTER AUTOMATIK DI SINI
            if st.button("🖨️ Cetak Tag Barcode Sekarang (A6)", use_container_width=True):
                # Suntikan kod arahan print tingkap browser secara terus tanpa perlu klik kanan lagi
                st.components.v1.html(
                    f"""
                    {html_kertas_a6_lengkap}
                    <script>
                        window.print();
                    </script>
                    """,
                    height=0
                )
                st.success("🎉 Arahan cetakan bersih telah dihantar ke mesin printer termal abang!")
        else:
            st.warning("⚠️ Tiada pecahan data karpet dijumpai untuk nombor invoice ini di dalam tab 'Karpet'.")
