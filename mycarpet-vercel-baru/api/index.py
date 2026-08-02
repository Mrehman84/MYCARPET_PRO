from http.server import BaseHTTPRequestHandler
import os
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Hantar isyarat selamat kepada komputer/web
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        
        try:
            laporan = "=== SISTEM DETEKTIF KUNCI GOOGLE (INDEX.PY) ===\n\n"
            
            # 🕵️‍♂️ Menyemak Kunci Pertama: GOOGLE_CLIENT_EMAIL
            kunci_email = os.environ.get("GOOGLE_CLIENT_EMAIL")
            if kunci_email:
                laporan += "✅ BERJAYA: Kunci 'GOOGLE_CLIENT_EMAIL' dijumpai!\n"
                laporan += f"   Isi email: {kunci_email}\n\n"
            else:
                laporan += "❌ RALAT: Kunci 'GOOGLE_CLIENT_EMAIL' TIADA/KOSONG!\n\n"
                
            # 🕵️‍♂️ Menyemak Kunci Kedua: GOOGLE_PRIVATE_KEY
            kunci_private = os.environ.get("GOOGLE_PRIVATE_KEY")
            if kunci_private:
                laporan += "✅ BERJAYA: Kunci 'GOOGLE_PRIVATE_KEY' dijumpai!\n"
                laporan += f"   Panjang teks kunci: {len(kunci_private)} huruf\n\n"
                
                # Petunjuk Tambahan untuk Masalah Vercel yang Popular:
                if "\\n" in kunci_private:
                    laporan += "⚠️ AMARAN DETEKTIF:\n"
                    laporan += "Kunci private kamu mengandungi tulisan '\\n'.\n"
                    laporan += "Kadang-kadang Vercel keliru dengan tulisan ini.\n"
                    laporan += "Pastikan kod utama kamu ada fungsi '.replace(\"\\\\n\", \"\\n\")' ya!\n\n"
            else:
                laporan += "❌ RALAT: Kunci 'GOOGLE_PRIVATE_KEY' TIADA/KOSONG!\n\n"

            laporan += "=== TAMAT SEMAKAN ==="
            self.wfile.write(laporan.encode('utf-8'))
            
        except Exception as e:
            # Jika ada ralat lain yang menyebabkan robot tersangkut
            mesej_ralat = "=== ⚠️ RALAT DIKESAN PADA KOD ===\n\n"
            mesej_ralat += f"Masalah: {str(e)}\n\n"
            mesej_ralat += traceback.format_exc()
            self.wfile.write(mesej_ralat.encode('utf-8'))
            
        return
