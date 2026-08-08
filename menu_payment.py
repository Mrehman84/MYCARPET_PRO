import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pakar_kewangan

#=================================================
#20/7/2026 tambahkan code menu kewangan. yg mana ada tanda 20/7 adalah code baru
#================================================================================
# ----------------------------------------------------------------------
# TAMBAHAN SUNTIKAN SISTEM LEJAR KEWANGAN SECARA TERASING (JANGAN USIK KOD ASAL)
# ----------------------------------------------------------------------
def hantar_ke_lejar_revenue(id_invois, nama_pelanggan, saluran_masuk, amount_dibayar, jenis_bayaran):
    try:
        # Hubungkan ke Google Sheet baru menggunakan kunci rahsia kewangan
        scope = ["https://googleapis.com", "https://googleapis.com"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account_finance"], scopes=scope)

        client = gspread.authorize(creds)
        sheet = client.open("https://docs.google.com/spreadsheets/d/1xCSGuFUQjSp33kRSSOJpYP2AIMKdTemg5wWi8jyPm_o/edit?gid=314909126#gid=314909126")
        revenue_sheet = sheet.worksheet("Raw_Revenue")
        
        all_values = revenue_sheet.get_all_values()
        tarikh_sekarang = datetime.now()
        
        # Standarisasi nama saluran masuk agar sepadan dengan drop-down lejar
        saluran_bersih = "TUNAI" if "TUNAI" in str(saluran_masuk).upper() else str(saluran_masuk).upper()
        
        # Jika sheet lejar masih kosong, bina header otomatis dahulu
        if len(all_values) == 0:
            headers = ["NO", "TARIKH", "ID_INVOIS", "PELANGGAN", "SALURAN_MASUK", "KATEGORI_SERVIS", "AMOUNT", "CATATAN", "GABUNGAN"]
            revenue_sheet.append_row(headers)
            next_id = 1
        else:
            next_id = len(all_values)
            
        # Logik lejar: Generasi kod gabungan otomatis bulanan
        bulan_tahun_str = tarikh_sekarang.strftime("%b%Y") # Hasil cth: Jul2026
        kod_gabungan = f"{saluran_bersih}{bulan_tahun_str}" # Hasil cth: TUNAIJul2026
        
        catatan_lejar = f"Bayaran {jenis_bayaran} untuk Invois {id_invois}"
        
        row_data = [
            next_id,
            tarikh_sekarang.strftime("%d/%m/%Y"),
            id_invois,
            nama_pelanggan,
            saluran_bersih,
            "CUCI KARPET",  # Fasa awal: Set default cuci carpet sahaja
            float(amount_dibayar),
            catatan_lejar,
            kod_gabungan
        ]
        
        revenue_sheet.append_row(row_data)
        return True, kod_gabungan
    except Exception as e:
        return False, str(e)
# ----------------------------------------------------------------------

def papar_menu_payment():
    st.title("💳 Pengurusan Pembayaran & Invois")
    st.info("Sistem menarik data daripada Tab Tempahan secara live dan merekodkan status ke dalam Tab Payment.")

    # 1. SAMBUNGAN DATABASE GOOGLE SHEETS (SELAMAT & TERASING)
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Menggunakan fail kunci rahsia yang sedia ada dalam projek abang
        # GANTIKAN BARIS 15 DENGAN KOD INI:
        info_kredensial = st.secrets["gspread"]
        creds = Credentials.from_service_account_info(info_kredensial, scopes=scope)
            
            # PERIKSA BARIS INI: Pastikan baris di bawah ini ada dan tidak terpadam!
        gc = gspread.authorize(creds)
            
            # GANTIKAN BARIS 19 DENGAN PAUTAN URL SEBENAR INI:
        url_sheet = "https://docs.google.com/spreadsheets/d/1AAszxb_8Rbvb9ruXCVL_vQN12NME0eHYEtxqMj6OIRo/edit?gid=0#gid=0"
        sh = gc.open_by_url(url_sheet)

        t_tempahan = sh.worksheet("Tempahan")
        t_payment = sh.worksheet("Payment")
        t_customer = sh.worksheet("Pelanggan")
        t_karpet = sh.worksheet("Karpet")

    except Exception as e:
        st.error(f"⚠️ Gagal bersambung ke Google Sheets. Sila pastikan nama fail 'MYCARPET_PRO' dan 'kunci_google.json' adalah betul. Ralat: {e}")
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
            
        # AMBIL DATA DEPOSIT DAN BAKI DARI TAB PAYMENT UNTUK DIPAPARKAN DI ATAS
        try:
            p_match_payment = df_payment[df_payment['INV NO'] == v_no_invoice]
            if not p_match_payment.empty:
                v_deposit_papar = p_match_payment.iloc[-1].get('AMAUN DIBAYAR', 0.0)
                v_baki_papar = p_match_payment.iloc[-1].get('BAKI', 0.0)
            else:
                v_deposit_papar = 0.0
                v_baki_papar = v_jumlah_invoice
        except:
            v_deposit_papar = 0.0
            v_baki_papar = v_jumlah_invoice

        # 1. PAPAR MAKLUMAT PELANGGAN & INVOIS
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Nama Pelangan:** {v_nama}")
            st.markdown(f"**No. Telefon:** {v_no_tel}")
            st.markdown(f"**Alamat:** {v_alamat}")
        with col2:
            st.markdown(f"**Tarikh Tempahan:** {v_tarikh_masuk}")
            st.markdown(f"### Jumlah Invois: RM {v_jumlah_invoice:.2f}")
            st.markdown(f"##### Deposit Dibayar: RM {float(v_deposit_papar):.2f}")
            st.markdown(f"##### Baki Semasa: RM {float(v_baki_papar):.2f}")

        st.divider()


            # 2. BORANG INPUT PEMBAYARAN BARU
        st.subheader("💳 Borang Kemas Kini Pembayaran")
            
    with st.form("borang_pembayaran"):
        v_kaedah_bayar = st.selectbox(
            "Pilih Kaedah Pembayaran:",
            ["TUNAI (CASH)", "TRANSFER BANK", "QR PAY", "KAD KREDIT/DEBIT"]
        )

        # 1. CARI INVOIS INI DI DALAM TAB PAYMENT UNTUK AMBIL BAKI TERKINI
        try:
            p_match_payment = df_payment[df_payment['INV NO'] == v_no_invoice]
            if not p_match_payment.empty:
                v_baki_semasa = p_match_payment.iloc[-1].get('BAKI', 0.0)
            else:
                v_baki_semasa = v_jumlah_invoice
        except Exception as e:
            v_baki_semasa = v_jumlah_invoice

        # 2. FORMAT NILAI LALAI UNTUK INPUT NOMBOR
        try:
            nilai_baki_default = float(v_baki_semasa)
        except:
            nilai_baki_default = float(v_jumlah_invoice)

        # 3. PAPARKAN KOTAK INPUT NOMBOR DI DALAM FORM
        v_amaun_dibayar = st.number_input(
            "Masukkan Amaun yang Dibayar (RM):",
            min_value=0.00,
            value=nilai_baki_default,
            step=0.50
        )

        # 4. BUTANG SUBMIT DI DALAM FORM (WAJIB MASUK 8 SPASI KE DALAM)
        butang_hantar = st.form_submit_button("Kemas Kini Pembayaran")


            # 3. PROSES SIMPAN DATA KE TAB 'PAYMENT' GOOGLE SHEETS
        if butang_hantar:
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
                v_baki = nilai_baki_default - v_amaun_dibayar 
                v_status_bayar = "PAID" if v_baki <= 0 else "DEPOSIT" 

                # GUNA PANDAS TIMESTAMP: Kebal ralat import
                v_masa_sekarang = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                v_nota = "" 

                # Susunan baris data baru untuk dimasukkan ke tab Payment 
                baris_baru = [ 
                    v_no_invoice,      # INV NO 
                    v_cust_id,        # CUSTOMER ID 
                    v_nama,           # NAMA 
                    v_jumlah_invoice, # JUMLAH INVOIS 
                    v_amaun_dibayar,  # AMAUN DIBAYAR 
                    v_baki,           # BAKI 
                    v_kaedah_bayar,   # KAEDAH PEMBAYARAN 
                    v_status_bayar,   # STATUS 
                    v_masa_sekarang,  # TARIKH BAYARAN 
                    v_nota            # NOTA 
                ] 

                try: 
                    # 1. MASUKKAN KE TAB PAYMENT (FAIL OPERASI - ASAL)
                    t_payment.append_row(baris_baru) 
                    st.success(f"🎉 Pembayaran untuk Invois {v_no_invoice} berjaya direkodkan ke Google Sheets!") 

                    # ====================================================================
                    # 🚀 2. SUNTIKAN TERUS REAL-TIME: MASUKKAN KE TAB RAW_REVENUE (FAIL FINANCE)
                    # ====================================================================
                    try:
                        import config
                        
                        # Hubung terus fail kewangan menggunakan URL dalam config
                        client_finance = config.hubung_google_sheets()
                        sheet_finance = client_finance.open_by_url(config.URL_FINANCE_SHEET)
                        ws_revenue = sheet_finance.worksheet("Raw_Revenue")
                        
                        # Ambil baris terakhir di Raw_Revenue untuk jana ID No baharu secara auto
                        data_rev_skrg = ws_revenue.get_all_values()
                        no_turutan_f = 1
                        if len(data_rev_skrg) > 1:
                            try:
                                no_turutan_f = int(data_rev_skrg[-1]) + 1
                            except:
                                no_turutan_f = len(data_rev_skrg)
                        
                        # Menggunakan 100% nama pembolehubah borang asal anda
                        harga_f = str(v_amaun_dibayar).upper().replace('RM', '').strip()
                        # Ditukar supaya mengambil alamat penuh pelanggan untuk Lajur D
                        pelanggan_f = v_alamat if 'v_alamat' in locals() else "-"

                        saluran_f = "MAYBANK" if "TRANSFER" in str(v_kaedah_bayar).upper() or "BANK" in str(v_kaedah_bayar).upper() else "TUNAI"
                        
                        # Set format tarikh lejar DD/MM/YYYY secara automatik mengikut waktu semasa
                        tarikh_f = pd.Timestamp.now().strftime("%d/%m/%Y")
                        bulan_tahun_f = pd.Timestamp.now().strftime("%b%Y").upper()
                        gabungan_kod_f = f"{saluran_f}{bulan_tahun_f}"
                        
                        # Susunan baris mengikut jalur lejar kewangan anda (Lajur A hingga I)
                        baris_suntikan_finance = [[
                            no_turutan_f,                   # Lajur A (NO)
                            tarikh_f,                       # Lajur B (TARIKH)
                            str(v_no_invoice).upper(),      # Lajur C (ID_INVOIS)
                            pelanggan_f,                    # Lajur D (PELANGGAN)
                            saluran_f,                      # Lajur E (SALURAN_MASUK)
                            "CUCI KARPET",                  # Lajur F (KATEGORI_SERVIS)
                            harga_f,                        # Lajur G (AMOUNT)
                            f"Auto-Direct: Invois {v_no_invoice}", # Lajur H (CATATAN)
                            gabungan_kod_f                  # Lajur I (GABUNGAN)
                        ]]
                        
                        # Tembak masuk serta-merta tanpa perlu scan memori yang berat!
                        ws_revenue.append_rows(baris_suntikan_finance, value_input_option="USER_ENTERED")
                        st.toast("💻 Auto-Sync: Data berjaya dihantar ke Lejar Kewangan!", icon="📊")
                        
                    except Exception as err_suntik:
                        # Jika kewangan ada ralat sekatan, cetak di log belakang dan jangan sekat transaksi kedai
                        print(f"⚠️ Amaran: Gagal suntik terus ke Finance: {str(err_suntik)}")
                    # ====================================================================

                    # 3. KEMASKINI STATUS 'PAID' DI TAB TEMPAHAN (FAIL OPERASI - ASAL)
                    data_tempahan_raw = t_tempahan.get_all_values() 
                    senarai_inv_tempahan = [str(r[0]).strip() for r in data_tempahan_raw] 
                    
                    if v_no_invoice in senarai_inv_tempahan: 
                        indeks_baris = senarai_inv_tempahan.index(v_no_invoice) + 1 
                        
                        if v_baki <= 0: 
                            t_tempahan.update_cell(indeks_baris, 5, "PAID") 
                            st.toast(f"Status {v_no_invoice} di Tab Tempahan telah dikemaskini ke PAID!", icon="✅") 
                        else: 
                            t_tempahan.update_cell(indeks_baris, 5, "PARTIAL") 

                except Exception as e: 
                    st.warning(f"Nota: Gagal mengemaskini status PAID di Tab Tempahan secara automatik: {e}")


        # ====================================================================
        # 🚀 ENJIN SUNTIKAN TERUS REAL-TIME (100% AUTO & RINGAN)
        # ====================================================================
                try:
                    # 1. Hubung ke fail kewangan anda secara langsung menggunakan config
                    import config
                    from datetime import datetime
                    
                    client_finance = config.hubung_google_sheets()
                    sheet_finance = client_finance.open_by_url(config.URL_FINANCE_SHEET)
                    ws_revenue = sheet_finance.worksheet("Raw_Revenue")
                    
                    # 2. Dapatkan nombor urutan terakhir di Raw_Revenue untuk baris baharu
                    data_rev = ws_revenue.get_all_values()
                    no_turutan = 1
                    if len(data_rev) > 1:
                        try:
                            no_turutan = int(data_rev[-1][0]) + 1
                        except:
                            no_turutan = len(data_rev)
                    
                    # 3. Ambil data yang sedang aktif ditaip dalam borang Streamlit anda sekarang
                    # (Sila pastikan nama pembolehubah ini sepadan dengan kod borang menu_payment anda)
                    inv_no_auto = str(no_invois_sekarang).strip().upper() # Contoh pembolehubah invois anda
                    cust_id_auto = str(id_pelanggan_sekarang).strip()
                    nama_auto = str(nama_pelanggan_sekarang).strip()
                    harga_auto = str(jumlah_bayaran_sekarang).upper().replace('RM', '').strip()
                    kaedah_auto = str(kaedah_pembayaran_sekarang).upper()
                    
                    # Tetapkan nama paparan pelanggan
                    pelanggan_auto = nama_auto if nama_auto and nama_auto != "-" else cust_id_auto
                    saluran_auto = "MAYBANK" if "TRANSFER" in kaedah_auto or "BANK" in kaed_auto else "TUNAI"
                    
                    # Format tarikh masa kini secara auto ke DD/MM/YYYY
                    tarikh_sekarang = datetime.now().strftime("%d/%m/%Y")
                    bulan_tahun_auto = datetime.now().strftime("%b%Y").upper()
                    gabungan_kod_auto = f"{saluran_auto}{bulan_tahun_auto}"
                    
                    # 4. Susun mengikut struktur jalur lejar kewangan anda (A hingga I)
                    baris_suntikan_terus = [[
                        no_turutan,                 # Lajur A (NO)
                        tarikh_sekarang,            # Lajur B (TARIKH)
                        inv_no_auto,                # Lajur C (ID_INVOIS)
                        pelanggan_auto,             # Lajur D (PELANGGAN)
                        saluran_auto,               # Lajur E (SALURAN_MASUK)
                        "CUCI KARPET",              # Lajur F (KATEGORI_SERVIS)
                        harga_auto,                 # Lajur G (AMOUNT)
                        f"Auto-Direct: Invois {v_no_invoice}", # Lajur H (CATATAN)

                        gabungan_kod_auto           # Lajur I (GABUNGAN)
                    ]]
                    
                    # 5. Tembak terus masuk ke Raw_Revenue tanpa perlu scan sheet lagi!
                    ws_revenue.append_rows(baris_suntikan_terus, value_input_option="USER_ENTERED")
                    st.toast("💻 Auto-Sync: Transaksi berjaya direkodkan terus ke Lejar Kewangan!", icon="✅")
                    
                except Exception as err_suntik:
                    # Mengeluarkan ralat nyata jika nama pembolehubah borang anda tidak sepadan
                    st.error(f"⚠️ Amaran: Data selamat di Payment, tetapi gagal suntik terus ke Finance: {str(err_suntik)}")
                # ====================================================================



             #20/7=======================================================================================================

                    # Kira baki untuk paparan skrin
                    if v_baki > 0:
                        st.info(f"Baki tunggakan yang perlu dibayar: RM {v_baki:.2f}")
                    elif v_baki < 0:
                        st.success(f"Pulangan baki kepada pelanggan: RM {abs(v_baki):.2f}")
                        
                except Exception as e:
                    st.error(f"❌ Gagal menyimpan data ke Google Sheets. Ralat: {e}")
 

                
       
               

        

