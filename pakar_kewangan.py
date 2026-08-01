import pandas as pd
import time
import config

def jalankan_proses_berpusat():
    try:
        client = config.hubung_google_sheets()
        sheet_kewangan = client.open_by_url(config.URL_FINANCE_SHEET)
        sheet_dashboard = sheet_kewangan.worksheet("DASHBOARD")
        
        # Ambil teks trigger live dari O2
           # === PENGURUSAN MASTER TAHUN KEBANGKITAN O2 ===
        # Mengambil nilai live dari Sel O2 tab DASHBOARD
        nilai_o2_mentah = sheet_dashboard.cell(2, 15).value
        
        if nilai_o2_mentah:
            try:
                # Jika dibaca nombor perpuluhan (2024.0), kita bersihkan jadi teks "2024"
                tahun_bersih = str(int(float(nilai_o2_mentah))).strip()
            except:
                tahun_bersih = str(nilai_o2_mentah).strip()
        else:
            tahun_bersih = "2026" # Nilai backup standard jika sel O2 kosong
            
        # Menetapkan semula teks_trigger asal anda supaya kod bawah tidak rosak
        teks_trigger = tahun_bersih
        print(f"📡 Enjin Berpusat: Mengesan Master Tahun O2 Aktif -> {teks_trigger}")
        # =============================================

        
        # 1. Isyarat perbelanjaan
        if "REFRESH_EXPENSES_" in teks_trigger:
            print("📊 Mengesan kemasukan perbelanjaan baharu. Memproses perbelanjaan...")
            jalankan_automasi_matriks_belanja() 
            
        # 2. Isyarat jualan / revenue baharu
        elif "REFRESH_REVENUE_" in teks_trigger:
            print("💰 Mengesan kemasukan revenue/pendapatan baharu. Memproses revenue...")
            # Masukkan nama fungsi pengiraan revenue anda di sini, contoh:
            # jalankan_automasi_matriks_revenue()
            pass
            
        # 3. Isyarat perubahan pada tab analisa jualan (Tukar tahun atau edit manual)
        elif "REFRESH_ANALISA_" in teks_trigger:
            print("📈 Mengesan perubahan pada tab analisis. Mengira semula analisis...")
            jalankan_automasi_analisis_jualan()
            # Masukkan nama fungsi pengiraan analisis jualan anda di sini, contoh:
            # jalankan_automasi_analisis_jualan()
            pass
# ... [Kekalkan kod atas anda dari Baris 8 hingga Baris 37 tepat seperti dalam gambar] ...

        else:
            print("🔄 Isyarat am dikesan. Menjalankan penyisipan penuh semua modul...")
            # 1. Jalankan modul perbelanjaan asal anda
            jalankan_automasi_matriks_belanja()
            
            # 2. 🚀 TAMBAH 2 BARIS INI: Supaya isyarat manual 'REFRESH' turut memproses jualan baharu
            migrasi_payment_ke_revenue()
            jalankan_pengira_jualan_dashboard()
            
    except Exception as e:
        print(f"❌ Ralat kritikal pengurus pusat: {str(e)}")








   
import pandas as pd
import time
from datetime import datetime
import config 

