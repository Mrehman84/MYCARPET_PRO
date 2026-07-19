import streamlit as st
import pandas as pd
import qrcode
import io
import base64

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
    st.title("🖨️ Cetak QR Code Carpet")
    st.caption("Sistem pengurusan cetakan tag stiker QR Carpet (Format Kertas A6 Grid).")

    # Ambil data dari Google Sheets
    data_t = t_tempahan.get_all_values() if t_tempahan else []
    data_k = t_karpet.get_all_values() if t_karpet else []
    data_p = t_pelanggan.get_all_values() if t_pelanggan else []

    if len(data_t) <= 1:
        st.info("ℹ️ Tiada data tempahan aktif ditemui buat masa ini.")
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
            st.warning("⚠️ Tiada pecahan data karpet dijumpai untuk nombor invoice ini di dalam tab 'Karpet'.")
            return

        # 1. PAPARAN JADUAL PREVIEW DATA
        st.markdown(f"### 📊 2. Senarai Karpet Dalam Invoice Ini")
        st.dataframe(df_pecahan_karpet, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.markdown(f"### 📑 3. Pratonton Halaman Cetakan A6 ({len(df_pecahan_karpet)} Stiker)")

        # 2. BINA STRUKTUR GRID KERTAS A6
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
                    body {{ background: none; }}
                    .halaman-a6-container {{ width: 100mm; height: 150mm; padding: 0; margin: 0; }}
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

        # Papar komponen kotak pratonton di Streamlit
        st.components.v1.html(html_kertas_a6_lengkap, height=580, scrolling=True)
        st.markdown("---")

        # ===================================================================
        # 3. HELAH PINTAR: BUTANG PENCETUS PDF BAWAAN TELEFON & LAPTOP
        # ===================================================================
        st.markdown("### 🖨️ Tindakan Cetakan:")
        
        # Butang ini akan membuka tetingkap cetakan bersih yang mesra peranti mudah alih (telefon)
        # Di telefon, ia akan mencetuskan dialog sistem "Save as PDF" secara automatik bersaiz A6
        html_butang_cetak_pintar = f"""
        <script>
        function bukaTetingkapCetak() {{
            var tetingkap = window.open('', '_blank', 'width=600,height=800');
            tetingkap.document.write(`{html_kertas_a6_lengkap}`);
            tetingkap.document.close();
            tetingkap.focus();
            setTimeout(function() {{
                tetingkap.print();
                tetingkap.close();
            }}, 500);
        }}
        </script>
        <button onclick="bukaTetingkapCetak()" style="width: 100%; background-color: #00cc66; color: white; border: none; padding: 14px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-bottom: 10px;">
            🖨️ Cetak / Simpan Sebagai PDF (Sesuai Untuk Telefon & Laptop)
        </button>
        """
        st.components.v1.html(html_butang_cetak_pintar, height=70)
