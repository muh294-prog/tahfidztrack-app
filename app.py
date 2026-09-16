import base64
import datetime
import io
import os
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Nama File Gambar Logo
IMAGE_FILENAME = "WhatsApp Image 2026-09-12 at 10.04.17 AM.jpeg"


# Function Konversi Gambar ke Base64 (Untuk Web)
def get_image_base64(image_path):
  if os.path.exists(image_path):
    with open(image_path, "rb") as img_file:
      return base64.b64encode(img_file.read()).decode("utf-8")
  return ""


img_base64 = get_image_base64(IMAGE_FILENAME)
img_src = (
    f"data:image/jpeg;base64,{img_base64}" if img_base64 else IMAGE_FILENAME
)

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="TahfidzTrack — SMPIT Ibnul Qayyim",
    page_icon=IMAGE_FILENAME if os.path.exists(IMAGE_FILENAME) else "🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS Custom Styling (REVISI #20: Modern Styling & Iconography Support)
st.markdown(
    """
<style>
    /* SVG Ornamen Daun & Bunga Hijau di Pojok Kiri Atas */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 250px;
        height: 250px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath fill='%20%2310B981' opacity='0.25' d='M0,0 Q30,10 50,40 Q20,50 0,0 Z'/%3E%3Cpath fill='%20%23059669' opacity='0.3' d='M0,0 Q10,40 40,60 Q50,20 0,0 Z'/%3E%3Cpath fill='%20%2334D399' opacity='0.2' d='M10,0 Q40,20 60,10 Q30,40 10,0 Z'/%3E%3Ccircle cx='35' cy='35' r='4' fill='%20%236EE7B7' opacity='0.4'/%3E%3Ccircle cx='48' cy='22' r='3' fill='%20%23A7F3D0' opacity='0.5'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        z-index: 1000;
        pointer-events: none;
    }

    /* SVG Ornamen Daun & Bunga Hijau di Pojok Kanan Atas */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0;
        right: 0;
        width: 250px;
        height: 250px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath fill='%20%2310B981' opacity='0.25' d='M100,0 Q70,10 50,40 Q80,50 100,0 Z'/%3E%3Cpath fill='%20%23059669' opacity='0.3' d='M100,0 Q90,40 60,60 Q50,20 100,0 Z'/%3E%3Cpath fill='%20%2334D399' opacity='0.2' d='M90,0 Q60,20 40,10 Q70,40 90,0 Z'/%3E%3Ccircle cx='65' cy='35' r='4' fill='%20%236EE7B7' opacity='0.4'/%3E%3Ccircle cx='52' cy='22' r='3' fill='%20%23A7F3D0' opacity='0.5'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        z-index: 1000;
        pointer-events: none;
    }

    /* Styling Background Utama */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), 
                    url("WhatsApp Image 2026-09-12 at 10.04.17 AM.jpeg") no-repeat center center fixed;
        background-size: cover;
        color: #F8FAFC;
    }

    /* Warna Label Form Agar Terbaca Sangat Jelas */
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
    }

    /* Warna Teks Menu Tab Navigasi Utama */
    button[data-baseweb="tab"] p {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px;
    }

    /* Tab Aktif Highlight Hijau Emerald */
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #34D399 !important;
        font-weight: 800 !important;
    }
    
    /* Header Container Botanical Gradient */
    .main-header {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.95) 0%, rgba(16, 185, 129, 0.9) 100%);
        padding: 24px;
        border-radius: 20px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.35);
        text-align: center;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    
    .main-header h1 {
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 10px 0 0 0 !important;
        color: #FFFFFF !important;
        letter-spacing: 0.8px;
    }
    
    .main-header p {
        font-size: 13.5px;
        margin-top: 4px;
        opacity: 0.95;
        letter-spacing: 0.4px;
    }

    /* Metric/Card Box */
    .card-box {
        background-color: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(6px);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #10B981;
    }
    
    .metric-label {
        font-size: 12.5px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    /* Primary Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 22px !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.5) !important;
    }

    /* Custom Badges */
    .badge-success {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
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

# Database Murid Per Kelas
DATABASE_MURID = {
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
            "Nama Murid",
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
  df = pd.read_csv(DATA_FILE)
  if "Nama Santri" in df.columns:
    df.rename(columns={"Nama Santri": "Nama Murid"}, inplace=True)
  return df


def save_data(df):
  df.to_csv(DATA_FILE, index=False)


# --- GENERATE PDF ---
def generate_pdf(df_filtered, bulan_tahun, nama_kelas):
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
      spaceAfter=4,
  )

  subtitle_style = ParagraphStyle(
      "SubTitleStyle",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=10,
      textColor=colors.HexColor("#0F172A"),
      alignment=1,
      spaceAfter=15,
  )

  if os.path.exists(IMAGE_FILENAME):
    img = RLImage(IMAGE_FILENAME, width=60, height=60)
    img.hAlign = "CENTER"
    elements.append(img)
    elements.append(Spacer(1, 8))

  elements.append(
      Paragraph(
          "LAPORAN REKAPITULASI BULANAN TAHFIDZ QURAN", title_style
      )
  )
  elements.append(
      Paragraph(
          f"SMPIT IBNUL QAYYIM MAKASSAR — {nama_kelas} | Periode: {bulan_tahun}",
          subtitle_style,
      )
  )

  table_data = [
      ["No", "Tanggal", "Nama Murid", "Jenis", "Surah (Ayat)", "Hlm", "Nilai"]
  ]
  for idx, row in df_filtered.reset_index(drop=True).iterrows():
    table_data.append([
        str(idx + 1),
        str(row["Tanggal"]),
        str(row["Nama Murid"]).split(" - ")[0][:18],
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

  if "VIIIA" in nama_kelas:
    guru_pengampu = "Ustadz Muh. Faiz Gufran, S.H."
  else:
    guru_pengampu = "Ustadz Achmad Adnan P.H."

  ttd_text = (
      f"Makassar, {datetime.date.today().strftime('%d %B %Y')}\n"
      f"Guru Pengampu Tahfidz,\n\n\n\n({guru_pengampu})"
  )
  ttd_table = Table([["", ttd_text]], colWidths=[280, 220])
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


# Render Header Utama
def render_header(title, subtitle):
  st.markdown(
      f"""
      <div class="main-header">
          <img src="{img_src}" width="75" style="border-radius: 50%; background: white; padding: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
          <h1>{title}</h1>
          <p>{subtitle}</p>
      </div>
  """,
      unsafe_allow_html=True,
  )


# Modal Edit Dialog
@st.dialog("🛠️ Modifikasi Record Setoran")
def modal_edit_setoran(orig_idx, row_data):
  st.write(f"**Update Entri Tanggal {row_data['Tanggal']}**")
  with st.form(key=f"modal_form_{orig_idx}"):
    e_jenis = st.selectbox(
        "Kategori Setoran",
        ["Sabaq", "Murajaah", "Manzil"],
        index=["Sabaq", "Murajaah", "Manzil"].index(row_data["Jenis Setoran"]),
    )
    e_surah = st.text_input("Nama Surah Al-Qur'an", value=row_data["Surah"])

    c_a, c_b = st.columns(2)
    with c_a:
      e_a_awal = st.number_input(
          "Ayat Awal", min_value=1, value=int(row_data["Ayat Awal"])
      )
      e_hlm = st.number_input(
          "Volume (Halaman)",
          min_value=0.1,
          value=float(row_data["Halaman"]),
          step=0.5,
      )
    with c_b:
      e_a_akhir = st.number_input(
          "Ayat Akhir", min_value=1, value=int(row_data["Ayat Akhir"])
      )
      e_salah = st.number_input(
          "Catatan Kekurangan", min_value=0, value=int(row_data["Salah"])
      )

    btn_simpan = st.form_submit_button("🛡️ SIMPAN REVISI DATA")

    if btn_simpan:
      df_temp = load_data()
      calc_nilai = max(0.0, min(100.0, round(100.0 - (e_salah * 2.0), 2)))

      df_temp.loc[orig_idx, "Jenis Setoran"] = e_jenis
      df_temp.loc[orig_idx, "Surah"] = e_surah
      df_temp.loc[orig_idx, "Ayat Awal"] = e_a_awal
      df_temp.loc[orig_idx, "Ayat Akhir"] = e_a_akhir
      df_temp.loc[orig_idx, "Halaman"] = e_hlm
      df_temp.loc[orig_idx, "Salah"] = e_salah
      df_temp.loc[orig_idx, "Nilai"] = calc_nilai

      save_data(df_temp)
      st.success("Perubahan record berhasil diperbarui!")
      st.rerun()


# Session State Login
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["user_email"] = ""

# ==========================================
# 1. TAMPILAN HALAMAN LOGIN
# ==========================================
if not st.session_state["logged_in"]:
  render_header(
      "TahfidzTrack — SMPIT Ibnul Qayyim",
      "Sistem Management & Monitoring Hafalan Qur'an Murid",
  )

  col_left, col_center, col_right = st.columns([1, 2, 1])
  with col_center:
    with st.form("login_form"):
      st.subheader("🔑 Autentikasi Pengampu")
      email = st.text_input(
          "Alamat Email Akademik",
          placeholder="contoh: mohfaizgufran@iqis.sch.id",
      )
      password = st.text_input(
          "Sandi Keamanan", type="password", placeholder="••••••••"
      )
      submit = st.form_submit_button("Akses Portal ➔")

      if submit:
        email_clean = email.strip().lower()
        pass_clean = password.strip()
        if (
            email_clean in CREDENTIALS
            and CREDENTIALS[email_clean] == pass_clean
        ):
          st.session_state["logged_in"] = True
          st.session_state["user_email"] = email_clean
          st.success("Otentikasi berhasil! Mengarahkan ke sistem...")
          st.rerun()
        else:
          st.error("Kredensial tidak terverifikasi.")

# ==========================================
# 2. TAMPILAN APLIKASI UTAMA
# ==========================================
else:
  render_header(
      "TahfidzTrack — SMPIT Ibnul Qayyim",
      "Sistem Management & Monitoring Hafalan Qur'an Murid",
  )

  c_user, c_logout = st.columns([4, 1])
  with c_user:
    st.markdown(
        f"🏛️ **Pembimbing Aktif:** <span"
        f" class='badge-success'>{st.session_state['user_email']}</span>",
        unsafe_allow_html=True,
    )
  with c_logout:
    if st.button("🚪 Log Out"):
      st.session_state["logged_in"] = False
      st.rerun()

  st.write("")

  df_data = load_data()

  # NAVIGASI UTAMA (REVISI #20: Icon Kreatif & Elegan)
  nav_tab1, nav_tab2, nav_tab3, nav_tab4 = st.tabs([
      "✦ Presensi Setoran",
      "◈ Analytics & Rekap",
      "🪶 Tracking Portal",
      "📜 Certificate & PDF",
  ])

  # TAB 1: INPUT SETORAN
  with nav_tab1:
    st.subheader("✨ Form Input Setoran Harian")
    st.caption("Pencatatan progres hafalan harian murid secara real-time")

    with st.container():
      c1, c2 = st.columns(2)
      with c1:
        kelas_sel = st.selectbox("🏛️ Rombongan Belajar", list(DATABASE_MURID.keys()))
        murid_sel = st.selectbox("👤 Profil Murid", DATABASE_MURID[kelas_sel])
        jenis_sel = st.selectbox(
            "📌 Kategori Setoran", ["Sabaq", "Murajaah", "Manzil"]
        )
        surah_sel = st.text_input("🪷 Nama Surah Al-Qur'an", "Al-Baqarah")

      with c2:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
          ayat_awal = st.number_input("🧮 Ayat Awal", min_value=1, value=1)
        with col_a2:
          ayat_akhir = st.number_input("🧮 Ayat Akhir", min_value=1, value=10)

        halaman = st.number_input(
            "📄 Volume (Halaman)", min_value=0.1, value=1.0, step=0.5
        )
        salah = st.number_input(
            "⚡ Catatan Kekurangan/Bantuan", min_value=0, value=0
        )

    nilai_calc = max(0.0, min(100.0, round(100.0 - (salah * 2.0), 2)))

    st.write("")
    m1, m2 = st.columns(2)
    with m1:
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Indeks Kelancaran Hafalan</div>
              <div class="metric-value">{nilai_calc} <span style="font-size:18px; color:#94A3B8;">/ 100</span></div>
          </div>
      """,
          unsafe_allow_html=True,
      )
    with m2:
      if nilai_calc >= 90:
        kualitas = "Mumtaz (Sangat Baik)"
      elif nilai_calc >= 75:
        kualitas = "Jayyid Jiddan (Baik)"
      elif nilai_calc >= 60:
        kualitas = "Jayyid (Cukup)"
      else:
        kualitas = "Rasib (Perlu Murajaah)"

      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Predikat Evaluasi</div>
              <div class="metric-value" style="font-size: 22px; color: #34D399; padding-top:8px;">{kualitas}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )

    if st.button("🛡️ SIMPAN RECORD SETORAN", use_container_width=True):
      new_record = {
          "Tanggal": datetime.date.today().strftime("%Y-%m-%d"),
          "Guru Input": st.session_state["user_email"],
          "Kelas": kelas_sel,
          "Nama Murid": murid_sel,
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

      st.snow()
      st.toast(
          f"✨ Barakallahu Fiik! Data setoran {murid_sel.split(' - ')[0]} telah"
          " tersimpan.",
          icon="🕌",
      )
      st.success(
          f"Alhamdulillah! Data setoran {murid_sel.split(' - ')[0]} berhasil"
          " dicatat ke dalam database."
      )

  # TAB 2: REKAPAN & STATISTIK
  with nav_tab2:
    st.subheader("◈ Ringkasan Metrik & Statistik Tahfidz")
    st.caption("Overview capaian kolektif seluruh santri dan riwayat transaksi")

    k1, k2, k3 = st.columns(3)
    with k1:
      st.markdown(
          f"""
          <div class="card-box">
              <div class="metric-label">Aktivitas Setoran Terdata</div>
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
              <div class="metric-label">Akumulasi Halaman Tersetor</div>
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
              <div class="metric-label">Rata-Rata Performa Santri</div>
              <div class="metric-value">{avg_score}</div>
          </div>
      """,
          unsafe_allow_html=True,
      )

    st.subheader("📑 Matriks Riwayat Setoran")
    st.dataframe(df_data, use_container_width=True)

  # TAB 3: DASHBOARD MURID
  with nav_tab3:
    st.subheader("🪶 Monitoring Progres Santri")
    st.caption("Evaluasi individual serta penyesuaian riwayat hafalan")

    c_k, c_s = st.columns(2)
    with c_k:
      k_sel = st.selectbox("Pilih Kelas", list(DATABASE_MURID.keys()))
    with c_s:
      s_sel = st.selectbox("Pilih Nama Murid", DATABASE_MURID[k_sel])

    df_filtered = df_data[df_data["Nama Murid"] == s_sel].copy()

    if not df_filtered.empty:
      p1, p2, p3 = st.columns(3)
      with p1:
        st.metric(
            "Frekuensi Setoran", f"{len(df_filtered)} Sesi", delta="Keaktifan"
        )
      with p2:
        st.metric(
            "Progres Akumulasi",
            f"{df_filtered['Halaman'].sum()} Hlm",
            delta="Capaian",
        )
      with p3:
        st.metric(
            "Indeks Kelancaran",
            f"{round(df_filtered['Nilai'].mean(), 1)}",
            delta="Performa",
        )

      st.write("---")
      st.subheader("📜 Log Setoran Santri")

      for orig_idx, row in df_filtered.iterrows():
        col_tgl, col_jenis, col_detail, col_nilai, col_btn_edit, col_btn_del = (
            st.columns([1.5, 1.5, 3, 1, 0.8, 0.8])
        )

        with col_tgl:
          st.write(f"🗓️ **{row['Tanggal']}**")
        with col_jenis:
          st.write(f"🏷️ **{row['Jenis Setoran']}**")
        with col_detail:
          st.write(
              f"🪷 Surah **{row['Surah']}** ({row['Ayat Awal']}-{row['Ayat Akhir']})"
              f" — {row['Halaman']} Hlm"
          )
        with col_nilai:
          st.write(f"💎 **{row['Nilai']}**")

        with col_btn_edit:
          if st.button("🛠️", key=f"edit_btn_{orig_idx}"):
            modal_edit_setoran(orig_idx, row)

        with col_btn_del:
          if st.button("🗑️", key=f"del_btn_{orig_idx}"):
            df_data = df_data.drop(orig_idx).reset_index(drop=True)
            save_data(df_data)
            st.success("Setoran berhasil dihapus!")
            st.rerun()

        st.markdown(
            "<hr style='margin: 4px 0 12px 0; border-color: #334155;'>",
            unsafe_allow_html=True,
        )

    else:
      st.info("Belum ada data rekaman setoran untuk santri ini.")

  # TAB 4: LAPORAN PDF
  with nav_tab4:
    st.subheader("📜 Penerbitan Laporan PDF Resmi")
    st.caption("Cetak dokumen rekapitulasi bulanan berformat resmi per kelas")

    if not df_data.empty:
      df_data["Tanggal_DT"] = pd.to_datetime(df_data["Tanggal"])
      df_data["Bulan_Tahun"] = df_data["Tanggal_DT"].dt.strftime("%Y-%m")

      tab_8a, tab_8c = st.tabs(["🏛️ KELAS VIIIA", "🏛️ KELAS VIIIC"])

      with tab_8a:
        st.write("### Dokumen Resmi — KELAS VIIIA")
        st.caption("Pengampu Akademik: **Ustadz Muh. Faiz Gufran, S.H.**")
        df_8a = df_data[df_data["Kelas"] == "KELAS VIIIA"]

        if not df_8a.empty:
          b_pdf_8a = st.selectbox(
              "Periode Laporan (Kelas VIIIA)",
              df_8a["Bulan_Tahun"].unique(),
              key="pdf_8a",
          )
          df_pdf_8a = df_8a[df_8a["Bulan_Tahun"] == b_pdf_8a]

          st.write(f"**Pratinjau Data KELAS VIIIA ({len(df_pdf_8a)} entri):**")
          st.dataframe(df_pdf_8a, use_container_width=True)

          pdf_bytes_8a = generate_pdf(df_pdf_8a, b_pdf_8a, "KELAS VIIIA")

          st.write("")
          st.download_button(
              label="📥 UNDUH LAPORAN PDF (KELAS VIIIA)",
              data=pdf_bytes_8a,
              file_name=f"Laporan_Tahfidz_KELAS_VIIIA_{b_pdf_8a}.pdf",
              mime="application/pdf",
              use_container_width=True,
          )
        else:
          st.warning("Belum ada data setoran untuk KELAS VIIIA.")

      with tab_8c:
        st.write("### Dokumen Resmi — KELAS VIIIC")
        st.caption("Pengampu Akademik: **Ustadz Achmad Adnan P.H.**")
        df_8c = df_data[df_data["Kelas"] == "KELAS VIIIC"]

        if not df_8c.empty:
          b_pdf_8c = st.selectbox(
              "Periode Laporan (Kelas VIIIC)",
              df_8c["Bulan_Tahun"].unique(),
              key="pdf_8c",
          )
          df_pdf_8c = df_8c[df_8c["Bulan_Tahun"] == b_pdf_8c]

          st.write(f"**Pratinjau Data KELAS VIIIC ({len(df_pdf_8c)} entri):**")
          st.dataframe(df_pdf_8c, use_container_width=True)

          pdf_bytes_8c = generate_pdf(df_pdf_8c, b_pdf_8c, "KELAS VIIIC")

          st.write("")
          st.download_button(
              label="📥 UNDUH LAPORAN PDF (KELAS VIIIC)",
              data=pdf_bytes_8c,
              file_name=f"Laporan_Tahfidz_KELAS_VIIIC_{b_pdf_8c}.pdf",
              mime="application/pdf",
              use_container_width=True,
          )
        else:
          st.warning("Belum ada data setoran untuk KELAS VIIIC.")
    else:
      st.info("Sistem belum memiliki data setoran untuk dicetak.")