def migrasi_payment_ke_revenue():
    print("\n==========================================================")
    print(" 🛠️ SPARE PENYELENGGARAAN: RECOVERY PAYMENT -> RAW_REVENUE")
    print("KITA SUDAH ADA PAYMENT AUTO,INI HANYA BACKUP JIKA ADA DATA HILANG")
    print("==========================================================")

    
    try:
        # 1. Hubung ke Google Sheets API via config
        client = config.hubung_google_sheets()
        
        # 2. BACA FAIL FINANCE -> AMBIL SEMUA DATA SEKALIGUS (1 REQUEST SAHAJA)
        sheet_finance = client.open_by_url(config.URL_FINANCE_SHEET)
        ws_revenue = sheet_finance.worksheet("Raw_Revenue")
        data_revenue_mentah = ws_revenue.get_all_values()
        
        # Tukar data kewangan sedia ada kepada Pandas DataFrame untuk proses kilat
        invois_sudah_ada = set()
        no_turutan_terakhir = 0
        
        if len(data_revenue_mentah) > 1:
            df_rev = pd.DataFrame(data_revenue_mentah[1:], columns=data_revenue_mentah[0])
            # Ambil lajur C (ID_INVOIS) dan tukar jadi set huruf besar
            if 'ID_INVOIS' in df_rev.columns:
                invois_sudah_ada = set(df_rev['ID_INVOIS'].str.strip().str.upper().dropna().unique())
            elif len(data_revenue_mentah[1][0]) > 2: # Failback jika nama header lari
                invois_sudah_ada = set([str(b[2]).strip().upper() for b in data_revenue_mentah[1:] if len(b) > 2])
            
            # Cari ID terakhir di lajur A
            try:
                no_turutan_terakhir = int(data_revenue_mentah[-1][0])
            except:
                no_turutan_terakhir = len(data_revenue_mentah) - 1

        # 3. BACA FAIL OPERASI -> AMBIL SEMUA DATA SEKALIGUS (1 REQUEST SAHAJA)
        sheet_operasi = client.open_by_url(config.URL_OPERASI_SHEET)
        ws_payment = sheet_operasi.worksheet("Payment")
        data_payment_mentah = ws_payment.get_all_values() 
        
        if not data_payment_mentah or len(data_payment_mentah) <= 1:
            print("✨ Terminal: Tab Payment kosong.")
            return

        # 4. GUNA LOGIK MEMORI PYTHON (TIADA COUPLING GOOGLE API DI DALAM LOOP)
        baris_payment = data_payment_mentah[1:]
        baris_baru_akan_ditampal = []
        
        for baris_mentah_pay in baris_payment:
            if len(baris_mentah_pay) > 0 and any(str(sel).strip() for sel in baris_mentah_pay):
                
                inv_no_payment = str(baris_mentah_pay[0]).strip()
                
                # Langkau jika data tidak sah
                if not inv_no_payment or inv_no_payment.lower() == "inv no" or inv_no_payment == "-":
                    continue
                
                # SEMAKAN KILAT DALAM MEMORI: Jika invois tiada di Finance
                if inv_no_payment.upper() not in invois_sudah_ada:
                    no_turutan_terakhir += 1
                    
                    cust_id = str(baris_mentah_pay[1]).strip() if len(baris_mentah_pay) > 1 else ""
                    nama_pelanggan = str(baris_mentah_pay[2]).strip() if len(baris_mentah_pay) > 2 else ""
                    harga_raw = str(baris_mentah_pay[3]).strip() if len(baris_mentah_pay) > 3 else "0"
                    kaedah_bayar = str(baris_mentah_pay[6]).strip().upper() if len(baris_mentah_pay) > 6 else ""
                    tarikh_raw = str(baris_mentah_pay[8]).strip() if len(baris_mentah_pay) > 8 else ""
                    
                    harga = harga_raw.upper().replace('RM', '').strip()
                    pelanggan = nama_pelanggan if nama_pelanggan and nama_pelanggan != "-" else cust_id
                    saluran = "MAYBANK" if "TRANSFER" in kaedah_bayar or "BANK" in kaedah_bayar else "TUNAI"
                    
                    # Tukar Format Tarikh
                    tarikh_kewangan = tarikh_raw
                    bulan_tahun_kod = "JUL2026"
                    if tarikh_raw and " " in tarikh_raw:
                        try:
                            tarikh_sahaja = tarikh_raw.split(" ")
                            dt_obj = datetime.strptime(tarikh_sahaja[0], "%Y-%m-%d")
                            tarikh_kewangan = dt_obj.strftime("%d/%m/%Y")
                            bulan_tahun_kod = dt_obj.strftime("%b%Y").upper()
                        except:
                            pass

                    baris_salinan_terus = [
                        no_turutan_terakhir,              # Lajur A (NO)
                        tarikh_kewangan,                  # Lajur B (TARIKH)
                        inv_no_payment.upper(),           # Lajur C (ID_INVOIS)
                        pelanggan,                        # Lajur D (PELANGGAN)
                        saluran,                          # Lajur E (SALURAN_MASUK)
                        "CUCI KARPET",                    # Lajur F (KATEGORI_SERVIS)
                        harga,                            # Lajur G (AMOUNT)
                        f"Auto-Streamlit: Invois {inv_no_payment.upper()}", # Lajur H (CATATAN)
                        f"{saluran}{bulan_tahun_kod}"     # Lajur I (GABUNGAN)
                    ]
                    baris_baru_akan_ditampal.append(baris_salinan_terus)

        # 5. HANTAR DATA PUKAL SEKALIGUS (1 REQUEST SAHAJA UNTUK TULIS)
        if baris_baru_akan_ditampal:
            ws_revenue.append_rows(baris_baru_akan_ditampal, value_input_option="USER_ENTERED")
            print(f"🎉 BERJAYA AUTOMATIK! Menambah {len(baris_baru_akan_ditampal)} data baharu ke Raw_Revenue.")
        else:
            print("✨ Terminal: Rekod sedia ada sudah selari.")

    except Exception as e:
        print(f"❌ Enjin Pandas gagal: {str(e)}")







import time
import pandas as pd
import subprocess
import config

# =========================================================================
# 📊 MODUL 1: RAW_REVENUE -> DASHBOARD (KOD ASAL + DINAMIK)
# =========================================================================
def jalankan_pengira_jualan_dashboard():
    print("\n==========================================================")
    print(" 📊 ENGIN JUALAN MULTI-TAHUN: RAW_REVENUE -> DASHBOARD")
    print("==========================================================")
    try:
        client = config.hubung_google_sheets()
        sheet_finance = client.open_by_url(config.URL_FINANCE_SHEET)
        ws_dashboard = sheet_finance.worksheet("DASHBOARD")
        ws_revenue = sheet_finance.worksheet("Raw_Revenue")
        time.sleep(1)
        
        tahun_master_raw = ws_dashboard.cell(2, 15).value # Sel O2 Dashboard
        if not tahun_master_raw:
            tahun_master_raw = "2026"
        tahun_pilihan = str(tahun_master_raw).strip()
        print(f"🎯 TAHUN SUIS INDUK DIKESAN LIVE: {tahun_pilihan}")
        
        time.sleep(1)
        data_revenue = ws_revenue.get_all_records()
        if not data_revenue:
            print("⚠️ Tab Raw_Revenue kosong!")
            return
            
        df_rev = pd.DataFrame(data_revenue)
        df_rev['AMOUNT_NUM'] = pd.to_numeric(df_rev['AMOUNT'].astype(str).str.replace('RM','', case=False).str.replace(',','').str.strip(), errors='coerce').fillna(0.0)
        df_rev['GABUNGAN_STR'] = df_rev['GABUNGAN'].astype(str).str.strip().str.upper()
        
        def ekstrak_bulan_jualan(row):
            gabung = row['GABUNGAN_STR']
            if tahun_pilihan in gabung:
                for bln in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]:
                    if bln in gabung:
                        return bln
            return ""
            
        df_rev['BULAN_EKSTRAK'] = df_rev.apply(ekstrak_bulan_jualan, axis=1)
        df_rev_filtered = df_rev[df_rev['BULAN_EKSTRAK'] != ""].copy()
        rumusan_jualan = df_rev_filtered.groupby('BULAN_EKSTRAK')['AMOUNT_NUM'].sum().to_dict()
        
        susunan_bulan_dashboard = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        blok_jualan_dashboard = []
        for bln_nama in susunan_bulan_dashboard:
            nilai_jualan = rumusan_jualan.get(bln_nama, 0.0)
            blok_jualan_dashboard.append([round(float(nilai_jualan), 2) if nilai_jualan > 0 else 0])
            
        print(f"🚀 Mengepam masuk data jualan tahun {tahun_pilihan} ke Sel D13:D24 Dashboard...")
        time.sleep(1)
        ws_dashboard.update(range_name="D13:D24", values=blok_jualan_dashboard)
        print("✅ Berjaya Memulihkan Struktur Jualan Dashboard!")
        
    except Exception as e:
        print(f"❌ Ralat sistem pemprosesan jualan: {str(e)}")






