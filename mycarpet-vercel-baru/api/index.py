from http.server import BaseHTTPRequestHandler
import os
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Hantar isyarat kepada pelayan bahawa kod kita sedia berjalan
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        
        try:
            # 🔍 [BAHAGIAN SEMAKAN KUNCI]
            # Tukar 'KUNCI_SAYA' kepada nama kunci rahsia (Environment Variable) yang kamu guna di Vercel
            nama_kunci = "mycarpet-pro" 
            kunci_rahsia = os.environ.get(nama_kunci)
            
            # Membina mesej laporan untuk dipaparkan di skrin
            laporan = "=== SISTEM DETEKTIF RALAT INDEX.PY ===\n\n"
            
            if kunci_rahsia:
                laporan += f"✅ BERJAYA: Kunci '{nama_kunci}' dijumpai!\n"
                laporan += f"Isi kunci kamu (3 huruf pertama): {kunci_rahsia[:3]}***\n\n"
                
                # 🚀 TULIS KOD UTAMA KAMU DI SINI:
                # (Sila letakkan fungsi atau kod Python kamu yang lain di bawah baris ini)
                
                laporan += "Status Aplikasi: Berjalan dengan baik tanpa ralat."
            else:
                laporan += f"❌ RALAT: Kunci '{nama_kunci}' TIADA atau KOSONG di dalam Vercel!\n"
                laporan += "Sila pastikan kamu sudah memasukkannya di menu Settings > Environment Variables pada Vercel."

            # Memaparkan hasil laporan yang berjaya ke skrin web
            self.wfile.write(laporan.encode('utf-8'))
            
        except Exception as e:
            # 🚨 JIKA ADA RALAT LAIN, BAHAGIAN INI AKAN MENANGKAPNYA
            mesej_ralat = "=== ⚠️ RALAT DIKESAN PADA KOD PYTHON ===\n\n"
            mesej_ralat += f"Jenis Masalah: {str(e)}\n\n"
            mesej_ralat += "--- Laporan Kerosakan Penuh (Traceback) ---\n"
            mesej_ralat += traceback.format_exc() # Menukar ralat penuh menjadi teks
            
            # Memaparkan teks ralat berwarna merah/putih terus ke skrin web kamu
            self.wfile.write(mesej_ralat.encode('utf-8'))
            
        return
