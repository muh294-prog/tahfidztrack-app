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
    page_title="TahfidzTrack SMP 8 IQIS",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS Premium & Modern)
st.markdown(
    """
<style>
    /* Main Theme Styling */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.3);
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #FFFFFF !important;
        letter-spacing: 0.5px;
    }
    
    .main-header p {
        font-size: 14px;
        margin-top: 6px;
        opacity: 0.9;
    }

    /* Metric/Card Box */
    .card-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #10B981;
    }
    
    .metric-label {
        font-size: 13px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Primary Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.5) !important;
    }

    /* Custom Badges */
    .badge-success {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
    }
    
    /* Input Form Enhancements */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        border-radius: 10px !important;
        border-color: #334155 !important;
        background-color: #1E293B !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# File Penyimpanan Data
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
      textColor=colors.HexColor("#10B981"),
      alignment=1,
      spaceAfter=8,
  )

  subtitle_style = ParagraphStyle(
      "SubTitleStyle",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=10,
      textColor=colors.HexColor("#0F172A"),
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
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#059669")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, 0), 8),
          ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
          ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
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


# Session State Login
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["user_email"] = ""

# Halaman Login Modern
if not st.session_state["logged_in"]:
  st.markdown(
      """
      <div class="main-header">
          <h1>📖 TahfidzTrack SMP 8 IQIS</h1>
          <p>Sistem Management & Monitoring Hafalan Qur'an Santri</p>
      </div>
  """,
      unsafe_allow_html=True,
  )

  col_center, _ = st.columns([2, 1])
  with col_center:
    with st.form("login_form"):
      st.subheader("🔐 Login Ustadz / Ustazdah")
      email = st.text_input("Email Resmi", placeholder="contoh: ustadz@iqis.sch.id")
      password = st.text_input(
          "Kata Sandi", type="password", placeholder="••••••••"
      )
      submit = st.form_submit_button("Masuk Ke Sistem ➔")

      if submit:
        email_clean = email.strip().lower()
        pass_clean = password.strip()
        if (
            email_clean in CREDENTIALS
            and CREDENTIALS[email_clean] == pass_clean
        ):
          st.session_state["logged_in"] = True
          st.session_state["user_email"] = email_clean
          st.success("Login Berhasil! Membuka Dasbor...")
          st.rerun()
        else:
          st.error("Email atau Kata Sandi tidak sesuai.")

else:
  # Sidebar Navigation Menu
  st.sidebar.markdown(
      """
      <div style="text-align: center; padding: 10px 0;">
          <h2 style="color: #10B981; margin: 0; font-weight: 800;">📖 TahfidzTrack</h2>
          <p style="font-size: 12px; color: #94A3B8;">SMP 8 IQIS Portal</p>
      </div>
  """,
      unsafe_allow_html=True,
  )

  st.sidebar.markdown(
      f"👤 **Pembimbing:**\n`<span class='badge-success'>{st.session_state['user_email']}</span>`",
      unsafe_allow_html=True,
  )
  st.sidebar.write("")

  menu = st.sidebar.radio(
      "Menu Utama",
      [
          "📝 Input Setoran",
          "📊 Rekapan & Statistik",
          "🔍 Dashboard Santri",
          "📄 Cetak Laporan PDF",
      ],
  )

  if st.sidebar.button("🚪 Keluar / Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

  df_data = load_data()

  # MENU 1: INPUT SETORAN
  if menu == "📝 Input Setoran":
    st.markdown(
        """
        <div class="main-header">
            <h1>📝 Form Input Setoran Harian</h1>
            <p>Catat capaian hafalan harian Sabaq, Murajaah, atau Manzil santri</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
      c1, c2 = st.columns(2)
      with c1:
        kelas_sel = st.selectbox("🏷️ Pilih Kelas", list(DATABASE_SANTRI.keys()))
        santri_sel = st.selectbox(
            "👦 Nama Santri", DATABASE_SANTRI[kelas_sel]
        )
        jenis_sel = st.selectbox(
            "📌 Jenis Setoran", ["Sabaq", "Murajaah", "Manzil"]
        )
        surah_sel = st.text_input("📖 Nama Surah", "Al-Baqarah")

      with c2:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
          ayat_awal = st.number_input("🔢 Ayat Awal", min_value=1, value=1)
        with col_a2:
          ayat_akhir = st.number_input("🔢 Ayat Akhir", min_value=1, value=10)

        halaman = st.number_input(
            "📄 Jumlah Halaman", min_value=0.1, value=1.0, step=0.5
        )
        salah = st.number_input("⚠️ Jumlah Salah / Bantuan", min_value=0, value=0)

    # Indikator Nilai Real-time
    nilai_calc = max(0.0, round(100 - (salah * 2.85), 2))

    st.write("")
    m1, m2 = st.columns(2)
    with m1:
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Perhitungan Skor Kelancaran</div>
              <div class="metric-value">{nilai_calc} <span style="font-size:18px; color:#94A3B8;">/ 100</span></div>
          </div>
      """,
          unsafe_allow_html=True,
      )
    with m2:
      kualitas = (
          "Mumtaz (Sangat Baik)"
          if nilai_calc >= 90
          else ("Jayyid Jiddan (Baik)" if nilai_calc >= 75 else "Maqbul (Cukup)")
      )
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Predikat Prediksi</div>
              <div class="metric-value" style="font-size: 22px; color: #34D399; padding-top:8px;">{kualitas}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )

    if st.button("💾 SIMPAN SETORAN SANTRI", use_container_width=True):
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
      st.balloons()
      st.success(
          f"Alhamdulillah! Data setoran {santri_sel.split(' - ')[0]} telah berhasil disimpan."
      )

  # MENU 2: REKAPAN & STATISTIK
  elif menu == "📊 Rekapan & Statistik":
    st.markdown(
        """
        <div class="main-header">
            <h1>📊 Data Rekapan & Statistik Tahfidz</h1>
            <p>Ringkasan performa dan riwayat lengkap seluruh setoran santri</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    k1, k2, k3 = st.columns(3)
    with k1:
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Total Setoran Masuk</div>
              <div class="metric-value">{len(df_data)}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )
    with k2:
      total_hlm = df_data["Halaman"].sum() if not df_data.empty else 0
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Total Halaman Tersetor</div>
              <div class="metric-value">{round(total_hlm, 1)}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )
    with k3:
      avg_score = round(df_data["Nilai"].mean(), 1) if not df_data.empty else 0
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Rata-rata Nilai Santri</div>
              <div class="metric-value">{avg_score}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )

    st.subheader("📋 Tabel Riwayat Setoran")
    st.dataframe(df_data, use_container_width=True)

  # MENU 3: DASHBOARD SANTRI
  elif menu == "🔍 Dashboard Santri":
    st.markdown(
        """
        <div class="main-header">
            <h1>🔍 Monitoring Perkembangan Santri</h1>
            <p>Cek statistik individual hafalan santri secara rinci</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    c_k, c_s = st.columns(2)
    with c_k:
      k_sel = st.selectbox("Pilih Kelas", list(DATABASE_SANTRI.keys()))
    with c_s:
      s_sel = st.selectbox("Pilih Nama Santri", DATABASE_SANTRI[k_sel])

    df_filtered = df_data[df_data["Nama Santri"] == s_sel]

    if not df_filtered.empty:
      p1, p2, p3 = st.columns(3)
      with p1:
        st.metric(
            "Jumlah Setoran", f"{len(df_filtered)} Kali", delta="Aktivitas"
        )
      with p2:
        st.metric(
            "Capaian Halaman",
            f"{df_filtered['Halaman'].sum()} Hlm",
            delta="Progres",
        )
      with p3:
        st.metric(
            "Rata-rata Nilai",
            f"{round(df_filtered['Nilai'].mean(), 1)}",
            delta="Kelancaran",
        )

      st.write("---")
      st.subheader("📜 Detail Riwayat Setoran Santri")
      st.dataframe(df_filtered, use_container_width=True)
    else:
      st.info("Belum ada catatan setoran untuk santri ini.")

  # MENU 4: LAPORAN PDF
  elif menu == "📄 Cetak Laporan PDF":
    st.markdown(
        """
        <div class="main-header">
            <h1>📄 Cetak Laporan PDF Resmi</h1>
            <p>Unduh rekapitulasi nilai bulanan siap cetak atau dibagikan ke Orang Tua Santri</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if not df_data.empty:
      df_data["Tanggal_DT"] = pd.to_datetime(df_data["Tanggal"])
      df_data["Bulan_Tahun"] = df_data["Tanggal_DT"].dt.strftime("%Y-%m")

      col_p1, col_p2 = st.columns(2)
      with col_p1:
        k_pdf = st.selectbox("Pilih Kelas Laporan", list(DATABASE_SANTRI.keys()))
      with col_p2:
        b_pdf = st.selectbox(
            "Pilih Periode Bulan", df_data["Bulan_Tahun"].unique()
        )

      df_pdf = df_data[
          (df_data["Kelas"] == k_pdf) & (df_data["Bulan_Tahun"] == b_pdf)
      ]

      if not df_pdf.empty:
        st.write(f"**Pratinjau Data Laporan ({len(df_pdf)} entri):**")
        st.dataframe(df_pdf, use_container_width=True)

        pdf_bytes = generate_pdf(
            df_pdf, b_pdf, k_pdf, st.session_state["user_email"]
        )

        st.write("")
        st.download_button(
            label="📥 UNDUH LAPORAN PDF RESMI",
            data=pdf_bytes,
            file_name=f"Laporan_Tahfidz_{k_pdf}_{b_pdf}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
      else:
        st.warning("Belum ada data setoran untuk kelas dan periode ini.")
    else:
        
      st.info("Sistem belum memiliki data setoran untuk dicetak.")
