    
import streamlit as st

def papar_menu_temujanji():
    st.markdown("## 📅 Penjana Mesej Slot Janji Temu")
    
    # Kotak input manual untuk alamat
    alamat_manual = st.text_area("Masukkan Alamat Pelanggan:", placeholder="Contoh: No 32, Jalan Seri Abadi...")
    
    # Membuat semula lajur tarikh dan masa
    col_tarikh, col_masa = st.columns(2)
    
    with col_tarikh:
        tarikh_manual = st.date_input("Pilih Tarikh Ambil:", format="DD-MM-YYYY")
        
    with col_masa:
        masa_manual = st.text_input("Masukkan Masa Ambil:", placeholder="Contoh: 10:30 AM")
        
    # Formatkan tarikh dalam bentuk teks
    tarikh_format = tarikh_manual.strftime("%d-%m-%Y")
    
    # Struktur draf mesej WhatsApp
    skrip_slot = f"""*Pusat Cucian Karpet MyCarpetPro v2.0*

Slot janji temu untuk pengambilan karpet anda telah dimasukkan ke dalam sistem kami:
🗓️ *Tarikh:* {tarikh_format}
⏰ *Masa:* {masa_manual}
📍 *Alamat:* {alamat_manual}

Sila maklumkan kepada kami jika anda perlu menukar slot ini. Terima kasih kerana mempercayai perkhidmatan kami!"""

    st.markdown("---")
    # Paparan kotak teks baharu dengan butang COPY otomatis di penjuru kanan atas
    st.write("Salin Mesej di Bawah:")
    st.code(skrip_slot, language="text")
