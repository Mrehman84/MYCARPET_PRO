import io
import os
import streamlit as st
from fpdf import FPDF





def paparan_menu_invoice(sheet):
    st.title("🖨️ Cetak Invois & Resit Resmi")

    try:
        # 1. AMBIL LEMBARAN DATA
        ws_tempahan = sheet.worksheet("Tempahan")
        ws_karpet = sheet.worksheet("Karpet")
        ws_pelanggan = sheet.worksheet("Pelanggan")
        ws_payment = sheet.worksheet("Payment")

        data_tempahan = ws_tempahan.get_all_records()
        data_karpet = ws_karpet.get_all_records()
        data_pelanggan = ws_pelanggan.get_all_records()
        data_payment = ws_payment.get_all_records()
        # =====================================================================
        # FASA 1: TAPISAN DROPDOWN PINTAR (STATUS KARPET LAJUR G TAB KARPET)
        # =====================================================================
        inv_aktif_set = set()
        for k_row in data_karpet:
            k_inv = ""
            for k in k_row.keys():
                if k.strip().upper() in ["INV NO", "INV_NO", "NO INVOIS"]:
                    k_inv = str(k_row[k]).strip()
                    break

            status_karpet = ""
            for k in k_row.keys():
                if k.strip().upper() in ["STATUS", "STATUS KARPET"]:
                    status_karpet = str(k_row[k]).strip().upper()
                    break

            # Selagi ada karpet yang belum selesai dihantar, invois dikira aktif
            if k_inv and status_karpet != "SELESAI DIHANTAR":
                inv_aktif_set.add(k_inv)


        # =====================================================================
        # 3. BINA DROPDOWN PILIHAN GABUNGAN INV NO & ALAMAT (LOGIK MENU PAYMENT)
        # =====================================================================
        import pandas as pd
        df_tempahan = pd.DataFrame(data_tempahan)
        df_customer = pd.DataFrame(data_pelanggan)

        # Seragamkan nama lajur kepada Huruf Besar untuk mengelakkan ralat ejaan Sheets
        df_tempahan.columns = [str(c).upper().strip() for c in df_tempahan.columns]
        df_customer.columns = [str(c).upper().strip() for c in df_customer.columns]

        pilihan_options = []
        mapping_tempahan = {}

        if 'INV NO' in df_tempahan.columns:
            for idx, row in df_tempahan.iterrows():
                c_inv = str(row.get('INV NO', '-')).strip()
                c_cust_id = str(row.get('CUSTOMER ID', '-')).strip()
                
                # Hanya proses jika invois ini wujud dalam set invois aktif
                if c_inv in inv_aktif_set:
                    c_alamat = ""
                    if not df_customer.empty and c_cust_id != "-":
                        c_match = df_customer[df_customer['CUSTOMER ID'] == c_cust_id]
                        if not c_match.empty:
                            c_alamat = str(c_match.iloc[0].get('ALAMAT', '')).strip()
                    
                    teks_pilihan = f"{c_inv} | {c_alamat}" if c_alamat else f"{c_inv} | -"
                    pilihan_options.append(teks_pilihan)
                    
                    # Simpan baris data asal ke dalam dictionary untuk digunakan oleh row_utama di bawah
                    # Kita guna baris asal t_row dari data_tempahan supaya kod bawah adik tidak rosak
                    for original_row in data_tempahan:
                        if str(original_row.get("INV NO", original_row.get("INV_NO", ""))).strip() == c_inv:
                            mapping_tempahan[c_inv] = original_row
                            break

        invoice_terpilih = st.selectbox("🔍 Pilih Invoice & Alamat Pelanggan:", pilihan_options)

        # 3. PECATKAN STRING DROPDOWN UNTUK INV NO BERSIH (PUNCA SEBENAR DATA RM 0.00 KOSONG)
        inv_no_aktif = str(invoice_terpilih.split(" | ")[0]).strip()
        row_utama = mapping_tempahan[inv_no_aktif]


        

        # Pecahkan string dropdown untuk dapatkan INV NO yang bersih
        inv_no_aktif = str(invoice_terpilih.split(" | ")[0]).strip()
        row_utama = mapping_tempahan[inv_no_aktif]

        # 4. SINKRONISASI DATA PELANGGAN
        cust_id_asal = str(
            row_utama.get("CUSTOMER ID", row_utama.get("CUSTOMER_ID", ""))
        ).strip()

        alamat_pelanggan = str(row_utama.get("ALAMAT", "-")).strip()
        no_tel_pelanggan = "-"
        nama_pelanggan = cust_id_asal

        for p_row in data_pelanggan:
            p_id = str(
                p_row.get("CUSTOMER ID", p_row.get("CUSTOMER_ID", ""))
            ).strip()

                    # Memastikan nama lajur Customer ID dibaca dengan selamat tanpa mengira huruf besar atau kecil
        cust_id_asal = str(row_utama.get("CUSTOMER ID", row_utama.get("Customer ID", row_utama.get("customer id", "")))).strip()


        ## # 5. AMBIL REKOD DEPOSIT (TAB PAYMENT)
        deposit_nilai = 0.0
        for pay_row in data_payment:
            pay_inv = str(
                pay_row.get("INV NO", pay_row.get("INV_NO", ""))
            ).strip()
            if pay_inv == inv_no_aktif:
                try:
                    nilai_raw = 0
                    for k, v in pay_row.items():
                        if "AMAUN" in k.upper() or "DEPOSIT" in k.upper():
                            nilai_raw = v
                            break
                    
                    nilai_str = str(nilai_raw).replace("RM", "").strip()
                    deposit_nilai = float(nilai_str) if nilai_str else 0.0
                    break
                except:
                    deposit_nilai = 0.0
                    break


        # 6. EKSTRAK MULTI-ITEM KARPET (LAJUR JENIS & HARGA)
        senarai_karpet_invois = []
        sub_jumlah_karpet = 0.0

        for k_row in data_karpet:
            k_inv = ""
            for k in k_row.keys():
                if k.strip().upper() in ["INV NO", "INV_NO", "NO INVOIS"]:
                    k_inv = str(k_row[k]).strip()
                    break

            if k_inv == inv_no_aktif:
                try:
                    harga_raw = str(k_row.get("HARGA", 0)).replace("RM", "").strip()
                    harga_seunit = float(harga_raw) if harga_raw else 0.0
                except:
                    harga_seunit = 0.0

                unit = 1
                total_item = unit * harga_seunit
                sub_jumlah_karpet += total_item

                qr_id = str(k_row.get("QR ID", k_row.get("QR_ID", ""))).strip()
                jenis_carpet = str(
                    k_row.get("JENIS", "CUCIAN CARPET")
                ).strip()

                label_item = (
                    f"{jenis_carpet} [QR ID: {qr_id}]"
                    if qr_id
                    else jenis_carpet
                )
                senarai_karpet_invois.append(
                    {
                        "nama": label_item,
                        "unit": unit,
                        "harga_seunit": harga_seunit,
                        "total": total_item,
                    }
                )

        if not senarai_karpet_invois:
            try:
                harga_asal = float(
                    str(row_utama.get("JUMLAH HARGA", 0))
                    .replace("RM", "")
                    .strip()
                )
            except:
                harga_asal = 0.0
            sub_jumlah_karpet = harga_asal
            senarai_karpet_invois.append(
                {
                    "nama": "PERKHIDMATAN CUCIAN CARPET",
                    "unit": 1,
                    "harga_seunit": harga_asal,
                    "total": harga_asal,
                }
            )

        # 7. BORANG INPUT MANUAL UNTUK SERVIS TAMBAHAN
        st.write("---")
        st.subheader("➕ Tambah Perkhidmatan Ekstra (Manual)")
        col_servis, col_harga = st.columns(2)

        with col_servis:
            servis_tambahan_nama = st.text_input(
                "Keterangan Servis Tambahan:",
                placeholder="Contoh: Caj Urgen Delivery",
            )
        with col_harga:
            servis_tambahan_harga = st.number_input(
                "Harga Servis (RM):", min_value=0.0, step=1.0, value=0.0
            )

        # Hitung kalkulasi akhir secara real-time
        sub_jumlah_akhir = sub_jumlah_karpet + servis_tambahan_harga
        jumlah_bersih_akhir = sub_jumlah_akhir - deposit_nilai

        item_list_pdf = list(senarai_karpet_invois)
        if servis_tambahan_nama and servis_tambahan_harga > 0:
            item_list_pdf.append(
                {
                    "nama": f"{servis_tambahan_nama.upper()} (TAMBAHAN)",
                    "unit": 1,
                    "harga_seunit": servis_tambahan_harga,
                    "total": servis_tambahan_harga,
                }
            )

        # 8. PAPARAN PREVIU RINGKASAN SEBENAR DI SKRIN Streamlit
    # 1. AMBIL DATA DARI TAB PAYMENT MENGGUNAKAN KAEDAH GSPREAD ASLI
        try:
            data_p_mentah = sheet.worksheet("Payment").get_all_values()
        except:
            data_p_mentah = []

        import pandas as pd
        df_p = pd.DataFrame(data_p_mentah[1:], columns=[str(c).upper().strip() for c in data_p_mentah[0]]) if len(data_p_mentah) > 1 else pd.DataFrame()
        
                ## 2. HITUNG DEPOSIT DAN BAKI  17/7
                # # 2. HITUNG DEPOSIT DAN BAKI SECARA SELAMAT
                # # 2. HITUNG DEPOSIT DAN BAKI SECARA SELAMAT
        v_baki_bersih_akhir = sub_jumlah_akhir - deposit_nilai
        jumlah_bersih_akhir = sub_jumlah_akhir - deposit_nilai
        v_baki_bersih = sub_jumlah_akhir - deposit_nilai  # <--- TAMBAH NAMA INI JUGA



      
        st.write("---")
        st.subheader("👀 Previu Ringkasan Invois")

        tarikh_inv = str(
            row_utama.get("TARIKH", row_utama.get("Tarikh", "-"))
        ).strip()
        status_inv = str(
            row_utama.get("STATUS", row_utama.get("Status", "PENDING"))
        ).strip()

        with st.container(border=True):
            st.write(
                f"**NO INVOIS:** {inv_no_aktif} | **TARIKH:** {tarikh_inv}"
            )
            st.write(
                f"**PELANGGAN:** {cust_id_asal} - {nama_pelanggan} | **TEL:** {no_tel_pelanggan}"
            )
            st.write(f"**ALAMAT KIRIM:** {alamat_pelanggan}")
            st.write("**SENARAI REKOD ITEM KARPET:**")
            for idx, item in enumerate(item_list_pdf, 1):
                st.text(
                    f"  {idx}. {item['nama']} x{item['unit']} - RM {item['total']:.2f}"
                )

            st.write(
                f"💰 **Sub Jumlah Keseluruhan:** RM {sub_jumlah_akhir:.2f} | **Deposit Ditolak:** RM {deposit_nilai:.2f}"
            )
            st.info(
             f"🔴 **BAKI JUMLAH BERSIH (PERLU DIBAYAR):** RM {jumlah_bersih_akhir:.2f}" #DIGANTI UNUTK LIHAT BAKI DI JUMLAH INVOICE 17/7
         )

            

        data_pdf_input = {
            "inv_no": inv_no_aktif,
            "tarikh": tarikh_inv,
            "customer_id": f"{cust_id_asal} - {nama_pelanggan}".strip(" - "),
            "alamat": alamat_pelanggan,
            "no_telefon": no_tel_pelanggan,
            "status": status_inv,
            "sub_jumlah": sub_jumlah_akhir,
            "deposit": deposit_nilai,
            "jumlah_bersih": v_baki_bersih_akhir,#17/7 DIUBAHSUAI
        }

        # JANA ENGINE PDF
        pdf_file = jana_pdf_invois_terkini(data_pdf_input, item_list_pdf)

        st.download_button(
            label="📥 Generate & Send PDF Invoice",
            data=pdf_file,
            file_name=f"Invoice_{inv_no_aktif}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        # 1. BUTANG MUAT TURUN PDF (KEDUKAN ASAL)
        st.download_button(
            label="📥 Download PDF Invoice",
            data=pdf_file,
            file_name=f"Invoice_{inv_no_aktif}.pdf",
            mime="application/pdf"
        )
       
        

        # 2. AUTOMATIK HANTAR WHATSAPP MENGIKUT NOMBOR TELEFON DATA PELANGGAN
        try:
            # Mengambil nombor telefon sebenar dari pemboleh ubah 'no_tel_pelanggan' yang sedia ada di baris atas
            no_tel_wa = str(no_tel_pelanggan).strip()
            
            # Membersihkan nombor telefon daripada sebarang simbol atau spasi kosong
            no_tel_wa = "".join(c for c in no_tel_wa if c.isdigit())
            
            # Memastikan format kod negara Malaysia (60) adalah betul
            if no_tel_wa.startswith("0"):
                no_tel_wa = "6" + no_tel_wa
            elif not no_tel_wa.startswith("60") and no_tel_wa:
                no_tel_wa = "60" + no_tel_wa

            # Membina ayat mesej ringkasan baki automatik
            mesej_wa = (
                f"Salam *{nama_pelanggan}*, ini adalah maklumat baki invois rasmi dari MYCARPET PRO.\n\n"
                f"🧾 *No. Invois:* {inv_no_aktif}\n"
                f"💰 *Jumlah Keseluruhan:* RM {sub_jumlah_akhir:.2f}\n"
                f"🔴 *Baki Perlu Dibayar:* RM {v_baki_bersih:.2f}\n\n"
                f"Sila . Terima kasih! 🙏"
            )
            
            import urllib.parse
            # Menukarkan teks mesej menjadi pautan URL WhatsApp yang sah
            link_whatsapp = f"https://wa.me/{no_tel_wa}?text={urllib.parse.quote(mesej_wa)}"
            
            # Memaparkan butang hijau WhatsApp secara rasmi
            st.link_button("🟢 Hantar Invois & Mesej ke WhatsApp", link_whatsapp, use_container_width=True)
        except Exception as wa_error:
            st.warning(f"Nota: Butang WhatsApp gagal dibina kerana isu data nombor: {wa_error}")


    except Exception as err:
        st.error(f"Ralat sistem pemprosesan fail invoice: {err}")


def jana_pdf_invois_terkini(data_invois, item_list):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    status_str = str(data_invois["status"]).upper()
    is_paid = "DITERIMA" in status_str or "PAID" in status_str

    if is_paid:
        r_brand, g_brand, b_brand = 40, 167, 69
        r_bg, g_bg, b_bg = 240, 255, 240
    else:
        r_brand, g_brand, b_brand = 255, 109, 0
        r_bg, g_bg, b_bg = 255, 240, 240


    # Logo Rasmi PNG
    logo_path = "logo_westberry.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=15, y=10, w=58)
    else:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.text(15, 17, "WESTBERRY ENTERPRISE")

    # Tajuk Atas
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(r_brand, g_brand, b_brand)
    pdf.set_xy(120, 10)
    pdf.cell(75, 10, "INVOICE", ln=1, align="R")

    # Info Box Kanan Atas
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(145, 20)
    pdf.cell(20, 5, "INVOICE NO", border=1, align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(30, 5, data_invois["inv_no"], border=1, align="C", ln=1)

    pdf.set_x(145)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(20, 5, "DATE", border=1, align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(30, 5, str(data_invois["tarikh"]), border=1, align="C", ln=1)

    # Info Kedai
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(15, 26)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 4, "WESTBERRY ENTERPRISE", ln=1)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
        # GANTIKAN BARIS 391 HINGGA 395 DENGAN KOD BERSIH INI:
    pdf.set_xy(15, 30)  # Menetapkan kedudukan awal teks info kedai
    pdf.cell(100, 4, "LOT 52 JALAN PERUSAHAAN, KG SIAM,", ln=1)
    
    pdf.set_x(15)       # Kekalkan ke kiri untuk baris kedua
    pdf.cell(100, 4, "PAYA BESAR 09600 LUNAS KEDAH.", ln=1)
    
    pdf.set_x(15)       # Kekalkan ke kiri untuk baris ketiga
    pdf.cell(100, 4, "TEL: 017-4050336", ln=1)

    
    pdf.ln(4)

    # Banner "INVOICE TO"
    pdf.set_fill_color(r_brand, g_brand, b_brand)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(180, 6, " INVOICE TO", ln=1, fill=True)

    pdf.ln(2)
    y_penerima = pdf.get_y()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(120, 5, data_invois["customer_id"], ln=1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.multi_cell(120, 4, f"Alamat: {data_invois['alamat']}")
    pdf.set_x(15)
    pdf.cell(120, 4, f"No. Telefon: {data_invois['no_telefon']}", ln=1)

    # Badge Status
    pdf.set_xy(160, y_penerima)
    pdf.set_draw_color(r_brand, g_brand, b_brand)
    pdf.set_fill_color(r_bg, g_bg, b_bg)
    pdf.set_text_color(r_brand, g_brand, b_brand)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(35, 7, status_str, border=1, align="C", fill=True)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_xy(15, y_penerima + 18)

    # Jadual Karpet
    pdf.set_fill_color(r_brand, g_brand, b_brand)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(10, 6, "BIL", border=1, align="C", fill=True)
    pdf.cell(100, 6, "KETERANGAN SERVIS / JENIS CARPET", border=1, fill=True)
    pdf.cell(15, 6, "UNIT", border=1, align="C", fill=True)
    pdf.cell(28, 6, "HARGA SEUNIT (RM)", border=1, align="C", fill=True)
    pdf.cell(27, 6, "TOTAL (RM)", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8.5)

    for idx, item in enumerate(item_list, 1):
        pdf.cell(10, 6, str(idx), border=1, align="C")
                # === KOD AUTO-FIT FON UNTUK KETERANGAN KARPET ===
        teks_karpet = f"{item['nama']}"
        panjang_huruf = len(teks_karpet)
        
        # Mengira saiz fon secara automatik berdasarkan panjang teks
        if panjang_huruf > 65:
            saiz_fon_dinamik = 6.5
        elif panjang_huruf > 50:
            saiz_fon_dinamik = 7.5
        else:
            saiz_fon_dinamik = 8.5  # Mengikut saiz standard fail Anda di baris 442
            
        # Set fon dinamik sebelum cetak lajur keterangan
        pdf.set_font("Helvetica", "", saiz_fon_dinamik)
        pdf.cell(100, 6, teks_karpet, border=1)
        
        # Kembalikan semula saiz fon standard untuk petak lajur seterusnya
        pdf.set_font("Helvetica", "", 8.5)

        pdf.cell(15, 6, str(item['unit']), border=1, align="C")
        pdf.cell(28, 6, f"{item['harga_seunit']:.2f}", border=1, align="R")
        pdf.cell(27, 6, f"{item['total']:.2f}", border=1, align="R")
        pdf.ln()

    # Blok Kewangan Kanan Bawah
    pdf.ln(2)
    y_total = pdf.get_y()
    pdf.set_font("Helvetica", "B", 8.5)

    pdf.set_xy(125, y_total)
    pdf.cell(33, 5, "SUB TOTAL", border=1)
    pdf.cell(27, 5, f"RM {data_invois['sub_jumlah']:.2f}", border=1, align="R")

    pdf.set_xy(125, y_total + 5)
    pdf.cell(33, 5, "DEPOSIT", border=1)
    pdf.cell(27, 5, f"RM {data_invois['deposit']:.2f}", border=1, align="R")

    pdf.set_xy(125, y_total + 10)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(33, 5, "JUMLAH BERSIH", border=1, fill=True)
    pdf.cell(
        27,
        5,
        f"RM {data_invois['jumlah_clean']:.2f}"
        if "jumlah_clean" in data_invois
        else f"RM {data_invois['jumlah_bersih']:.2f}",
        border=1,
        align="R",
        fill=True,
    )

    # Info Bank Pembayaran
    pdf.set_xy(15, y_total + 15)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(50, 3.5, "UNTUK PEMBAYARAN:", ln=1)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(50, 4.5, "MAYBANK-MATI-UR REHMAN", ln=1)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(180, 40, 40)
    pdf.cell(50, 4.5, "15-203-142-4070", ln=1)

    # === TAMBAHAN NOTA PROFESIONAL DI BAHAGIAN BAWAH INVOIS ===
    pdf.ln(20)  # Memberi ruang kosong ke bawah supaya tidak rapat dengan jadual
    
    # Bahagian 1: Terma & Syarat Pembayaran
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 100, 100)  # Warna kelabu korporat
    pdf.cell(0, 4, "TERMA & SYARAT PEMBAYARAN:", ln=1)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 4, "1. Sila jelaskan baki bayaran penuh semasa penghantaran atau pengambilan karpet dilakukan.", ln=1)
    pdf.cell(0, 4, "2. Sila sertakan resit/bukti transaksi Online Transfer kepada pihak kami untuk pengesahan baki.", ln=1)
    
    pdf.ln(10)  # Jarakkan sedikit sebelum ucapan terima kasih
    
    # Bahagian 2: Nota Penghargaan & Terima Kasih
    pdf.set_font("Helvetica", "BI", 9)  # Bold + Italic (BI)
    pdf.set_text_color(40, 167, 69)     # Warna hijau kejayaan (Success Green)
    pdf.cell(0, 5, "Thank you for your business! We look forward to serving you again.", ln=1, align="C")
    pdf.cell(0, 5, "~~~ Terima kasih kerana memilih MYCARPET PRO! Sokongan Anda amat kami hargai ~~~", ln=1, align="C")
    # =========================================================

    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output())
    pdf_output.seek(0)
    return pdf_output

      