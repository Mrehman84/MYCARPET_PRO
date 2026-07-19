import streamlit as st
import gspread



def inisial_database_segar():
    try:
        from google.oauth2 import service_account

        info_kredensial = st.secrets["gspread"]
                
        gc = gspread.auth.service_account_from_dict(info_kredensial)

        kredensial = gspread.service_account.Credentials.from_service_account_info(
            info_kredensial, scopes=skop
        )

        # Buka fail utama menggunakan URL aktif anda
        url_sheet = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=205062829#gid=205062829"
        buka_fail = gc.open_by_url(url_sheet)

        tab_harga = buka_fail.worksheet("SENARAI_HARGA")
        t_pelanggan = buka_fail.worksheet("Pelanggan")
        t_tempahan = buka_fail.worksheet("Tempahan")
        t_karpet = buka_fail.worksheet("Karpet")

        return tab_harga, t_pelanggan, t_tempahan, t_karpet
    except Exception as e:
        st.error(f"❌ Gagal menyambung ke Google Sheets: {e}")
        return None, None, None, None
