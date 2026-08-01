import time
import subprocess
import config

print("=====================================================")
print("🤖 AUTOMATION DAEMON: MYCARPET FINANCIAL MONITOR v2")
print("⚠️ ANTI-SEKATAN GOOGLE API (SUPER-SAFE): AKTIF")
print("=====================================================\n")

# -------------------------------------------------------------------------
# ⚙️ PEMBOLEHUBAH INGATAN DAEMON (MEMORI JANGA PENDEK PYTHON)
# -------------------------------------------------------------------------
nilai_trigger_lama = ""
baris_revenue_lama = 0
baris_expenses_lama = 0
fasa_mula_sedut = True

while True:
    try:
        # Buka hubungan baharu setiap kitaran untuk mengelakkan token tamat tempoh
        klien = config.hubung_google_sheets()
        sheet_kewangan = klien.open_by_url(config.URL_FINANCE_SHEET)
        
        sheet_dashboard = sheet_kewangan.worksheet("DASHBOARD")
        sheet_raw_rev = sheet_kewangan.worksheet("Raw_Revenue")
        sheet_raw_exp = sheet_kewangan.worksheet("Raw_Expenses")
        
        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 1: LOCK SAIZ ASAL JADUAL (WARM-UP FASA)
        # -------------------------------------------------------------------------
        # Menggunakan get_all_values() untuk memintas masalah cache Google API. 
        # Membaca jumlah baris semasa sewaktu skrip mula dihidupkan.
        # -------------------------------------------------------------------------
        if fasa_mula_sedut:
            baris_revenue_lama = len(sheet_raw_rev.get_all_values())
            baris_expenses_lama = len(sheet_raw_exp.get_all_values())
            fasa_mula_sedut = False
            print(f"📦 [DAEMON LIVE]: Memulakan kawalan latar belakang.")
            print(f"   ├─ Saiz Semasa Raw_Revenue  : {baris_revenue_lama} baris.")
            print(f"   └─ Saiz Semasa Raw_Expenses : {baris_expenses_lama} baris.\n")

        # 1. Baca nilai live pilihan tahun dari Sel O2 Master Dashboard
        nilai_trigger_semasa = sheet_dashboard.cell(2, 15).value
        
        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 2: PENCETUS A (Dropdown Tahun Master O2 Berubah)
        # -------------------------------------------------------------------------
        if nilai_trigger_semasa:
            nilai_str = str(nilai_trigger_semasa).strip()
            if nilai_str != str(nilai_trigger_lama).strip():
                print(f"⚡ [ALERT O2]: Perubahan Master Tahun Dikesan -> {nilai_str}")
                print("🚀 Memicu Fail Utama Pakar Kewangan...")
                
                # Menjalankan fail utama anda untuk merefresh semua data mengikut tahun baru
                subprocess.run(["python", "pakar_kewangan.py"], check=True)
                
                nilai_trigger_lama = nilai_str
                # Reset tanda baris lama mengikut tahun baharu untuk keselamatan
                baris_revenue_lama = len(sheet_raw_rev.get_all_values())
                baris_expenses_lama = len(sheet_raw_exp.get_all_values())
                print("✨ Semua Penyata Kewangan Berjaya Disinkronasikan!\n")

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 3: PENCETUS B (Kemasukan Duit Masuk di Raw_Revenue)
        # -------------------------------------------------------------------------
        baris_revenue_semasa = len(sheet_raw_rev.get_all_values())
        if baris_revenue_semasa > baris_revenue_lama:
            baris_baru_rev = baris_revenue_semasa - baris_revenue_lama
            print(f"🔔 [ALERT REVENUE]: Mengecan {baris_baru_rev} data jualan baharu masuk di Raw_Revenue!")
            print("🚀 Menyinkronkan Penyata Aliran Tunai...")
            
            subprocess.run(["python", "pakar_kewangan.py"], check=True)
            
            baris_revenue_lama = baris_revenue_semasa
            print("✨ Selesai dikemas kini secara otomatis!\n")
            
        elif baris_revenue_semasa < baris_revenue_lama:
            baris_revenue_lama = baris_revenue_semasa # Logik jika anda delete baris secara manual

        # -------------------------------------------------------------------------
        # 📄 CERITA LANGKAH 4: PENCETUS C (Kemasukan Kos Keluar di Raw_Expenses)
        # -------------------------------------------------------------------------
        baris_expenses_semasa = len(sheet_raw_exp.get_all_values())
        if baris_expenses_semasa > baris_expenses_lama:
            baris_baru_exp = baris_expenses_semasa - baris_expenses_lama
            print(f"🔔 [ALERT EXPENSES]: Mengesan {baris_baru_exp} data perbelanjaan baharu masuk di Raw_Expenses!")
            print("🚀 Menyinkronkan Penyata Aliran Tunai...")
            
            subprocess.run(["python", "pakar_kewangan.py"], check=True)
            
            baris_expenses_lama = baris_expenses_semasa
            print("✨ Selesai dikemas kini secara otomatis!\n")
            
        elif baris_expenses_semasa < baris_expenses_lama:
            baris_expenses_lama = baris_expenses_semasa

        # 🌟 JEDA KESELAMATAN TINGGI: Menyemak setiap 15 saat bagi menjaga kuota Google API
        time.sleep(15)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistem master latar belakang ditutup secara manual.")
        break
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("\n🚨 [REST]: Had kuota Google API dicapai. Daemon berehat 60 saat...")
            time.sleep(60)
        else:
            print(f"⚠️ Amaran daemon: {e}. Mencuba semula dalam 10 saat...")
            time.sleep(10)
