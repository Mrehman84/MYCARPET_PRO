import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def papar_menu_payment():
    st.title("💳 Pengurusan Pembayaran & Invois")
    st.info("Sistem menarik data daripada Tab Tempahan secara live dan merekodkan status ke dalam Tab Payment.")

    # 1. SAMBUNGAN DATABASE GOOGLE SHEETS (SELAMAT & TERASING)
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Menggunakan fail kunci rahsia yang sedia ada dalam projek abang
        creds = Credentials.from_service_account_file("kunci_rahsia.json", scopes=scope)
        gc = gspread.authorize(creds)
        
        # GANTIKAN BARIS 19 DENGAN PAUTAN URL SEBENAR INI:
        url_sheet = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=667279755#gid=667279755"
        sh = gc.open_by_url(url_sheet)

        t_tempahan = sh.worksheet("Tempahan")
        t_payment = sh.worksheet("Payment")
        t_customer = sh.worksheet("Pelanggan")
        t_karpet = sh.worksheet("Karpet")

    except Exception as e:
        st.error(f"⚠️ Gagal bersambung ke Google Sheets. Sila pastikan nama fail 'MYCARPET_PRO' dan 'kunci rahsia.json' adalah betul. Ralat: {e}")
        st.stop()

        # # 2. AMBIL DATA MENTAH DARI 4 TAB GOOGLE SHEETS
    data_tempahan_mentah = t_tempahan.get_all_values()
    data_payment_mentah = t_payment.get_all_values()
    data_customer_mentah = t_customer.get_all_values()
    data_karpet_mentah = t_karpet.get_all_values()

    # # --- PENUKARAN KEPADA DATAFRAME PYTHON & PEMBERSIHAN HEADER ---
    df_tempahan = pd.DataFrame()
    if len(data_tempahan_mentah) > 1:
        df_tempahan = pd.DataFrame(data_tempahan_mentah[1:], columns=data_tempahan_mentah[0])
        df_tempahan.columns = [str(c).upper().strip() for c in df_tempahan.columns]

    df_payment = pd.DataFrame()
    if len(data_payment_mentah) > 1:
        df_payment = pd.DataFrame(data_payment_mentah[1:], columns=data_payment_mentah[0])
        df_payment.columns = [str(c).upper().strip() for c in df_payment.columns]

    df_customer = pd.DataFrame()
    if len(data_customer_mentah) > 1:
        df_customer = pd.DataFrame(data_customer_mentah[1:], columns=data_customer_mentah[0])
        df_customer.columns = [str(c).upper().strip() for c in df_customer.columns]

    df_karpet = pd.DataFrame()
    if len(data_karpet_mentah) > 1:
        df_karpet = pd.DataFrame(data_karpet_mentah[1:], columns=data_karpet_mentah[0])
        df_karpet.columns = [str(c).upper().strip() for c in df_karpet.columns]

    # # 3. SEMAK KEWUJUDAN LAJUR UTAMA & BINA DROPDOWN HUBUNGAN SILANG TAB
    if 'INV NO' in df_tempahan.columns:
        
        # Membina senarai pilihan dropdown dengan memadankan Alamat dari tab Customer
        senarai_invoice = []
        for idx, row in df_tempahan.iterrows():
            c_inv = row.get('INV NO', '-')
            c_cust_id = row.get('CUSTOMER ID', row.get('CUSTOMER_ID', '-'))
            
            c_alamat = ""
            if not df_customer.empty and c_cust_id != "-":
                c_match = df_customer[df_customer['CUSTOMER ID'] == c_cust_id]
                if not c_match.empty:
                    c_alamat = c_match.iloc[0].get('ALAMAT', '')
            
            teks_pilihan = f"{c_inv} | {c_alamat}" if c_alamat else str(c_inv)
            senarai_invoice.append(teks_pilihan)

        # # PETAK PILIHAN DROPDOWN UTAMA ATAS SCREEN
        invoice_dipilih = st.selectbox("Cari & Pilih Nombor Invois / Alamat Pelanggan:", senarai_invoice)

        # Mengambil nombor invois asli sahaja (Contoh: Ambil "INV0003")
        v_no_invoice = invoice_dipilih.split(" | ")[0] if " | " in str(invoice_dipilih) else str(invoice_dipilih)

        # Mencari baris data asal dari tab Tempahan berdasarkan INV NO asli
        df_terpilih = df_tempahan[df_tempahan['INV NO'] == v_no_invoice]
        
        if not df_terpilih.empty:
            p_match = df_terpilih  # Menyediakan p_match untuk rujukan kod HTML bawah
            row_terpilih = df_terpilih.iloc[0]
            
            v_cust_id = row_terpilih.get('CUSTOMER ID', row_terpilih.get('CUSTOMER_ID', '-'))
            v_tarikh_masuk = row_terpilih.get('TARIKH', '-')
            
            # Membaca harga dan membuang teks 'RM' serta spasi kosong secara automatik
            harga_raw = str(row_terpilih.get('JUMLAH HARGA', row_terpilih.get('TOTAL', '0.00')))
            harga_clean = harga_raw.upper().replace('RM', '').strip()
            v_jumlah_invoice = float(harga_clean) if harga_clean else 0.00


            # Menarik data peribadi secara live dari tab Customer berdasarkan v_cust_id
            v_nama = "-"
            v_no_tel = "-"
            v_alamat = "-"
            if not df_customer.empty and v_cust_id != "-":
                cust_lookup = df_customer[df_customer['CUSTOMER ID'] == v_cust_id]
                if not cust_lookup.empty:
                    row_cust = cust_lookup.iloc[0]
                    v_nama = row_cust.get('NAMA', '-')
                    v_no_tel = row_cust.get('TELEFON', row_cust.get('NO TELEFON', '-'))
                    v_alamat = row_cust.get('ALAMAT', '-')


        # === SAMBUNGAN KOD SEMALAM (MENU 4: PAYMENT) ===
        # Membaca maklumat harga dan nama daripada carian di atas
        if not df_terpilih.empty:
            st.success(f"✅ Data Invois {v_no_invoice} Berjaya Ditemui!")
            
            # 1. PAPAR MAKLUMAT PELANGGAN & INVOIS
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nama Pelanggan:** {v_nama}")
                st.markdown(f"**No. Telefon:** {v_no_tel}")
                st.markdown(f"**Alamat:** {v_alamat}")
            with col2:
                st.markdown(f"**Tarikh Tempahan:** {v_tarikh_masuk}")
                st.markdown(f"### **Jumlah Invois: RM {v_jumlah_invoice:.2f}**")

            st.divider()

            # 2. BORANG INPUT PEMBAYARAN BARU
            st.subheader("💳 Borang Kemas Kini Pembayaran")
            
            with st.form("borang_pembayaran"):
                v_kaedah_bayar = st.selectbox(
                    "Pilih Kaedah Pembayaran:",
                    ["TUNAI (CASH)", "TRANSFER BANK", "QR PAY", "KAD KREDIT/DEBIT"]
                )
                
                v_amaun_dibayar = st.number_input(
                    "Masukkan Amaun yang Dibayar (RM):", 
                    min_value=0.00, 
                    value=float(v_jumlah_invoice), 
                    step=0.50
                )
                
                v_nota = st.text_area("Nota Tambahan (Jika ada):", placeholder="Contoh: Bayaran penuh / Deposit")
                
                # Butang Hantar Borang
                butang_bayar = st.form_submit_button("Sahkan & Rekod Pembayaran")

            # 3. PROSES SIMPAN DATA KE TAB 'PAYMENT' GOOGLE SHEETS
            if butang_bayar:
                if v_amaun_dibayar < v_jumlah_invoice:
                    st.warning(f"⚠ Amaran: Amaun dibayar (RM {v_amaun_dibayar:.2f}) kurang daripada jumlah invois (RM {v_jumlah_invoice:.2f}).")
                        
            # Ambil nilai deposit lama daripada rekod pmatch jika ada
                v_deposit_lama = 0.0
                if not p_match.empty:
                    try:
                        # Membaca nilai DEPOSIT sedia ada pada baris pertama yang ditemui
                        v_deposit_lama = float(str(p_match.iloc[0].get('DEPOSIT', p_match.iloc[0].get('JUMLAH BAYARAN', 0))).replace("RM", "").strip())
                    except:
                        v_deposit_lama = 0.0

                # Formula baki baharu: Jumlah keseluruhan ditolak deposit lama dan ditolak amaun baharu yang dibayar sekarang
                v_baki = v_jumlah_invoice - v_deposit_lama - v_amaun_dibayar
                v_status_bayar = "PAID" if v_baki <= 0 else "PARTIAL"
                v_masa_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Susunan baris data baru untuk dimasukkan ke tab Payment
                baris_baru = [
                    v_no_invoice,      # INV NO
                    v_cust_id,         # CUSTOMER ID
                    v_nama,            # NAMA
                    v_jumlah_invoice,  # JUMLAH INVOIS
                    v_amaun_dibayar,   # AMAUN DIBAYAR
                    v_baki,            # BAKI
                    v_kaedah_bayar,    # KAEDAH PEMBAYARAN
                    v_status_bayar,    # STATUS
                    v_masa_sekarang,   # TARIKH BAYARAN
                    v_nota             # NOTA
                ]

                try:
                    # Masukkan data ke baris paling bawah dalam Tab Payment Google Sheets
                    t_payment.append_row(baris_baru)
                    st.success(f"🎉 Pembayaran untuk Invois {v_no_invoice} berjaya direkodkan ke Google Sheets!")
                    
                    # Kira baki untuk paparan skrin
                    if v_baki > 0:
                        st.info(f"Baki tunggakan yang perlu dibayar: RM {v_baki:.2f}")
                    elif v_baki < 0:
                        st.success(f"Pulangan baki kepada pelanggan: RM {abs(v_baki):.2f}")
                        
                except Exception as e:
                    st.error(f"❌ Gagal menyimpan data ke Google Sheets. Ralat: {e}")
        else:
            st.error("❌ Tiada data tempahan dijumpai untuk nombor invois ini.")


                
        # SEMAK STATUS ASAL DARI TAB PAYMENT (Anti-Tindih)
        status_asal = "PENDING"
        kaedah_asal = "PENDING"
        index_status_default = 0
                
        if not df_payment.empty and 'INV NO' in df_payment.columns:
            p_match = df_payment[df_payment['INV NO'].astype(str).str.strip().str.upper() == str(v_no_invoice).strip().upper()]

            if not p_match.empty:
                status_asal = str(p_match.iloc[0].get('STATUS BAYARAN', 'PENDING')).upper().strip()
                kaedah_asal = p_match.iloc[0].get('KAEDAH BAYARAN', 'PENDING')
                if status_asal == "PAID":
                    index_status_default = 1

                st.markdown("---")
                st.subheader(f"⚙️ Kawalan Status Dokumen: {v_no_invoice}")
                
               

        

