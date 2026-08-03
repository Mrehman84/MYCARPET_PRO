import streamlit as st
import pandas as pd
import qrcode
import io
import base64

@st.cache_data(ttl=600)
def fetch_data(_worksheet): # Tambah underscore '_' di depan nama parameter
    return _worksheet.get_all_values()

# Usage in your menu
#data_t = fetch_data(t_tempahan) if t_tempahan else []

# ===================================================================
# 1. FUNGSI JANA GAMBAR QR CODE (STABIL)
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
    st.title("🖨 Cetak QR Code Carpet")
    st.caption("Sistem pengurusan cetakan tag stiker QR Carpet (Format Stiker 40mm x 30mm).")

    data_t = fetch_data(t_tempahan) if t_tempahan else []
    # Ambil data dari Google Sheets
    data_t = t_tempahan.get_all_values() if t_tempahan else []
    data_k = t_karpet.get_all_values() if t_karpet else []
    data_p = t_pelanggan.get_all_values() if t_pelanggan else []

    if len(data_t) <= 1:
        st.info("ℹ Tiada data tempahan aktif ditemui buat masa ini.")
        return

    # Tukar menjadi Dataframe
    df_t = pd.DataFrame(data_t[1:], columns=data_t[0])
    df_k = pd.DataFrame(data_k[1:], columns=data_k[0])
    df_p = pd.DataFrame(data_p[1:], columns=data_p[0])

    # --- PILIHAN INVOICE ---
    pilihan_dropdown = ["-- Sila Pilih Invoice --"] + df_t.iloc[:, 0].unique().tolist()
    inv_sebenar = st.selectbox("🎯 1. Pilih Nombor Invoice Pelanggan:", pilihan_dropdown)

    if inv_sebenar != "-- Sila Pilih Invoice --":
        # Ambil data pelanggan
        row_t = df_t[df_t.iloc[:, 0] == inv_sebenar]
        cus_id_final = row_t.iloc[0, 2] if not row_t.empty else "CUS-0000"
        row_p = df_p[df_p.iloc[:, 0] == cus_id_final]

        # FIX AMBIL NO TELEFON: Cari lajur nombor telefon (biasanya indeks ke-2 atau lajur ke-3)
        no_tel_final = "000-0000000"
        if not row_p.empty:
            for col in row_p.columns:
                if 'TEL' in str(col).upper() or 'PHONE' in str(col).upper():
                    no_tel_final = str(row_p[col].values[0]).strip()
                    break
            if no_tel_final == "000-0000000" and len(row_p.columns) >= 3:
                no_tel_final = str(row_p.iloc[0, 2]).strip()

        # Tapis senarai pecahan karpet mengikut invoice
        df_pecahan_karpet = df_k[df_k.iloc[:, 1] == inv_sebenar]

        if df_pecahan_karpet.empty:
            st.warning("⚠ Tiada pecahan data karpet dijumpai untuk nombor invoice ini di dalam tab 'Karpet'.")
            return

        # 1. PAPARAN JADUAL PREVIEW DATA
        st.markdown(f"### 📊 2. Senarai Karpet Dalam Invoice Ini")
        st.dataframe(df_pecahan_karpet, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### 📑 3. Pratonton Halaman Cetakan 40mm x 30mm ({len(df_pecahan_karpet)} Stiker)")

        # 2. BINA STRUKTUR SENARAI STIKER INDIVIDU (40mm x 30mm)
        html_semua_stiker = ""
        for idx, row_k in df_pecahan_karpet.iterrows():
            qr_id_karpet = str(row_k.iloc[0]).strip()
            kod_saiz = str(row_k.iloc[2]).strip() # Mengambil kod gred karpet yang betul
            imej_qr_base64 = jana_gambar_qr(qr_id_karpet)

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

        # Rangka penuh reka bentuk HTML halaman khusus untuk Gulungan Stiker 40mm x 30mm
        html_stiker_40x30_lengkap = f"""
        <html>
        <head>
        <style>
            body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #ffffff; }}
            .halaman-container {{
                width: 40mm;
                margin: 0 auto;
                padding: 0;
            }}
            .stiker-box {{
                width: 40mm;
                height: 30mm;
                border: 1px dashed #000000;
                padding: 1.5mm;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                text-align: center;
                page-break-after: always; /* Asingkan setiap stiker ke halaman baharu semasa cetak */
            }}
            .header-tag {{ font-size: 6px; font-weight: bold; letter-spacing: 0.2px; color: #333; }}
            .invoice-title {{ font-size: 7px; font-weight: bold; margin: 0.5px 0; }}
            .barcode-zone img {{ width: 100%; height: 11mm; object-fit: contain; }}
            .id-text {{ font-size: 5.5px; font-weight: bold; font-family: monospace; }}
            .footer-text {{ font-size: 5px; border-top: 0.5px solid #000000; padding-top: 0.5px; font-weight: bold; color: #111; white-space: nowrap; overflow: hidden; }}
            
            @media print {{
                body {{ background: none; }}
                .stiker-box {{ border: none; }} /* Buang garisan dashed semasa cetakan sebenar */
                @page {{ size: 40mm 30mm; margin: 0; }}
            }}
        </style>
        </head>
        <body>
            <div class="halaman-container">
                {html_semua_stiker}
            </div>
        </body>
        </html>
        """

        # Papar komponen kotak pratonton di Streamlit
        st.components.v1.html(html_stiker_40x30_lengkap, height=350, scrolling=True)

        st.markdown("---")

        # ===================================================================
        # 3. HELAH PINTAR: BUTANG PENCETUS PDF BAWAAN TELEFON & LAPTOP
        # ===================================================================
        st.markdown("### 🖨 Tindakan Cetakan:")

        # Butang ini akan membuka tetingkap cetakan bersih berukuran 40mm x 30mm
        html_butang_cetak_pintar = f"""
        <script>
        function bukaTetingkapCetak() {{
            var tetingkap = window.open('', '_blank', 'width=400,height=400');
            tetingkap.document.write(`{html_stiker_40x30_lengkap}`);
            tetingkap.document.close();
            tetingkap.focus();
            setTimeout(function() {{
                tetingkap.print();
                tetingkap.close();
            }}, 500);
        }}
        </script>
        <button onclick="bukaTetingkapCetak()" style="width: 100%; background-color: #00cc66; color: white; border: none; padding: 14px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-bottom: 10px;">
            🖨 Cetak / Simpan Sebagai PDF (Sesuai Untuk Telefon & Laptop)
        </button>
        """
        st.components.v1.html(html_butang_cetak_pintar, height=70)