# =========================================================================
# 📈 MODUL 2: ANALISA JUALAN (2) & OPERASI KARPET
# =========================================================================



def bersihkan_harga_matriks(nilai_raw):
    # -------------------------------------------------------------------------
    # 🛠️ CERITA LANGKAH 1: PEMBERSIHAN FORMAT WANG RM
    # -------------------------------------------------------------------------
    # Tujuan: Menukarkan teks harga jualan atau kos seperti 'RM30.00' atau '6,74' 
    # kepada angka perpuluhan (float) bersih yang boleh dikira secara matematik.
    # -------------------------------------------------------------------------
    if not nilai_raw:
        return 0.0
    try:
        teks = str(nilai_raw).upper().replace('RM', '').strip()
        # Mengendali masalah tanda koma perpuluhan jika ada pada sistem Google Sheets
        if ',' in teks and '.' not in teks:
            teks = teks.replace(',', '.')
        elif ',' in teks and '.' in teks:
            teks = teks.replace(',', '')
        return float(teks)
    except (ValueError, TypeError):
        return 0.0

def normalisasi_kod_produk(kod_raw):
    # -------------------------------------------------------------------------
    # 🛠️ CERITA LANGKAH 2: PENSERAGAMAN KOD PRODUK (NORMALIZATION)
    # -------------------------------------------------------------------------
    # Tujuan: Menyelesaikan masalah amaran kuning terminal akibat tulisan manual 
    # yang tidak sekata antara tab Karpet dan tab Analisa.
    # Contoh: 'LP 4" X 6"', 'LP 4 X 6', dan 'Lp 5 X 7' semuanya akan dipaksa menjadi 
    # huruf besar, dibuang tanda inci ("), dan dibuang semua jarak kosong.
    # Hasil: 'LP 4" X 6"' dan 'LP 4 X 6' kedua-duanya akan bertukar menjadi 'LP4X6'.
    # -------------------------------------------------------------------------
    if not kod_raw:
        return ""
    teks = str(kod_raw).upper()          # Tukar semua kepada huruf besar sepenuhnya
    teks = teks.replace('"', '')         # Buang tanda simbol inci (")
    teks = teks.replace(" ", "")         # Buang semua ruang kosong (whitespace)
    return teks.strip()


