import streamlit as st
import gspread



def inisial_database_segar():
    try:
        info_kredensial = st.secrets["gspread"]
                  
        gc = gspread.service_account_from_dict(info_kredensial)

        # Buka fail utama menggunakan URL aktif anda
        url_sheet = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=1251116694#gid=1251116694"
        buka_fail = gc.open_by_url(url_sheet)

        tab_harga = buka_fail.worksheet("SENARAI_HARGA")
        t_pelanggan = buka_fail.worksheet("Pelanggan")
        t_tempahan = buka_fail.worksheet("Tempahan")
        t_karpet = buka_fail.worksheet("Karpet")

        return tab_harga, t_pelanggan, t_tempahan, t_karpet
    except Exception as e:
        st.error(f"❌ Gagal menyambung ke Google Sheets: {e}")
        return None, None, None, None
