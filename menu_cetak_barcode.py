import streamlit as st
import pandas as pd
import qrcode
import io
import base64

# ===================================================================
# 1. FUNGSI JANA GAMBAR QR CODE
# ===================================================================
def jana_gambar_qr(teks_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(teks_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer_memori = io.BytesIO()
    img.save(buffer_memori, format="PNG")
    
    kod_imej_digital = base64.b64encode(buffer_memori.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{kod_imej_digital}"


# ===================================================================
# 2. FUNGSI UTAMA PAPARAN MENU SYSTEM
# ===================================================================
def papar_menu_cetak_barcode(t_tempahan, t_karpet, t_pelanggan):
    st.title("🖨️ Cetak QR Code Carpet")
    st.caption("Sistem pengurusan cetakan tag stiker QR Carpet (Format Kertas A6 Grid).")

    # Ambil dan tukar data dari Google Sheets menjadi Dataframe Pandas
    df_t = pd.DataFrame(t_tempahan.get_all_values()[1:], columns=t_tempahan.get_all_values()[0]) if t_tempahan else pd.DataFrame()
    df_k = pd.DataFrame(t_karpet.get_all_values()[1:], columns=t_karpet.get_all_values()[0]) if t_karpet else pd.DataFrame()
    df_p = pd.DataFrame(t_pelanggan.get_all_values()[1:], columns=t_pelanggan.get_all_values()[0]) if t_pelanggan else pd.DataFrame()

    if df_t.empty:
        st.info("ℹ️ Tiada data tempahan aktif ditemui buat masa ini.")
        return

    # --- PILIHAN INVOICE ---
    pilihan_dropdown = ["-- Sila Pilih Invoice --"] + df_t.iloc[:, 0].unique().tolist()
    inv_sebenar = st.selectbox("🎯 1. Pilih Nombor Invoice Pelanggan:", pilihan_dropdown)

    if inv_sebenar != "-- Sila Pilih Invoice --":
        
        # ----------------================================================---
        # FIX: PENGAMBILAN DATA PELANGGAN YANG TEPAT MENGIKUT NAMA LAJUR (BUKAN INDEKS)
        # ----------------================================================---
        row_t = df_t[df_t.iloc[:, 0] == inv_sebenar]
        cus_id_final = row_t.iloc[0, 2] if not row_t.empty else "CUS-0000"
        
        # Cari data pelanggan dalam df_p
        row_p = df_p[df_p.iloc[:, 0] == cus_id_final]
        
        # Semak nama lajur telefon secara selamat (mengambil lajur bernama TELEFON atau No. Telefon)
        lajur_tel = [c for c in df_p.columns if 'TEL' in str(c).upper()]
        
        if not row_p.empty and lajur_tel:
            no_tel_final = str(row_p[lajur_tel[0]].values[0]).strip()
        else:
            # Jika tiada nama lajur, guna indeks asal lajur ke-3 (indeks 2) untuk No. Telefon
            no_tel_final = row_p.iloc[0, 2] if not row_p.empty else "000-0000000"

        # Tapis senarai pecahan karpet yang hanya milik nombor invoice ini
        df_pecahan_karpet = df_k[df_k.iloc[:, 1] == inv_sebenar]

        if df_pecahan_karpet.empty:
            st.warning("⚠️ Tiada pecahan data karpet dijumpai untuk nombor invoice ini di dalam tab 'Karpet'.")
            return

        # 1. PAPARAN JADUAL PREVIEW UNTUK SEMAK JUMLAH CARPET
        st.markdown(f"### 📊 2. Senarai Karpet Dalam Invoice Ini")
        df_view_clean = df_pecahan_karpet.copy()
        st.dataframe(df_view_clean, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.markdown(f"### 📑 3. Pratonton Halaman Cetakan A6 ({len(df_pecahan_karpet)} Stiker)")

        # 2. STRUKTUR GRID KERTAS A6
        html_semua_stiker = ""
        for idx, row_k in df_pecahan_karpet.iterrows():
            qr_id_karpet = str(row_k.iloc[0]).strip()
            kod_saiz = str(row_k.iloc[2]).strip()  # Mengambil data kod gred/saiz karpet
            
            # Jana gambar QR Code dinamik base64
            imej_qr_base64 = jana_gambar_qr(qr_id_karpet)

            # Menyusun stiker box ke dalam bentuk grid
            html_semua_stiker += f"""
            <div class="stiker-box">
                <div class="header-tag">MYCARPET PRO v2.0</div>
                <div class="invoice-title">INV: {inv_sebenar}</div>
                <div class="barcode-zone">
                    <img src="{imej_qr_base64}">
                </div>
                <div class="id-text">QR ID: {qr_id_karpet}</div>
                <div class="footer-text">
                    KOD: {kod_saiz} | CUS: {cus_id_final} | TEL: {no_tel_final}
                </div>
            </div>
            """

        # Rangka penuh reka bentuk HTML halaman kertas A6 dengan Grid Layout 2 Lajur
        html_kertas_a6_lengkap = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #ffffff; }}
                
                .halaman-a6-container {{
                    width: 100mm;
                    height: 150mm;
                    padding: 2mm;
                    box-sizing: border-box;
                    margin: 0 auto;
                }}
                
                .grid-layout {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    grid-gap: 2mm;
                }}
                
                .stiker-box {{
                    border: 1px dashed #000000;
                    padding: 4px;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    height: 34mm; 
                    text-align: center;
                    page-break-inside: avoid;
                }}
                
                .header-tag {{ font-size: 9px; font-weight: bold; letter-spacing: 0.5px; color: #333; }}
                .invoice-title {{ font-size: 11px; font-weight: bold; margin: 1px 0; }}
                .barcode-zone img {{ width: 100%; height: 16mm; object-fit: contain; }}
                .id-text {{ font-size: 8px; font-weight: bold; font-family: monospace; }}
                .footer-text {{ font-size: 7px; border-top: 1px solid #000000; padding-top: 1px; font-weight: bold; color: #111; }}
                
                @media print {{
                    body * {{ visibility: hidden; }}
                    .halaman-a6-container, .halaman-a6-container * {{ visibility: visible; }}
                    .halaman-a6-container {{ position: absolute; left: 0; top: 0; width: 100mm; height: 150mm; }}
                    @page {{ size: 100mm 150mm; margin: 0; }}
                }}
            </style>
        </head>
        <body>
            <div class="halaman-a6-container">
                <div class="grid-layout">
                    {html_semua_stiker}
                </div>
            </div>
        </body>
        </html>
        """

        # Papar komponen kotak pratonton
        st.components.v1.html(html_kertas_a6_lengkap, height=580, scrolling=True)
        st.markdown("---")

        # 3. BUTANG MUAT TURUN PINTAR JAVASCRIPT BLOB
        html_butang_muat_turun = f"""
        <script>
        function muatTurunHTML() {{
            var isiHTML = `{html_kertas_a6_lengkap}`;
            var blob = new Blob([isiHTML], {{type: "text/html"}});
            var url = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = url;
            a.download = "Stiker_Grid_A6_{inv_sebenar}.html";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }}
        </script>
        <button onclick="muatTurunHTML()" style="width: 100%; background-color: #ff4b4b; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold;">
            💾 Simpan Fail Cetakan QR Grid (Untuk Telefon)
        </button>
        """
        st.components.v1.html(html_butang_muat_turun, height=60)

        if st.button("🖨️ Cetak Terus Dari Laptop (A6 Grid)", use_container_width=True):
            st.components.v1.html(
                f"""
                {html_kertas_a6_lengkap}
                <script>
                window.print();
                </script>
                """,
                height=0
            )
            st.success("Arahan cetakan grid kemas telah dihantar!")