def jalankan_automasi_analisis_jualan():
    print("\n==========================================================")
    print(" 📈 ENGIN ANALISIS JUALAN (2): KEMASKINI MATRIKS DINAMIK")
    print("==========================================================")
    try:
        klien = config.hubung_google_sheets()
        sheet_kewangan = klien.open_by_url(config.URL_FINANCE_SHEET)
        sheet_operasi = klien.open_by_url(config.URL_OPERASI_SHEET)
        
        sheet_analisa = sheet_kewangan.worksheet("ANALISA JUALAN (2)")
        sheet_karpet = sheet_operasi.worksheet("Karpet")
        sheet_kos_servis = sheet_kewangan.worksheet("KOS SERVIS")
        
        # Ambil data secara live dari Google Sheets
        data_analisa = sheet_analisa.get_all_values()
        matriks_karpet = sheet_karpet.get_all_values()
        data_kos_servis = sheet_kos_servis.get_all_values()
        
        # === 🛠️ DIBAIKI: KUNCI TAHUN KEPADA MASTER O2 DASHBOARD UTAMA ===
        sheet_dash_central = sheet_kewangan.worksheet("DASHBOARD")
        tahun_master_raw = sheet_dash_central.cell(2, 15).value # Membaca Sel O2 Master
        if tahun_master_raw:
            try:
                tahun_penfull = str(int(float(tahun_master_raw))).strip()
            except:
                tahun_penfull = str(tahun_master_raw).strip()
        else:
            tahun_penfull = "2026"
        teks_tahun_aktif = tahun_penfull[-2:]
        # =======================================================================
        print(f"🎯 ANALISIS JUALAN AKTIF UNTUK TAHUN: 20{teks_tahun_aktif}")
        print("🚀 Memproses matriks jualan karpet...")

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 3: KEMASKINI TAJUK LAJUR BULAN DINAMIK (BARIS 7)
        # -------------------------------------------------------------------------
        # Tujuan: Menjana secara automatik tajuk bulan (Jan-26, Feb-26 dll) mengikut
        # tahun aktif Dashboard dan menembaknya ke baris 7 bagi ketiga-tiga jalur.
        # 🛡️ DIBAIKI: Jalur Untung Kasar ditukar dari AM7:AZ7 ke AO7:AZ7 untuk elak overwrite.
        # -------------------------------------------------------------------------
        senarai_12_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        senarai_tajuk_baru = [f"{m}-{teks_tahun_aktif}" for m in senarai_12_bulan]
        
        print("🔄 Mengemas kini tajuk lajur mengikut tahun aktif...")
        sheet_analisa.update(range_name="F7:Q7", values=[senarai_tajuk_baru], value_input_option="USER_ENTERED")    # Kuantiti
        sheet_analisa.update(range_name="X7:AI7", values=[senarai_tajuk_baru], value_input_option="USER_ENTERED")   # Nilai RM
        sheet_analisa.update(range_name="AO7:AZ7", values=[senarai_tajuk_baru], value_input_option="USER_ENTERED")  # Untung Kasar

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 4: PEMETAAN BARIS DINAMIK VIA KOLUM D (BLOK KUANTITI)
        # -------------------------------------------------------------------------
        # 🔄 DIBAIKI DINAMIK: Kunci had baris 42 dibuang. Python mengira jumlah baris secara
        # automatik menggunakan `len(data_analisa)`. Jika ada produk karpet baru dimasukkan
        # di baris bawah-bawah (Contoh: baris 43, 44, 50, dll), ia akan auto-diambil masuk!
        # Ambil kod rujukan dari Kolum D (Index 3 dalam list Python).
        # -------------------------------------------------------------------------
        peta_baris_produk = {}          # Menyimpan format bersih (Contoh: 'CK4X6': 8)
        peta_kod_asli_analisa = {}      # Menyimpan nama asal untuk rujukan paparan amaran
        jumlah_maksimum_baris = len(data_analisa)
        
        for idx, baris in enumerate(data_analisa):
            if idx >= 7:                # Membaca bermula dari Baris 8 di Google Sheets sehingga ke bawah tanpa had
                if len(baris) > 3:      # Pastikan baris mempunyai data sehingga Kolum D
                    # Saringan keselamatan: Elakkan membaca baris jumlah besar / ringkasan di bawah jadual
                    if str(baris[0]).strip().upper() == "TOTAL" or "TOTAL" in str(baris[1]).strip().upper():
                        continue
                        
                    kod_asli = str(baris[3]).strip()  # 🛠️ Kolum D (Index 3 dalam list Python)
                    if kod_asli:
                        kod_bersih = normalisasi_kod_produk(kod_asli)
                        peta_baris_produk[kod_bersih] = idx + 1
                        peta_kod_asli_analisa[kod_bersih] = kod_asli

        # Mengira berapa baris sasaran yang berjaya dikesan secara dinamik
        total_baris_dikesan = len(peta_baris_produk)
        baris_akhir_dinamik = max(peta_baris_produk.values()) if peta_baris_produk else 42
        print(f"📊 [INFO DINAMIK]: Menemui {total_baris_dikesan} jenis produk karpet. Julat operasi: Baris 8 hingga {baris_akhir_dinamik}.")

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 5: PEMETAAN DATA KOS SERVIS DARI KOLUM K
        # -------------------------------------------------------------------------
        # Tujuan: Mengumpul data Jumlah Kos Kasar per unit dari tab KOS SERVIS 
        # Kolum K (Indeks ke-10). Kod produk di Kolum B juga dibersihkan dengan ketat.
        # -------------------------------------------------------------------------
        peta_kos_servis = {} 
        for idx, baris in enumerate(data_kos_servis):
            if idx >= 4:                # Membaca data bermula dari baris ke-5
                if len(baris) > 10:     # Pastikan baris cukup panjang sehingga Kolum K
                    kod_kos_raw = str(baris[1]).strip()  # Kolum B (Index 1)
                    if kod_kos_raw:
                        kod_kos_bersih = normalisasi_kod_produk(kod_kos_raw)
                        peta_kos_servis[kod_kos_bersih] = bersihkan_harga_matriks(baris[10]) # Kolum K (Index 10)

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 6: EKSTRAK KEPALA JALUR TAB KARPET (SUMBER)
        # -------------------------------------------------------------------------
        # Tujuan: Mencari kedudukan Kolum KOD, HARGA, dan TARIKH di tab Karpet 
        # secara dinamik untuk mengelakkan ralat jika susunan kolum berubah.
        # -------------------------------------------------------------------------
        header_karpet = [str(h).strip().upper() for h in matriks_karpet[0]]
        idx_kod = header_karpet.index("KOD")
        idx_harga = header_karpet.index("HARGA")
        idx_tarikh = header_karpet.index("TARIKH")

        # Membina tempat pengiraan kosong di memori Python bagi setiap bulan (1 hingga 12)
        struktur_kiraan = {kod: {m: {'qty': 0, 'nilai': 0.0} for m in range(1, 13)} for kod in peta_baris_produk.keys()}

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 7: PROSES IMBAKAN, PENAPISAN & SIASATAN DATA RAW
        # -------------------------------------------------------------------------
        # Tujuan: Mengimbas setiap baris data di tab Karpet, melakukan saringan Tahun 
        # Master, dan memadankan kod menggunakan kaedah normalisasi huruf besar & simbol.
        # -------------------------------------------------------------------------
        total_data_dijumpai = 0
        total_data_diabaikan_tahun = 0
        
        print("\n🔎 [FASA SIASATAN]: Meneliti rekod jualan tab Karpet...")
        for idx, baris in enumerate(matriks_karpet[1:]):
            no_baris_sheet = idx + 2
            
            if len(baris) <= max(idx_kod, idx_harga, idx_tarikh):
                continue
                
            kod_karpet_raw = str(baris[idx_kod]).strip()
            harga_raw = baris[idx_harga]
            tarikh_raw = str(baris[idx_tarikh]).strip().replace(" ", "")
            
            if not kod_karpet_raw:
                continue
                
            kod_karpet_bersih = normalisasi_kod_produk(kod_karpet_raw)
            
            # Tukar format teks tarikh kepada objek datetime
            try:
                if '/' in tarikh_raw:
                    obj_tarikh = datetime.strptime(tarikh_raw, "%d/%m/%Y")
                elif '-' in tarikh_raw:
                    obj_tarikh = datetime.strptime(tarikh_raw, "%Y-%m-%d")
                else:
                    continue
            except ValueError:
                continue  # Skip jika tarikh manual tidak sah atau rosak
                
            # Saringan Tahun Master (Hanya ambil tahun pilihan di Dashboard)
            if str(obj_tarikh.year) != tahun_penfull:
                total_data_diabaikan_tahun += 1
                continue
                
            # Siasatan Padanan: Jika kod tiada dalam senarai rujukan Kolum D Analisa
            if kod_karpet_bersih not in struktur_kiraan:
                print(f"⚠️ Amaran Rujukan: Kod '{kod_karpet_raw}' di Baris {no_baris_sheet} tahun {tahun_penfull} ada, tetapi tiada dalam Kolum D Tab Analisa.")
                continue
                
            # Simpan hasil pengiraan ke dalam memori komputer
            harga_bersih = bersihkan_harga_matriks(harga_raw)
            struktur_kiraan[kod_karpet_bersih][obj_tarikh.month]['qty'] += 1
            struktur_kiraan[kod_karpet_bersih][obj_tarikh.month]['nilai'] += harga_bersih
            total_data_dijumpai += 1

        print(f"📊 [LAPORAN IMBASAN]: Berjaya mengekstrak {total_data_dijumpai} rekod bagi tahun {tahun_penfull}.")
        print(f"⏩ [LAPORAN IMBASAN]: Melompati {total_data_diabaikan_tahun} data lama (bukan tahun {tahun_penfull}).")

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 8: STRUKTURKAN BLOK GRID JADUAL MATRIKS JALUR BAHARU
  # Tujuan: Menyusun hasil pengiraan memori menjadi grid mengikut urutan 
        # baris asal produk yang dinamik dari Baris 8 hingga ke bawah-bawah.
        # -------------------------------------------------------------------------
        blok_kuantiti = []
        blok_nilai_rm = []
        blok_untung_kasar = []

        # Atur susunan mengikut nombor baris asal Google Sheets bagi memastikan data tidak bertukar tempat
        for kod_bersih, no_baris in sorted(peta_baris_produk.items(), key=lambda x: x[1]):
            baris_qty = []
            baris_val = []
            baris_utg = []
            
            for m in range(1, 13):
                qty = struktur_kiraan[kod_bersih][m]['qty']
                nilai = struktur_kiraan[kod_bersih][m]['nilai']
                
                # Mengira untung kasar menggunakan rujukan kos Kolum K
                kos_seunit = peta_kos_servis.get(kod_bersih, 0.0)
                kos_kasar_total = qty * kos_seunit
                untung_kasar = nilai - kos_kasar_total
                
                baris_qty.append(qty if qty > 0 else 0)
                baris_val.append(nilai if nilai > 0 else 0.0)
                baris_utg.append(untung_kasar)
                
            blok_kuantiti.append(baris_qty)
            blok_nilai_rm.append(baris_val)
            blok_untung_kasar.append(baris_utg)

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 9: TEMBAKAN DATA STATIK PUKAL (BULK UPDATE)
        # -------------------------------------------------------------------------
        # 🛡️ DIBAIKI: Koordinat Untung Kasar ditukar dari AM8 ke AO8 untuk elak overwrite 
        # Kolum AM (Kod) & Kolum AN (Jenis). Had baris hujung diset secara dinamik.
        # -------------------------------------------------------------------------
        julat_qty = f"F8:Q{baris_akhir_dinamik}"
        julat_val = f"X8:AI{baris_akhir_dinamik}"
        julat_utg = f"AO8:AZ{baris_akhir_dinamik}"  # 🛠️ Bermula di AO8 (Kotak Januari)
        
        print(f"🚀 Menembak data Kuantiti bersih ke jalur {julat_qty}...")
        sheet_analisa.update(range_name=julat_qty, values=blok_kuantiti, value_input_option="USER_ENTERED")
        
        print(f"🚀 Menembak data Nilai Jualan bersih ke jalur {julat_val}...")
        sheet_analisa.update(range_name=julat_val, values=blok_nilai_rm, value_input_option="USER_ENTERED")
        
        print(f"🚀 Menembak data Untung Kasar bersih ke jalur {julat_utg}...")
        sheet_analisa.update(range_name=julat_utg, values=blok_untung_kasar, value_input_option="USER_ENTERED")

        print(f"✨ [KAUNTER MATRIKS]: Sukses mengeset {total_data_dijumpai} jualan karpet secara dinamik!")
        print("✅ Berjaya Memproses Analisis Jualan (2)!")
        
    except Exception as e:
        print(f"❌ Ralat sistem analisis jualan: {str(e)}")



