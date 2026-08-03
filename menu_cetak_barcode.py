import streamlit as st
import pandas as pd
import qrcode
import io
import base64

@st.cache_data(ttl=600)
def fetch_data(_worksheet):
    return _worksheet.get_all_values()

# Fungsi Jana Gambar QR
def jana_gambar_qr(teks_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(teks_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer_memori = io.BytesIO()
    img.save(buffer_memori, format="PNG")
    kod_imej_digital = base64.b64encode(buffer_memori.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{kod_imej_digital}"

# Fungsi Utama Paparan Menu System
def papar_menu_cetak_barcode(t_tempahan, t_karpet, t_pelanggan):
    st.title("🖨 Cetak QR Code Carpet")
    st.caption("Sistem cetakan tag stiker QR (40mm x 30mm).")

    # Ambil dan tukar data kepada DataFrame
    data_t = t_tempahan.get_all_values() if t_tempahan else []
    data_k = t_karpet.get_all_values() if t_karpet else []
    
    if len(data_t) <= 1:
        st.info("ℹ Tiada data tempahan aktif.")
        return

    df_t = pd.DataFrame(data_t[1:], columns=data_t[0])
    df_k = pd.DataFrame(data_k[1:], columns=data_k[0])

    # Pilihan Invois
    pilihan_dropdown = ["-- Sila Pilih Invoice --"] + df_t.iloc[:, 0].unique().tolist()
    inv_sebenar = st.selectbox("🎯 1. Pilih Nombor Invoice:", pilihan_dropdown)

    if inv_sebenar != "-- Sila Pilih Invoice --":
        # Tapis data karpet
        df_pecahan_karpet = df_k[df_k.iloc[:, 1] == inv_sebenar]

        if df_pecahan_karpet.empty:
            st.warning("⚠ Tiada data karpet untuk invois ini.")
            return

        st.markdown(f"### 📊 2. Senarai Karpet")
        st.dataframe(df_pecahan_karpet, use_container_width=True, hide_index=True)

        # Jana HTML Stiker 40mm x 30mm
        html_semua_stiker = ""
        for _, row_k in df_pecahan_karpet.iterrows():
            qr_id_karpet = str(row_k.iloc[0]).strip()
            kod_saiz = str(row_k.iloc[2]).strip()
            imej_qr_base64 = jana_gambar_qr(qr_id_karpet)
            html_semua_stiker += f"""
            <div class="stiker-box" style="width:40mm; height:30mm; border:1px dashed #000; padding:1.5mm; box-sizing:border-box; text-align:center; page-break-after:always;">
                <div style="font-size:6px; font-weight:bold;">MYCARPET PRO v2.0</div>
                <div style="font-size:7px; font-weight:bold;">INV: {inv_sebenar}</div>
                <img src="{imej_qr_base64}" style="width:100%; height:11mm; object-fit:contain;">
                <div style="font-size:5.5px; font-weight:bold;">QR ID: {qr_id_karpet}</div>
                <div style="font-size:5px; border-top:0.5px solid #000;">KOD: {kod_saiz}</div>
            </div>
            """

        html_final = f"<html><body>{html_semua_stiker}</body></html>"
        st.components.v1.html(html_final, height=350, scrolling=True)

        # Butang Cetak
        st.markdown("### 🖨 Tindakan Cetakan:")
        if st.button("Cetak / Simpan Sebagai PDF"):
            st.components.v1.html(f"<script>window.print();</script>", height=0)

# Panggil fungsi (Asumsi `t_tempahan`, `t_karpet`, `t_pelanggan` didefinisikan)
# papar_menu_cetak_barcode(t_tempahan, t_karpet, t_pelanggan)
