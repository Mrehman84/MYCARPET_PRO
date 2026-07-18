import streamlit as st
import pandas as pd
from datetime import datetime
from app import inisial_database_segar 
import time
from database import inisial_database_segar





    # --- MENU 2: TEMPAHAN BARU ---

def papar_menu_tempahan_baru(): # <--- TAMBAH BARIS INI
        # 1. Hubungkan sesi pangkalan data segar Google Sheets
        tab_harga, t_pelanggan, t_tempahan, t_karpet = inisial_database_segar() # <--- Tambah 4 space di depan (Indented)

        alamat_input = ""   # <--- Tambah 4 space di depan
        nama_input = ""     # <--- Tambah 4 space di depan
        telefon_input = ""  # <--- Tambah 4 space di depan
        daerah_input = ""   # <--- Tambah 4 space di depan


        # 2. Kotak pilihan jenis pendaftaran pelanggan
        status_pelanggan = st.radio("Status Pelanggan:", [
                                    "Pelanggan Sedia Ada", "Pelanggan Baru"], horizontal=True)

        # 3. Aliran logik untuk Pelanggan Sedia Ada
        data_p_mentah = t_pelanggan.get_all_values() if t_pelanggan else []
        df_p = pd.DataFrame()

        if status_pelanggan == "Pelanggan Sedia Ada":
            if len(data_p_mentah) > 1:
                df_p = pd.DataFrame(data_p_mentah[1:], columns=data_p_mentah[0])
                df_p.columns = [str(c).upper().strip() for c in df_p.columns]

            if not df_p.empty:
                # Cipta senarai paparan gabungan: "ID - Alamat" untuk memudahkan carian anda
                senarai_paparan = ["-- Sila Pilih Pelanggan --"]
                for idx, row in df_p.iterrows():
                    cus_id = str(row.get('CUSTOMER ID', '')).strip()
                    alamat_p = str(row.get('ALAMAT', '')).strip()
                    if cus_id and alamat_p:
                        senarai_paparan.append(f"{cus_id} - {alamat_p}")
                    else:
                        senarai_paparan.append(
                            cus_id if cus_id else f"Pelanggan {idx+1}")

                pilih_gabungan = st.selectbox(
                    "Pilih Pelanggan (ID - Alamat):", senarai_paparan)

                if pilih_gabungan != "-- Sila Pilih Pelanggan --":
                    id_asal = pilih_gabungan.split(" - ")[0].strip()
                    # Tapis mengikut ID yang sepadan
                    df_filtered = df_p[df_p['CUSTOMER ID'] == id_asal]
                    if not df_filtered.empty:
                        info_p = df_filtered.iloc[0]
                        nama_input = info_p.get('NAMA', '')
                        telefon_input = info_p.get('TELEFON', '')
                        alamat_input = info_p.get('ALAMAT', '')
                        daerah_input = info_p.get('DAERAH', '')

                        st.session_state["id_pelanggan_dipilih"] = id_asal
                        st.info(
                            f"👤 Pelanggan: {nama_input} | 📞 Tel: {telefon_input}")
        else:
            # Paparan Borang Input Manual untuk Pelanggan Baru
            nama_input = st.text_input("Nama Pelanggan Baru:")
            telefon_input = st.text_input("No. Telefon:")
            alamat_input = st.text_input("Alamat Rumah:")
            daerah_input = ""  # Dibiarkan kosong untuk manual kemudian mengikut permintaan

        st.markdown("---")
        st.subheader("🧺 Butiran Permaidani")

        # 4. Menguruskan penambahan/pengurangan bilangan borang permaidani secara dinamik
        if "bilangan_karpet" not in st.session_state:
            st.session_state.bilangan_karpet = 1

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("➕ Tambah Karpet", use_container_width=True):
                st.session_state.bilangan_karpet += 1
        with col_b2:
            if st.button("➖ Kurang Karpet", use_container_width=True) and st.session_state.bilangan_karpet > 1:
                st.session_state.bilangan_karpet -= 1

        # Tarik data senarai gred/kod karpet dari Google Sheets tab 'Harga' (SENARAI_HARGA)
        data_harga_mentah = tab_harga.get_all_values() if tab_harga else []
        df_harga_opt = pd.DataFrame()
        if len(data_harga_mentah) > 1:
            df_harga_opt = pd.DataFrame(
                data_harga_mentah[1:], columns=data_harga_mentah[0])
            df_harga_opt.columns = [str(c).upper().strip()
                                    for c in df_harga_opt.columns]

        data_karpet_borang = []
        total_harga_keseluruhan = 0.0

        # =========================================================================
        # 1. GELUNG (LOOPING) PEMBINAAN BARIS INPUT PERMAIDANI (VERSI PADANAN TEKSTUAL TEPAT)
        # =========================================================================
        # Pastikan bilangan_karpet sentiasa wujud dalam memori untuk mengelakkan ralat sistem kosong

        for i in range(st.session_state.bilangan_karpet):
            st.markdown(f"📊 **Karpet #{i+1}**")

            # Ambil senarai KOD dari tab Harga sebagai menu dropdown
            if not df_harga_opt.empty and 'KOD' in df_harga_opt.columns:
                senarai_kod_sheets = df_harga_opt['KOD'].dropna().tolist()
            else:
                senarai_kod_sheets = ["CK 4X6", "PELBAGAI"]

            # Kekalkan pilihan "CUSTOM (Saiz Sendiri)" di bahagian paling bawah senarai menu
            if "CUSTOM (Saiz Sendiri)" not in senarai_kod_sheets:
                senarai_kod_sheets.append("CUSTOM (Saiz Sendiri)")

            # Baris Pertama Lajur Input
            c1, c2, c3 = st.columns(3)
            with c1:
                kod_pilihan = st.selectbox(
                    f"Pilih Kod/Gred Karpet #{i+1}", senarai_kod_sheets, key=f"kod_{i}")

            # Semak jenis pilihan kod pengguna (Gunakan format huruf besar sepenuhnya untuk perbandingan)
            pilihan_clean = str(kod_pilihan).strip().upper()
            is_custom_manual = "CUSTOM (SAIZ SENDIRI)" in pilihan_clean

            # Tarik data padanan daripada database Google Sheets tab 'Harga'
            harga_default_sheets = 15.0
            jenis_default_sheets = "Cucian Carpet"

            if not df_harga_opt.empty and not is_custom_manual:
                # Lakukan padanan huruf secara selamat dengan menukar kedua-dua lajur kepada huruf besar sepenuhnya
                df_harga_opt['KOD_UPPER'] = df_harga_opt['KOD'].astype(
                    str).str.strip().str.upper()
                row_padan = df_harga_opt[df_harga_opt['KOD_UPPER']
                                        == pilihan_clean]

                if not row_padan.empty:
                    try:
                        # Ambil nilai lajur 'HARGA OPEN' dan bersihkan simbol RM
                        harga_raw = str(row_padan.iloc[0].get(
                            'HARGA OPEN', '15.0')).replace('RM', '').strip()
                        harga_default_sheets = float(harga_raw)
                        jenis_default_sheets = str(row_padan.iloc[0].get(
                            'JENIS CARPET', 'Carpet')).strip()
                    except Exception as e:
                        harga_default_sheets = 15.0
            elif is_custom_manual:
                harga_default_sheets = 2.50  # Harga asas per sqft untuk fungsi custom manual
                jenis_default_sheets = "CUSTOM"

            with c2:
                qty_k = st.number_input(
                    f"Kuantiti #{i+1}", min_value=1, value=1, step=1, key=f"qty_{i}")

            with c3:
                # Label bertukar dinamik tetapi kotak HARGA KEKAL BOLEH DIEDIT MANUAL
                label_harga = "Harga Per Sqft (RM) #" if is_custom_manual else "Harga Seunit (RM) #"
                harga_seunit = st.number_input(f"{label_harga}{i+1}", min_value=0.0, value=float(
                    harga_default_sheets), step=0.50, key=f"harga_base_{i}")

            # Aliran Logik Pengiraan Bersyarat & Kemunculan 5 Kotak Input Custom Manual
            if is_custom_manual:
                st.markdown(f"⚙️ *Konfigurasi Karpet Custom #{i+1}*")

                c_cust1, c_cust2 = st.columns(2)
                with c_cust1:
                    kod_custom_input = st.text_input(
                        f"Masukkan Kod Baru #{i+1} (Contoh: CT 4X6)", value="CUSTOM-KOD", key=f"custom_kod_{i}")
                with c_cust2:
                    jenis_custom_input = st.text_input(
                        f"Masukkan Jenis Karpet #{i+1} (Contoh: Carpet Tenun)", value="Carpet Tenun", key=f"custom_jenis_{i}")

                c_sz1, c_sz2, c_sz3 = st.columns(3)
                with c_sz1:
                    lebar_f = st.number_input(
                        f"Lebar (Kaki) #{i+1}", min_value=1.0, value=4.0, step=0.5, key=f"lebar_{i}")
                with c_sz2:
                    panjang_f = st.number_input(
                        f"Panjang (Kaki) #{i+1}", min_value=1.0, value=6.0, step=0.5, key=f"panjang_{i}")

                    # Formula Kira Luas dan Subtotal Harga Custom
                    luas_kaki = lebar_f * panjang_f
                    harga_seunit_kiraan = luas_kaki * harga_seunit
                    subtotal_harga = harga_seunit_kiraan * qty_k

                    with c_sz3:
                        st.text_input(
                            f"Jumlah Luas #{i+1}", value=f"{luas_kaki} sqft", disabled=True, key=f"luas_view_{i}")

                    kod_final = kod_custom_input
                    jenis_final = f"{jenis_custom_input.upper()} SAIZ {int(lebar_f)}X{int(panjang_f)}"
                    saiz_teks = f"{lebar_f}' x {panjang_f}' ({luas_kaki} sqft)"
                    harga_simpanan = harga_seunit_kiraan

            elif "PELBAGAI" in pilihan_clean:
                c_sz1, c_sz2, c_sz3 = st.columns(3)
                with c_sz1:
                    lebar_f = st.number_input(
                        f"Lebar (Kaki) #{i+1}", min_value=1.0, value=4.0, step=0.5, key=f"lebar_{i}")
                with c_sz2:
                    panjang_f = st.number_input(
                        f"Panjang (Kaki) #{i+1}", min_value=1.0, value=6.0, step=0.5, key=f"panjang_{i}")

                luas_kaki = lebar_f * panjang_f
                subtotal_harga = (luas_kaki * harga_seunit) * qty_k

                with c_sz3:
                    st.text_input(
                        f"Jumlah Luas (sqft) #{i+1}", value=f"{luas_kaki} sqft", disabled=True, key=f"luas_view_{i}")

                saiz_teks = f"{lebar_f}' x {panjang_f}' ({luas_kaki} sqft)"
                kod_final = kod_pilihan
                jenis_final = jenis_default_sheets
                harga_simpanan = luas_kaki * harga_seunit
            else:
                # Kategori Gred Standard (Dicantumkan semula supaya tiada ralat sintaks terputus)
                subtotal_harga = harga_seunit * qty_k
                saiz_teks = str(kod_pilihan).split(
                )[-1] if "X" in pilihan_clean else "Standard"

                kod_final = kod_pilihan
                jenis_final = jenis_default_sheets
                harga_simpanan = harga_seunit

                # Paparan maklumat ringkasan dinamik di bawah kotak input (Kini Membaca Data Dengan Betul)
                st.caption(f"ℹ️ **Jenis:** {jenis_final}")
                st.caption(
                    f"🌲 **Greenwood (Anggaran Asal Sheets):** RM {harga_default_sheets:.2f}")

            # Pastikan formula darab harga_seunit x qty_k digunakan untuk gred standard
                harga_paparan_sub = harga_seunit * \
                    qty_k if not is_custom_manual else subtotal_harga

                st.text_input(
                    f"Subtotal Harga Karpet #{i+1}",
                    value=f"RM {harga_paparan_sub:.2f}",
                    disabled=True,
                    key=f"sub_view_{i}_{kod_pilihan}_{qty_k}_{harga_seunit}"
                )

                total_harga_keseluruhan += subtotal_harga

                # Memasukkan data ke dalam senarai borang
                data_karpet_borang.append({
                    "kod": kod_final,
                    "jenis": jenis_final,
                    "qty": qty_k,
                    "harga": harga_simpanan,
                    "saiz": saiz_teks
                })

        st.markdown("---")
        st.metric("💰 Jumlah Keseluruhan Tempahan",
                f"RM {total_harga_keseluruhan:.2f}")

        # # 2. BUTANG SIMPAN TEMPAHAN (DI LUAR GELUNG KARPET)
        if st.button("💾 Sahkan & Simpan Tempahan Baru", use_container_width=True):
            
            # --- UTAMAKAN INI: Takrifkan next_inv di baris teratas butang simpan ---
            data_t_semasa = t_tempahan.get_all_values() if t_tempahan else []
            if len(data_t_semasa) > 1:
                nombor_turutan = (len(data_t_semasa) - 1) + 1
                next_inv = f"INV26{nombor_turutan:04d}"
            else:
                next_inv = "INV260001"

            tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
            harga_formatted = f"RM {total_harga_keseluruhan:.2f}"

            if status_pelanggan == "Pelanggan Sedia Ada":
                current_cus_id = st.session_state.get("id_pelanggan_dipilih", "CUS0001")
            else:
                data_p_semasa = t_pelanggan.get_all_values() if t_pelanggan else []
                if len(data_p_semasa) > 1:
                    current_cus_id = f"CUS{len(data_p_semasa):04d}"
                else:
                    current_cus_id = "CUS0001"

                if nama_input and telefon_input:
                    t_pelanggan.append_row([current_cus_id, nama_input, telefon_input, alamat_input, ""])

            # Masukkan rekod induk ke tab Tempahan
            baris_tempahan = [next_inv, tarikh_hari_ini, current_cus_id, harga_formatted, "Pending"]
            t_tempahan.append_row(baris_tempahan)

            # # 4. Simpan data per helai karpet ke tab Karpetsecara DINAMIK & BETUL
            counter_item = 1
            for i in range(st.session_state.bilangan_karpet):
                # Ambil data input secara langsung daripada setiap kotak baris #1, #2, #3 skrin
                kod_dinamik = st.session_state.get(f"kod_{i}", "PELBAGAI")
                qty_int = int(st.session_state.get(f"qty_{i}", 1))
                harga_seunit_dinamik = float(st.session_state.get(f"harga_base_{i}", 15.00))
                
                # Logik ambil jenis dan saiz teks mengikut perkiraan borang
                item_data = data_karpet_borang[i] if i < len(data_karpet_borang) else {"jenis": "Carpet", "saiz": "Standard"}
                jenis_dinamik = item_data.get("jenis", "Carpet")
                saiz_dinamik = item_data.get("saiz", "Standard")

                for _ in range(qty_int):
                    qr_id = f"{next_inv}-{counter_item}"
                    
                    baris_karpet = [
                        qr_id,                                # Lajur A: QR ID
                        next_inv,                             # Lajur B: INV NO
                        str(kod_dinamik).strip().upper(),     # Lajur C: KOD (Dinamik mengikut apa abang klik!)
                        str(jenis_dinamik).strip(),           # Lajur D: JENIS
                        f"RM {harga_seunit_dinamik:.2f}",     # Lajur E: HARGA
                        str(saiz_dinamik).strip(),            # Lajur F: Column 1 (SAIZ)
                        "DALAM PROSES"                            # Lajur G: STATUS
                    ]
                    t_karpet.append_row(baris_karpet)
                    counter_item += 1

            teks_senarai_karpet = ""
            for idx, item in enumerate(data_karpet_borang):
                teks_senarai_karpet += f"• ({idx+1}). {item['jenis'].upper()} ({item['saiz']}) \n"

            from datetime import timedelta
            tarikh_siap_anggaran = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")
            tarikh_ambil_format = datetime.now().strftime("%d-%m-%Y")

            mesej_wa = (
                f"*MYCARPET PRO v2.0*\n"
                f"Assalamualaikum / Salam Sejahtera,\n\n"
                f"Pelanggan yang dihormati, kami ingin memaklumkan bahawa karpet anda telah selamat diambil dan akan diproses untuk cucian. Berikut adalah maklumat pesanan anda:\n\n"
                f"• *No Invoice:* `{next_inv}` - ({alamat_input[:30]}...)\n"
                f"• *Tarikh Ambil:* {tarikh_ambil_format}\n"
                f"• *Tarikh Siap (Anggaran):* {tarikh_siap_anggaran}\n"
                f"• *Jumlah Karpet:* {st.session_state.bilangan_karpet} keping\n"
                f"• *Butiran Jenis Karpet:* \n{teks_senarai_karpet}\n"
                f"• *Jumlah Harga:* {harga_formatted}\n"
                f"• *Status:* Pickup & Proses Cucian\n\n"
                f"Sila hubungi kami jika anda mempunyai sebarang arahan khas atau ingin menjadualkan masa penghantaran yang sesuai nanti. Terima kasih kerana mempercayai perkhidmatan kami! 🙏✨"
            )

            st.session_state["data_tersimpan_state"] = True
            st.session_state["teks_resit_salinan"] = mesej_wa
            st.session_state["nota_sukses"] = f"🎉 Tempahan {next_inv} berjaya disimpan ke Google Sheets!"
            st.rerun()

        # Paparan Mesej Resit
        if st.session_state.get("data_tersimpan_state", False):
            st.success(st.session_state.get("nota_sukses", "Simpanan Berjaya!"))
            st.markdown("### 📱 Salinan Mesej WhatsApp Resit")
            st.info("💡 Sila klik butang ikon salin (Copy) di penjuru kanan atas kotak teks di bawah ini, kemudian buka aplikasi WhatsApp di laptop abang dan tekan 'Ctrl + V' untuk hantar kepada pelanggan.")
            st.code(st.session_state.get("teks_resit_salinan", ""), language="text")

        st.markdown("---")
        if st.button("🔄 Buka Borang Baru (Reset Skrin)", use_container_width=True):
            st.session_state.bilangan_karpet = 1
            st.session_state["data_tersimpan_state"] = False
            if "id_pelanggan_dipilih" in st.session_state:
                del st.session_state["id_pelanggan_dipilih"]
            st.rerun()