# =========================================================================
# 🧮 MODUL 3: MATRIKS PERBELANJAAN BULANAN (YANG KITA URUSKAN TADI)
# =========================================================================
def jalankan_automasi_matriks_belanja():
    # Fungsi ini adalah kod perbelanjaan yang telah kita baiki sebelum ini.
    # Dipanggil automatik sekiranya isyarat 'REFRESH_EXPENSES_' dikesan.
    pass 



# =========================================================================
# ENJIN 3: MATRIKS BULANAN PERBELANJAAN (KOD ASAL 100%)
# =========================================================================
def jalankan_automasi_matriks_belanja():
    print("\n==========================================================")
    print(" 🧮 AUTOMASI MULTI-TAHUN: MATRIKS BULANAN (PERBELANJAAN)")
    print("==========================================================")
    try:
        print("\n⏳ Memanggil fungsi sambungan API...")
        client = config.hubung_google_sheets()
        print("📥 Membuka Sheet Kewangan (DB_MYCARPET-FINANCE)...")
        sheet_finance = client.open_by_url(config.URL_FINANCE_SHEET)
        
        ws_perbelanjaan = sheet_finance.worksheet("PERBELANJAAN")
        time.sleep(1)
        
                # === DIBAIKI: MEMBACA TAHUN DARI PUSAT INPUT MASTER (SEL O2 DASHBOARD) ===
        ws_dash_central = sheet_finance.worksheet("DASHBOARD")
        tahun_master_raw = ws_dash_central.cell(2, 15).value  # Membaca Sel O2 Master
        
        if tahun_master_raw:
            try:
                # Mengamankan ralat nombor float perpuluhan (2024.0 -> "2024")
                tahun_pilihan = str(int(float(tahun_master_raw))).strip()
            except:
                tahun_pilihan = str(tahun_master_raw).strip()
        else:
            tahun_pilihan = "2026"  # Backup tahun standard
            
        teks_tahun_aktif = tahun_pilihan[-2:]
        # =======================================================================

        if not tahun_master_raw:
            tahun_master_raw = "2026"
        tahun_pilihan = str(tahun_master_raw).strip()
        teks_tahun_aktif = tahun_pilihan[-2:]
        
        print(f"🎯 TAHUN AKTIF DIKESAN LIVE DARI H2: {tahun_pilihan}")
        
        senarai_12_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        senarai_tajuk_baru = [f"{m}-{teks_tahun_aktif}" for m in senarai_12_bulan]
        
        time.sleep(1)
        ws_perbelanjaan.update(range_name="R4:AC4", values=[senarai_tajuk_baru])
        
        print("📥 Membaca rekod induk dari tab 'Raw_Expenses'...")
        ws_exp = sheet_finance.worksheet("Raw_Expenses")
        time.sleep(1)
        
        data_raw_exp = ws_exp.get_all_values()
        if len(data_raw_exp) <= 1:
            print("⚠️ Tab Raw_Expenses kosong!")
            return
            
        # Tukar ke Dataframe menggunakan baris pertama sebagai Header
        header = data_raw_exp[0]
        rows = data_raw_exp[1:]
        df_exp = pd.DataFrame(rows, columns=header)
        
        # Bersihkan ruang kosong pada nama column
        df_exp.columns = df_exp.columns.str.strip()
        
        # Tukar AMOUNT ke Nombor secara selamat (Kalis Sel Kosong)
        df_exp['AMOUNT_NUM'] = df_exp['AMOUNT'].astype(str).str.replace('RM','', case=False).str.replace(',','').str.strip()
        df_exp['AMOUNT_NUM'] = pd.to_numeric(df_exp['AMOUNT_NUM'], errors='coerce').fillna(0.0)
        
        df_exp['TARIKH_STR'] = df_exp['TARIKH'].astype(str).str.strip()
        
        def ekstrak_tahun_string(teks):
            bahagian = teks.split('/')
            if len(bahagian) == 3:
                return bahagian[2].strip()
            return ""
            
        def ekstrak_bulan_nama_string(teks):
            bahagian = teks.split('/')
            if len(bahagian) == 3:
                try:
                    num_bulan = int(bahagian[1])
                    kamus_bulan = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 
                                   7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
                    return kamus_bulan.get(num_bulan, "")
                except:
                    return ""
            return ""
            
        df_exp['TAHUN_EKSTRAK'] = df_exp['TARIKH_STR'].apply(ekstrak_tahun_string)
        df_exp['BULAN_STR'] = df_exp['TARIKH_STR'].apply(ekstrak_bulan_nama_string)
        
        # Standardkan kod perbelanjaan (buang space berlebihan)
        df_exp['KOD_PERBELANJAAN'] = df_exp['KOD_PERBELANJAAN'].astype(str).str.strip()
        
        print(f"🔄 Memadam paparan lama & mengepam transaksi tahun {tahun_pilihan} ke Jalur A-M...")
               # Standardkan kod perbelanjaan (buang space berlebihan)
        df_exp['KOD_PERBELANJAAN'] = df_exp['KOD_PERBELANJAAN'].astype(str).str.strip()
        
        # 🌟 KOD BARU: Buka/Padam sebarang filter Google Sheets yang tersangkut di tab PERBELANJAAN 
        # Ini untuk mengelakkan baris lama tersembunyi (warna biru)
        try:
            ws_perbelanjaan.clear_basic_filter()
        except:
            pass # Langkau jika tiada filter yang aktif

        print(f"🔄 Memadam paparan lama & mengepam transaksi tahun {tahun_pilihan} ke Jalur A-M...")
        ws_perbelanjaan.batch_clear(["A5:M1000"])
        
        # Tapis data dari Raw_Expenses mengikut tahun pilihan pengguna
        df_exp_filtered = df_exp[df_exp['TAHUN_EKSTRAK'] == tahun_pilihan].copy()
        
        if not df_exp_filtered.empty:
            lajur_turutan = ['NO', 'TARIKH', 'BAYAR_MELALUI', 'JENIS BARANG', 'KUANTITI', 'HARGA_SEUNIT', 'BUTIRAN', 'KOD_PERBELANJAAN', 'AMOUNT', 'PEMBEKAL', 'CATATAN', 'COGS_ESTIMATE', 'GABUNGAN']
            
            # Guna fillna untuk elakkan data hilang jika ada lajur kosong
            for col in lajur_turutan:
                if col not in df_exp_filtered.columns:
                    df_exp_filtered[col] = ""
                    
            senarai_data_viewer = df_exp_filtered[lajur_turutan].astype(str).values.tolist()
            time.sleep(1)
            
            # Pam data tahun pilihan ke dalam baris 5 ke bawah
            ws_perbelanjaan.update(range_name=f"A5:M{4 + len(senarai_data_viewer)}", values=senarai_data_viewer)
            print(f"✅ Berjaya memaparkan {len(senarai_data_viewer)} baris data transaksi di Jalur A-M bagi tahun {tahun_pilihan}.")
        else:
            print(f"⚠️ Tiada rekod transaksi dijumpai untuk tahun {tahun_pilihan} di tab Raw_Expenses.")

        # ====================================================================
        # KIRA MATRIKS KANAN R:AC (Dinamik)
        # ====================================================================
        rumusan_kategori = df_exp_filtered.groupby(['KOD_PERBELANJAAN', 'BULAN_STR'])['AMOUNT_NUM'].sum().to_dict()
        time.sleep(1)
        
        data_semasa_belanja = ws_perbelanjaan.get_all_values()
        peta_kolum_bulan = {"JAN": 0, "FEB": 1, "MAR": 2, "APR": 3, "MAY": 4, "JUN": 5, "JUL": 6, "AUG": 7, "SEP": 8, "OCT": 9, "NOV": 10, "DEC": 11}
        grid_matriks_kanan = []
        total_rows = len(data_semasa_belanja)
        
        # Jalankan gelung menegak mengikut senarai COA (KOD PERBELANJAAN) di sebelah kanan
        for idx_row in range(4, total_rows):
            baris_sheet = data_semasa_belanja[idx_row]
            baris_bulan_vals = [0] * 12
            
            # Membaca Lajur Q (Indeks 16) - Mengunci Kod Perbelanjaan Menegak
            if len(baris_sheet) > 16:
                kod_coa_menegak = str(baris_sheet[16]).strip()
                if kod_coa_menegak and not any(h in kod_coa_menegak.lower() for h in ["kod_belanja", "kod belanja"]):
                    for bln_nama, idx_array in peta_kolum_bulan.items():
                        val_rm = rumusan_kategori.get((kod_coa_menegak, bln_nama), 0.0)
                        baris_bulan_vals[idx_array] = float(val_rm.item() if hasattr(val_rm, 'item') else val_rm)
                    grid_matriks_kanan.append(baris_bulan_vals)
        
        if grid_matriks_kanan:
            print(f"🚀 Mengepam masuk ringkasan nilai kos ke kotak matriks R5:AC{4 + len(grid_matriks_kanan)}...")
            time.sleep(1.5)
            ws_perbelanjaan.update(range_name=f"R5:AC{4 + len(grid_matriks_kanan)}", values=grid_matriks_kanan)
            
        print("\n==========================================================")
        print("🎉 BERJAYA PENUH! Jajaran kiri & kanan kini selari dan dikemas kini.")
        print("==========================================================")
        
    except Exception as e:
        print(f"❌ Ralat sistem pemprosesan: {str(e)}")














