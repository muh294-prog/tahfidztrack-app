import datetime
import io
import os
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="TahfidzTrack SMP 8 IQIS", page_icon="📖", layout="wide"
)

# File Penyimpanan Data Local/Cache
DATA_FILE = "tahfidz_track_data.csv"

# Akun Guru untuk Akses
CREDENTIALS = {
    "mohfaizgufran@iqis.sch.id": "Tahfizsmp8!",
    "adnanputra@iqis.sch.id": "Tahfizsmp8!",
    "rafly@iqis.sch.id": "Tahfizsmp8!",
    "bagusammar@iqis.sch.id": "Tahfizsmp8!",
    "huzaifah@iqis.sch.id": "Tahfizsmp8!",
}

# Database Santri Per Kelas
DATABASE_SANTRI = {
    "KELAS VIIIA": [
        "Achmad Sakha Recca Al Fath - 2510288",
        "Ahmad Yasin Mubarak - 2510289",
        "Akhdan Dzakwan Ahmad - 2510290",
        "Al Ahnaf Gani Poetra - 2510291",
        "Andi Muh. Dzaka Dzarwah Alam - 2510292",
        "Andi Muh. Athallah Azka - 2510293",
        "Bintang Tahta Al Hidayah. T - 2510294",
        "Danish Darmawan Arsyad - 2510295",
        "Dwi Dzaky Al Ghozaly - 2510296",
        "Fadel Mubarak Ihsan - 2510297",
        "Iqbal Ghaisan Iskandar - 2510298",
        "Leon David Alexma Rava - 2510299",
        "Luqman Hakim Rumodar - 2510300",
        "M. Zayn Adzaky Nawir - 2510301",
        "Muh Al Fabian Syah - 2510302",
        "Muhammad Reyvan Risani Rahmatullah - 2510303",
        "Muh. Aimar Zahwan - 2510304",
        "Muh. Alif Arif - 2510305",
        "Muh. Rayyan Ramadhan - 2510306",
        "Muhammad Ridho Syahrir - 2510307",
        "Muhammad Uswah - 2510308",
    ],
    "KELAS VIIIC": [
        "Abdul Khaliq - 2510335",
        "Andi Al Walid Mappatonang - 2510336",
        "Andrea milan elshaarawi - 2510337",
        "Bilfaqih Alteza Hasid - 2510338",
        "Dzaky Putra Triatama - 2510339",
        "Fadhil Abdillah Hasan - 2510340",
        "Faiz Ibrahim - 2510341",
        "Faizi Almaz Al-Baariqh - 2510342",
        "I Datuk Mirza Hibatullah Zahri - 2510343",
        "M. Dhafin Harits J - 2510344",
        "Muh Rasya AlFatah S - 2510345",
        "Muh. Fathin Affandi - 2510346",
        "Muhammad Yasir Az Zuhri - 2510347",
        "Muhammad Al Furqan - 2510348",
        "Muhammad Ali Kurniawan - 2510349",
        "Muhammad Danish Achmad - 2510350",
        "Muhammad Fathan Rahman - 2510351",
        "Muhammad Fikhi Anugrah - 2510352",
        "Muhammad Shafwan - 2510353",
        "Muhammad Yassar Asman - 2510354",
        "Muhammad Zaid Y - zaq1",
        "Zayyan Akasyah - 2510356",
    ],
}


def load_data():
  if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(
        columns=[
            "Tanggal",
            "Guru Input",
            "Kelas",
            "Nama Santri",
            "Jenis Setoran",
            "Surah",
            "Ayat Awal",
            "Ayat Akhir",
            "Halaman",
            "Salah",
            "Nilai",
        ]
    )
    df_init.to_csv(DATA_FILE, index=False)
    return df_init
  return pd.read_csv(DATA_FILE)


def save_data(df):
  df.to_csv(DATA_FILE, index=False)


def generate_pdf(df_filtered, bulan_tahun, nama_kelas, guru_name):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=A4,
      rightMargin=20,
      leftMargin=20,
      topMargin=20,
      bottomMargin=20,
  )
  elements = []

  styles = getSampleStyleSheet()
  title_style = ParagraphStyle(
      "TitleStyle",
      parent=styles["Heading1"],
      fontName="Helvetica-Bold",
      fontSize=14,
      textColor=colors.HexColor("#1B4332"),
      alignment=1,
      spaceAfter=8,
  )

  subtitle_style = ParagraphStyle(
      "SubTitleStyle",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=10,
      textColor=colors.HexColor("#0A192F"),
      alignment=1,
      spaceAfter=15,
  )

  elements.append(
      Paragraph(
          "LAPORAN REKAPITULASI BULANAN TAHFIDZ QURAN", title_style
      )
  )
  elements.append(
      Paragraph(
          f"SMP 8 IQIS — {nama_kelas} | Periode: {bulan_tahun}",
          subtitle_style,
      )
  )

  table_data = [
      ["No", "Tanggal", "Nama Santri", "Jenis", "Surah (Ayat)", "Hlm", "Nilai"]
  ]
  for idx, row in df_filtered.reset_index(drop=True).iterrows():
    table_data.append([
        str(idx + 1),
        str(row["Tanggal"]),
        str(row["Nama Santri"]).split(" - ")[0][:18],
        str(row["Jenis Setoran"]),
        f"{row['Surah']} ({row['Ayat Awal']}-{row['Ayat Akhir']})",
        f"{row['Halaman']}",
        f"{row['Nilai']}",
    ])

  t = Table(table_data, colWidths=[25, 65, 140, 55, 140, 35, 45])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, 0), 8),
          ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
          ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FDFBF7")),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
          ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
          ("FONTSIZE", (0, 1), (-1, -1), 7.5),
      ])
  )
  elements.append(t)
  elements.append(Spacer(1, 15))

  ttd_text = (
      f"Makassar, {datetime.date.today().strftime('%d %B %Y')}\n"
      f"Guru Pembimbing Tahfidz,\n\n\n\n({guru_name})"
  )
  ttd_table = Table([["", ttd_text]], colWidths=[300, 200])
  ttd_table.setStyle(
      TableStyle([
          ("ALIGN", (1, 0), (1, 0), "CENTER"),
          ("FONTNAME", (1, 0), (1, 0), "Helvetica"),
          ("FONTSIZE", (1, 0), (1, 0), 8),
      ])
  )
  elements.append(ttd_table)

  doc.build(elements)
  buffer.seek(0)
  return buffer


