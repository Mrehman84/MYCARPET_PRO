import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

def app():
    st.title("📊 Lejar Kewangan My Carpet Pro")
    st.markdown("---")
    
    try:
        client = get_gsheet_client()
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xCSGuFUQjSp33kRSSOJpYP2AIMKdTemg5wWi8jyPm_o/edit?gid=677693224#gid=677693224")
        tetapan_sheet = sheet.worksheet("Tetapan_Sistem")
        data_tetapan = tetapan_sheet.get_all_records()
        df_tetapan = pd.DataFrame(data_tetapan)
        senarai_bank = [x for x in df_tetapan["Akaun_Bank"].tolist() if x]
        senarai_belanja = [x for x in df_tetapan["Kod_Belanja"].tolist() if x]
    except Exception as e:
        st.error(f"Gagal menyambung ke Google Sheet: {e}")
        return

     # Inisialisasi struktur barang dalam session state jika belum wujud
    if "senarai_barang" not in st.session_state:
        st.session_state.senarai_barang = [{"jenis": "", "kod": senarai_belanja[0], "qty": 1, "uom": "LITER", "harga": 0.0}]

    # Fungsi interaktif untuk butang tambah/buang barang
    def tambah_baris_barang():
        st.session_state.senarai_barang.append({"jenis": "", "kod": senarai_belanja[0], "qty": 1, "uom": "LITER", "harga": 0.0})

    def buang_baris_barang(index):
        if len(st.session_state.senarai_barang) > 1:
            st.session_state.senarai_barang.pop(index)

    # 🧹 FUNGSI MENGOSONGKAN BORANG
    def kosongkan_borang():
        for idx in range(len(st.session_state.senarai_barang)):
            if f"jenis_{idx}" in st.session_state:
                st.session_state[f"jenis_{idx}"] = ""
            if f"qty_{idx}" in st.session_state:
                st.session_state[f"qty_{idx}"] = 1
            if f"harga_{idx}" in st.session_state:
                st.session_state[f"harga_{idx}"] = 0.0
        st.session_state.senarai_barang = [{"jenis": "", "kod": senarai_belanja[0], "qty": 1, "uom": "LITER", "harga": 0.0}]

    # 📥 MULA FORM: Mengunci semua input supaya STATIK
    with st.form(key="borang_kewangan_utama", clear_on_submit=True):
        st.subheader("Borang Resit Pembekal (Sistem Pecahan Barang)")
        
        tarikh = st.date_input("1. Tarikh Perbelanjaan", datetime.now())
        no_resit = st.text_input("2. Nombor Resit / Invois Pembekal", placeholder="cth: INV-99823 / CSH-102")
        akaun_pilihan = st.selectbox("3. Bayar Melalui (Akaun Dipotong)", senarai_bank)
        supplier = st.text_input("4. Nama Pembekal / Kedai (Supplier)", placeholder="cth: Kedai Kimia Jaya")
        catatan_resit = st.text_area("5. Catatan Resit Keseluruhan (Opsional)")
        st.markdown("---")
        
        st.subheader("📦 Pecahan Senarai Barang Berbilang")
        
        jumlah_kasar_resit = 0.0
        for idx, barang in enumerate(st.session_state.senarai_barang):
            st.markdown(f"**🛒 Item #{idx + 1}**")
            
            st.session_state.senarai_barang[idx]["jenis"] = st.text_input(
                f"Nama Barang #{idx+1}", value=barang["jenis"], key=f"jenis_{idx}", placeholder="cth: Sabun Ultra Foam"
            )
            st.session_state.senarai_barang[idx]["kod"] = st.selectbox(
                f"Kod Perbelanjaan #{idx+1}", senarai_belanja, index=senarai_belanja.index(barang["kod"]), key=f"kod_{idx}"
            )
            
            col_qty, col_uom = st.columns(2)
            with col_qty:
                st.session_state.senarai_barang[idx]["qty"] = st.number_input(
                    f"Kuantiti #{idx+1}", min_value=1, value=barang["qty"], key=f"qty_{idx}"
                )
            with col_uom:
                st.session_state.senarai_barang[idx]["uom"] = st.selectbox(
                    f"Unit Ukuran #{idx+1}", ["LITER", "KG", "ROLL", "PCS", "HELAI", "UNIT"], 
                    index=["LITER", "KG", "ROLL", "PCS", "HELAI", "UNIT"].index(barang["uom"]), key=f"uom_{idx}"
                )
                
            st.session_state.senarai_barang[idx]["harga"] = st.number_input(
                f"Harga Seunit RM #{idx+1}", min_value=0.0, value=barang["harga"], format="%.2f", key=f"harga_{idx}"
            )
            
            subtotal_item = st.session_state.senarai_barang[idx]["qty"] * st.session_state.senarai_barang[idx]["harga"]
            jumlah_kasar_resit += subtotal_item
            st.markdown(f"*Subtotal Kos Asal #{idx+1}: RM {subtotal_item:.2f}*")
            st.markdown("---")

        st.subheader("💰 Rumusan Kos & Pengiraan Caj")
        caj_pos = st.number_input("6. Caj Penghantaran / Kos Postage (RM)", min_value=0.0, format="%.2f")
        
        simpan_klik = st.form_submit_button("🚀 SIMPAN SELURUH RESIT MASUK LEJAR", use_container_width=True)

    # 🛒 BUTANG LUAR FORM
    col_tambah, col_buang = st.columns(2)
    with col_tambah:
        st.button("➕ TAMBAH KOTAK ITEM", on_click=tambah_baris_barang, use_container_width=True)
    with col_buang:
        if len(st.session_state.senarai_barang) > 1:
            st.button("🗑️ BUANG ITEM TERAKHIR", on_click=buang_baris_barang, args=(len(st.session_state.senarai_barang)-1,), use_container_width=True)

    # ⚙️ PROSES SIMPAN DATA
    if simpan_klik:
        borang_sah = True
        for b in st.session_state.senarai_barang:
            if not b["jenis"] or b["harga"] <= 0:
                borang_sah = False
                
        if not no_resit:
            st.warning("Sila masukkan Nombor Resit/Invois Pembekal untuk pengikat kumpulan data.")
        elif not supplier:
            st.warning("Sila masukkan nama pembekal syarikat.")
        elif not borang_sah:
            st.warning("Sila pastikan semua Nama Barang telah diisi dan Harga Seunit adalah lebih daripada RM0.00.")
        else:
            with st.spinner("Sistem sedang mengira agihan caj kos per unit dan menulis ke lejar..."):
                try:
                    expenses_sheet = sheet.worksheet("Raw_Expenses")
                    all_values = expenses_sheet.get_all_values()
                    
                    next_id = len(all_values)
                    
                    bulan_tahun_str = tarikh.strftime("%b%Y").upper()
                    kod_gabungan = f"{akaun_pilihan}{bulan_tahun_str}"
                    baris_pukal_resit = []
                    
                    for item in st.session_state.senarai_barang:
                        subtotal_kos_asal = item["qty"] * item["harga"]
                        
                        if jumlah_kasar_resit > 0:
                            nisbah_agihan_pos = (subtotal_kos_asal / jumlah_kasar_resit) * caj_pos
                        else:
                            nisbah_agihan_pos = 0.0
                            
                        amount_bersih_item = subtotal_kos_asal + nisbah_agihan_pos
                        
                        row_data = [
                            next_id,
                            tarikh.strftime("%d/%m/%Y"),
                            akaun_pilihan,
                            item["jenis"].upper(),
                            item["qty"],
                            item["harga"],
                            item["uom"],
                            item["kod"],
                            round(amount_bersih_item, 2),
                            supplier.upper(),
                            f"{catatan_resit} | No Resit: {no_resit.upper()}".strip(" | "),
                            "",
                            kod_gabungan
                        ]
                        baris_pukal_resit.append(row_data)
                        next_id += 1
                        
                    expenses_sheet.append_rows(baris_pukal_resit)
                    
                    # Memanggil fungsi pembersihan di posisi inden blok 'try' yang betul
                    kosongkan_borang()
                    st.success(f"🎉 Berjaya! Seluruh resit '{no_resit.upper()}' telah dimasukkan. Borang telah dikosongkan semula.")
                    st.rerun()
                    
                except Exception as err:
                    st.error(f"Gagal menyimpan transaksi resit: {err}")

if __name__ == "__main__":
    app()