# =========================================================================
# # ENJIN 4: PENYATA UNTUNG RUGI (P&L) - VERSI DIKEMASKINI & KALIS KOSONG
# =========================================================================

def normalisasi_nama_perkara(teks_raw):
    # -------------------------------------------------------------------------
    # 🛠️ CERITA LANGKAH 1: PENSERAGAMAN NAMA PERKARA/KOD BELANJA
    # -------------------------------------------------------------------------
    # Tujuan: Menghapuskan isu ketidakpadanan baris akibat teks bercampur atau 
    # tersilap jarak kosong antara tab PERBELANJAAN dan tab P&L.
    # Contoh: "5-1000  SABUN DAN PEWANGI" dan "5-1000 SABUN DAN PEWANGI" akan
    # diseragamkan menjadi "51000SABUNDANPEWANGI" supaya padanan 100% tepat.
    # -------------------------------------------------------------------------
    if not teks_raw:
        return ""
    teks = str(teks_raw).upper()
    teks = teks.replace("-", "").replace(" ", "").replace("/", "").replace("&", "")
    return teks.strip()

#================================================
###### ALIRAN TUNAI##########

def normalisasi_saluran_bank(nama_raw):
    # -------------------------------------------------------------------------
    # 🛠️ CERITA LANGKAH 1: PENSERAGAMAN NAMA BANK / SALURAN MASUK
    # -------------------------------------------------------------------------
    # Tujuan: Menghapuskan isu ralat perbezaan tipografi teks manual.
    # Memaksa teks bertukar ke huruf besar dan membuang semua jarak kosong.
    # Contoh: "Hong Leong", "hong leong", "HONG LEONG " semuanya bertukar 
    # menjadi "HONGLEONG" supaya padanan 100% tepat tanpa gagal.
    # -------------------------------------------------------------------------
    if not nama_raw:
        return ""
    return str(nama_raw).upper().replace(" ", "").strip()


