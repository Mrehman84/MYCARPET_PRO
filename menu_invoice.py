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
        # 3. BINA DROPDOWN PILIHAN GABUNGAN INV NO & ALAMAT (DARI TAB PELANGGAN)
        # =====================================================================
        pilihan_options = []
        mapping_tempahan = {}

        # Sediakan pemetaan untuk mencari alamat dari data_pelanggan
        mapping_alamat_pelanggan = {}
        for p_row in data_pelanggan:
            p_id = str(p_row.get("CUSTOMER ID", p_row.get("CUSTOMER_ID", ""))).strip().upper()
            p_alamat = str(p_row.get("ALAMAT", "")).strip()
            if p_id:
                mapping_alamat_pelanggan[p_id] = p_alamat

        for t_row in data_tempahan:
            inv_no = str(t_row.get("INV NO", t_row.get("INV_NO", ""))).strip()
            cust_id_t = str(t_row.get("CUSTOMER ID", t_row.get("CUSTOMER_ID", ""))).strip().upper()

            # Cari alamat yang sepadan secara dinamik berdasarkan CUSTOMER ID tab Pelanggan
            alamat_pangkalan = mapping_alamat_pelanggan.get(cust_id_t, "")

            if inv_no in inv_aktif_set:
                # GABUNGAN DINAMIK: Nombor invois berserta alamat dari tab Pelanggan
                label = f"{inv_no} | {alamat_pangkalan[:50]}" if alamat_pangkalan else f"{inv_no} | -"
                pilihan_options.append(label)
                mapping_tempahan[inv_no] = t_row

        if not pilihan_options:
            st.success("🎉 Cemerlang! Semua karpet bagi semua tempahan telah bertukar status kepada 'SELESAI DIHANTAR'.")
            return

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

            if p_id.upper() == cust_id_asal.upper() and p_id != "":
                if p_row.get("NAMA"):
                    nama_pelanggan = str(p_row.get("NAMA")).strip()
                if p_row.get("TELEFON"):
                    no_tel_pelanggan = str(p_row.get("TELEFON")).strip()
                if p_row.get("ALAMAT"):
                    alamat_pelanggan = str(p_row.get("ALAMAT")).strip()
                break

        # 5. 🛠️ AMBIL REKOD DEPOSIT (DIPERBAIKI SECARA TOTAL UNTUK MENGESAN SPASI HANTU)
        deposit_nilai = 0.0
        for pay_row in data_payment:
            pay_inv = ""
            for k in pay_row.keys():
                if str(k).strip().upper() in ["INV NO", "INV_NO", "NO INVOIS", "NO_INVOIS"]:
                    pay_inv = str(pay_row[k]).strip().upper()  # Membersihkan spasi hantu
                    break
            
            # Padankan invois tanpa gangguan spasi
            if pay_inv == str(inv_no_aktif).strip().upper():
                for k in pay_row.keys():
                    if str(k).strip().upper() in ["DEPOSIT", "JUMLAH BAYARAN", "BAYARAN", "AMBUL DEPOSIT", "JUMLAH HARGA"]:
                        try:
                            nilai_raw = str(pay_row[k]).replace("RM", "").strip()
                            deposit_nilai = float(nilai_raw) if nilai_raw else 0.0
                        except:
                            deposit_nilai = 0.0
                        break
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
                f"🔴 **BAKI JUMLAH BERSIH (PERLU DIBAYAR): RM {jumlah_bersih_akhir:.2f}**"
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
            "jumlah_bersih": jumlah_bersih_akhir,
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

    except Exception as err:
        st.error(f"Ralat sistem pemprosesan fail invoice: {err}")

# =====================================================================
        # TAMBAHAN BARU: BUTANG KONGSI KE WHATSAPP (TIDAK MENGUSIK KOD ASAL)
        # =====================================================================
    st.write("---")
    st.subheader("📲 Kongsi Nota / Invois ke WhatsApp")

    no_tel_bersih = str(no_tel_pelanggan).strip().replace("-", "").replace(" ", "")
        
    if no_tel_bersih and not no_tel_bersih.startswith("60"):
            if no_tel_bersih.startswith("0"):
                no_tel_bersih = "60" + no_tel_bersih[1:]
            else:
                no_tel_bersih = "60" + no_tel_bersih

    mesej_whatsapp = (
            f"Salam Sejahtera, En/Puan *{nama_pelanggan}*.\n\n"
            f"Berikut adalah ringkasan Invois Rasmi daripada *Westberry Enterprise*:\n"
            f"📄 *No. Invois:* {inv_no_aktif}\n"
            f"💰 *Jumlah Perlu Dibayar:* RM {jumlah_bersih_akhir:.2f}\n"
            f"📌 *Status Pembayaran:* {status_inv}\n\n"
            f"Sila muat turun fail PDF invois penuh yang telah kami hantar atau simpan. Terima kasih kerana memilih perkhidmatan kami! 🙏"
        )

    import urllib.parse
    mesej_encoded = urllib.parse.quote(mesej_whatsapp)
            # 🛠️ PEMBETULAN PAUTAN URL: Menggunakan wa.me yang dijamin lancar untuk telefon & laptop
    pautan_whatsapp_api = f"https://wa.me/{no_tel_bersih}?text={mesej_encoded}"


    st.link_button(
            label="🟢 Hantar Ringkasan Invois ke WhatsApp Pelanggan",
            url=pautan_whatsapp_api,
            use_container_width=True
        )
    
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

    # Watermark
    pdf.set_font("Helvetica", "B", 34)
    pdf.set_text_color(242, 242, 242)
    with pdf.rotation(angle=25, x=100, y=150):
        pdf.text(35, 150, "WESTBERRY\n    CUCI CUCI CARPET")

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
    pdf.multi_cell(
        100,
        3.5,
        "LOT 52 JALAN PERUSAHAAN, KG SIAM,\nPAYA BESAR 09600 LUNAS KEDAH.\nTEL: 017-4050336",
    )
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
        pdf.cell(100, 6, f" {item['nama']}", border=1)
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
    pdf.cell(50, 4.5, "Hong Leong Bank", ln=1)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(180, 40, 40)
    pdf.cell(50, 4.5, "05-901-032-897", ln=1)

    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output())
    pdf_output.seek(0)
    return pdf_output

 