# Sistem Session State untuk Login
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["user_email"] = ""

# Halaman Login
if not st.session_state["logged_in"]:
  st.title("🔒 Login - TahfidzTrack SMP 8 IQIS")
  with st.form("login_form"):
    email = st.text_input("Email Guru").strip().lower()
    password = st.text_input("Password", type="password").strip()
    submit = st.form_submit_button("Login")

    if submit:
      if email in CREDENTIALS and CREDENTIALS[email] == password:
        st.session_state["logged_in"] = True
        st.session_state["user_email"] = email
        st.success("Login berhasil!")
        st.rerun()
      else:
        st.error("Email atau password salah.")

else:
  # Sidebar Menu Aplikasi
  st.sidebar.title("📖 TahfidzTrack")
  st.sidebar.write(f"👤 **{st.session_state['user_email']}**")
  if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

  menu = st.sidebar.radio(
      "Menu Utama",
      [
          "➕ Input Setoran",
          "📋 Rekapan Data",
          "📊 Analisis Santri",
          "📄 Laporan PDF",
      ],
  )

  df_data = load_data()

  if menu == "➕ Input Setoran":
    st.header("Form Input Setoran Harian")

    col1, col2 = st.columns(2)
    with col1:
      kelas_sel = st.selectbox("Pilih Kelas", list(DATABASE_SANTRI.keys()))
      santri_sel = st.selectbox("Pilih Santri", DATABASE_SANTRI[kelas_sel])
      jenis_sel = st.selectbox(
          "Jenis Setoran", ["Sabaq", "Murajaah", "Manzil"]
      )
      surah_sel = st.text_input("Nama Surah", "Al-Baqarah")

    with col2:
      ayat_awal = st.number_input("Ayat Awal", min_value=1, value=1)
      ayat_akhir = st.number_input("Ayat Akhir", min_value=1, value=10)
      halaman = st.number_input("Jumlah Halaman", min_value=0.1, value=1.0)
      salah = st.number_input("Jumlah Salah", min_value=0, value=0)

    # Rumus Kalkulasi Nilai
    nilai_calc = max(0.0, round(100 - (salah * 2.85), 2))
    st.info(f"💡 Perhitungan Nilai Otomatis: **{nilai_calc}**")

    if st.button("💾 Simpan Record", use_container_width=True):
      new_record = {
          "Tanggal": datetime.date.today().strftime("%Y-%m-%d"),
          "Guru Input": st.session_state["user_email"],
          "Kelas": kelas_sel,
          "Nama Santri": santri_sel,
          "Jenis Setoran": jenis_sel,
          "Surah": surah_sel,
          "Ayat Awal": ayat_awal,
          "Ayat Akhir": ayat_akhir,
          "Halaman": halaman,
          "Salah": salah,
          "Nilai": nilai_calc,
      }
      df_updated = pd.concat(
          [df_data, pd.DataFrame([new_record])], ignore_index=True
      )
      save_data(df_updated)
      st.success(f"Data setoran {santri_sel} berhasil disimpan!")

  elif menu == "📋 Rekapan Data":
    st.header("Seluruh Rekapan Data Setoran")
    st.dataframe(df_data, use_container_width=True)

  elif menu == "📊 Analisis Santri":
    st.header("Analisis Capaian Hafalan Santri")
    if not df_data.empty:
      col_k, col_s = st.columns(2)
      with col_k:
        k_sel = st.selectbox("Kelas", list(DATABASE_SANTRI.keys()))
      with col_s:
        s_sel = st.selectbox("Santri", DATABASE_SANTRI[k_sel])

      df_filtered = df_data[df_data["Nama Santri"] == s_sel]
      if not df_filtered.empty:
        st.write(f"**Total Setoran:** {len(df_filtered)} kali")
        st.dataframe(df_filtered)
      else:
        st.warning("Belum ada data setoran untuk santri ini.")

  elif menu == "📄 Laporan PDF":
    st.header("Cetak Laporan Bulanan (PDF)")
    if not df_data.empty:
      df_data["Tanggal_DT"] = pd.to_datetime(df_data["Tanggal"])
      df_data["Bulan_Tahun"] = df_data["Tanggal_DT"].dt.strftime("%Y-%m")

      k_pdf = st.selectbox("Pilih Kelas", list(DATABASE_SANTRI.keys()))
      b_pdf = st.selectbox("Pilih Periode", df_data["Bulan_Tahun"].unique())

      df_pdf = df_data[
          (df_data["Kelas"] == k_pdf) & (df_data["Bulan_Tahun"] == b_pdf)
      ]

      if not df_pdf.empty:
        st.dataframe(df_pdf)
        pdf_bytes = generate_pdf(
            df_pdf, b_pdf, k_pdf, st.session_state["user_email"]
        )
        st.download_button(
            label="📥 Download PDF Laporan",
            data=pdf_bytes,
            file_name=f"Laporan_{k_pdf}_{b_pdf}.pdf",
            mime="application/pdf",
        )
      else:
        st.warning("Tidak ada data pada periode ini.")
        