def jalankan_automasi_aliran_tunai():
    print("\n==========================================================")
    print(" 🌊 ENGIN ALIRAN TUNAI: SINKRONISASI WANG MASUK & KELUAR")
    print("==========================================================")
    try:
        klien = config.hubung_google_sheets()
        sheet_kewangan = klien.open_by_url(config.URL_FINANCE_SHEET)
        
        sheet_aliran = sheet_kewangan.worksheet("ALIRAN TUNAI")
        sheet_raw_rev = sheet_kewangan.worksheet("Raw_Revenue")
        sheet_raw_exp = sheet_kewangan.worksheet("Raw_Expenses")
        sheet_dashboard = sheet_kewangan.worksheet("DASHBOARD")
        
        # Ambil seluruh data raw secara live
        matriks_revenue = sheet_raw_rev.get_all_values()
        matriks_expenses = sheet_raw_exp.get_all_values()
        
        # === 🛠️ KUNCI TAHUN KEPADA MASTER O2 DASHBOARD UTAMA ===
        tahun_master_raw = sheet_dashboard.cell(2, 15).value
        if tahun_master_raw:
            try:
                tahun_penfull = str(int(float(tahun_master_raw))).strip()
            except:
                tahun_penfull = str(tahun_master_raw).strip()
        else:
            tahun_penfull = "2026"
        print(f"🎯 Aliran Tunai Latar Belakang Aktif Untuk Tahun: {tahun_penfull}")

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 2 & 3: EKSTRAK KEPALA JALUR SECARA GEBAL (SAFE INDEXING)
        # -------------------------------------------------------------------------
        # DIBAIKI MUTLAK: Menggunakan gelung untuk mencari perkataan kunci separa. 
        # Ini menghalang ralat 'x not in list' jika ada ruang kosong tersembunyi pada header.
        # -------------------------------------------------------------------------
        header_rev = [str(h).strip().upper() for h in matriks_revenue[0]]
        idx_tgl_rev = next((i for i, h in enumerate(header_rev) if "TARIKH" in h), 1)
        idx_ch_rev = next((i for i, h in enumerate(header_rev) if "SALURAN" in h or "MASUK" in h), 4)
        idx_amt_rev = next((i for i, h in enumerate(header_rev) if "AMOUNT" in h or "JUMLAH" in h), 7)

        header_exp = [str(h).strip().upper() for h in matriks_expenses[0]]
        idx_tgl_exp = next((i for i, h in enumerate(header_exp) if "TARIKH" in h), 1)
        idx_ch_exp = next((i for i, h in enumerate(header_exp) if "BAYAR" in h or "MELALUI" in h), 2)
        idx_amt_exp = next((i for i, h in enumerate(header_exp) if "AMOUNT" in h or "JUMLAH" in h), 8)

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 4: STRUKTURKAN JALUR MATRIKS DI MEMORI PYTHON
        # -------------------------------------------------------------------------
        # Tujuan: Membina kotak ingatan kosong untuk 12 Bulan (Baris 1 hingga 12).
        # Setiap bulan memegang data simpanan bank bagi Wang Masuk dan Wang Keluar.
        # -------------------------------------------------------------------------
        peta_bank_index = {"MAYBANK": 0, "CIMB": 1, "HONGLEONG": 2, "TUNAI": 3}
        
        # Struktur: { BULAN_NUM: { 'masuk': [Mbb, Cimb, Hl, Tni], 'keluar': [Mbb, Cimb, Hl, Tni] } }
        ingatan_aliran = {m: {'masuk': [0.0]*4, 'keluar': [0.0]*4} for m in range(1, 13)}

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 5: AGREGASI DATA WANG MASUK (RAW REVENUE)
        # -------------------------------------------------------------------------
        total_rev_diproses = 0
        for baris in matriks_revenue[1:]:
            if len(baris) <= max(idx_tgl_rev, idx_ch_rev, idx_amt_rev):
                continue
            tarikh_raw = str(baris[idx_tgl_rev]).strip().replace(" ", "")
            saluran_raw = str(baris[idx_ch_rev]).strip()
            amount_raw = baris[idx_amt_rev]
            
            try:
                obj_tgl = datetime.strptime(tarikh_raw, "%d/%m/%Y") if '/' in tarikh_raw else datetime.strptime(tarikh_raw, "%Y-%m-%d")
                if str(obj_tgl.year) == tahun_penfull:
                    saluran_clean = normalisasi_saluran_bank(saluran_raw)
                    if saluran_clean in peta_bank_index:
                        b_idx = peta_bank_index[saluran_clean]
                        nilai_bersih = bersihkan_harga_matriks(amount_raw)
                        ingatan_aliran[obj_tgl.month]['masuk'][b_idx] += nilai_bersih
                        total_rev_diproses += 1
            except ValueError:
                continue

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 6: AGREGASI DATA WANG KELUAR (RAW EXPENSES)
        # -------------------------------------------------------------------------
        total_exp_diproses = 0
        for baris in matriks_expenses[1:]:
            if len(baris) <= max(idx_tgl_exp, idx_ch_exp, idx_amt_exp):
                continue
            tarikh_raw = str(baris[idx_tgl_exp]).strip().replace(" ", "")
            saluran_raw = str(baris[idx_ch_exp]).strip()
            amount_raw = baris[idx_amt_exp]
            
            try:
                obj_tgl = datetime.strptime(tarikh_raw, "%d/%m/%Y") if '/' in tarikh_raw else datetime.strptime(tarikh_raw, "%Y-%m-%d")
                if str(obj_tgl.year) == tahun_penfull:
                    saluran_clean = normalisasi_saluran_bank(saluran_raw)
                    if saluran_clean in peta_bank_index:
                        b_idx = peta_bank_index[saluran_clean]
                        nilai_bersih = bersihkan_harga_matriks(amount_raw)
                        ingatan_aliran[obj_tgl.month]['keluar'][b_idx] += nilai_bersih
                        total_exp_diproses += 1
            except ValueError:
                continue

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 7: STRUKTURKAN GRID PENUH UNTUK DISUNTIK KE GOOGLE SHEETS
        # -------------------------------------------------------------------------
        # Tujuan: Menyusun data memori menjadi grid menegak saiz 12 Baris x 8 Kolum.
        # Menukarkan angka 0 menjadi string kosong "" untuk memastikan hasil ultra-bersih.
        # -------------------------------------------------------------------------
        grid_aliran_output = []
        for m in range(1, 13):
            data_m_masuk = ingatan_aliran[m]['masuk']
            data_m_keluar = ingatan_aliran[m]['keluar']
            
            # Tukar format kepada angka bulat (Integer). Jika 0, kekalkan kosong ""
            baris_clean_masuk = [int(x) if x > 0 else "" for x in data_m_masuk]
            baris_clean_keluar = [int(x) if x > 0 else "" for x in data_m_keluar]
            
            # Gabungkan menjadi 8 kolum: [Mbb, Cimb, Hl, Tni, Mbb, Cimb, Hl, Tni]
            grid_aliran_output.append(baris_clean_masuk + baris_clean_keluar)

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 8: TEMBAKAN MATRIKS PUKAL STATIK KE TAB ALIRAN TUNAI
        # -------------------------------------------------------------------------
        # Tujuan: Menembak sekaligus dari D6 hingga K17. Langkah ini sangat pantas, 
        # selamat, dan 100% memelihara kolum formula J, L, M, N di sebelah kanan.
        # -------------------------------------------------------------------------
        julat_aliran_target = "D6:K17"
        print(f"🚀 Menembak grid data aliran tunai ke jalur {julat_aliran_target}...")
        sheet_aliran.update(range_name=julat_aliran_target, values=grid_aliran_output, value_input_option="USER_ENTERED")
        
        print(f"✨ [SUKSES ALIRAN TUNAI]: Berjaya menyinkronkan {total_rev_diproses} penerimaan dan {total_exp_diproses} kos keluar tahun {tahun_penfull} secara masa-nyata!")
        
    except Exception as e:
        print(f"❌ Ralat enjin aliran tunai: {str(e)}")


    # =========================================================================
    # OPERASI UTAMA MASTER ENGINE RUNNER
    # =========================================================================
# Rapatkan ke dinding kiri sekali (Tiada spasi langsung di permulaan baris)
if __name__ == "__main__":
    start_time = time.time()
    print("\n=====================================================")
    print("🤖 AUTOMATION ENG: 4-IN-1 MASTER FINANCIAL SYNC")
    print("=====================================================\n")

    # Jalankan 4 enjin secara berturutan dengan selamat
    jalankan_automasi_analisis_jualan()
    time.sleep(3)
    jalankan_automasi_matriks_belanja()
    time.sleep(3)
    jalankan_automasi_aliran_tunai()

    print(f"\n✨ [SUKSES] Semua selesai diselaraskan dalam {round(time.time() - start_time, 2)} saat!")




