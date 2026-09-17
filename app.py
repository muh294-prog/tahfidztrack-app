import datetime
import pandas as pd
import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import streamlit as st

# 1. CONFIGURATION & STYLING (Modern Dashboard UI)
st.set_page_config(
    page_page_title="TahfidzTrack Pro - Modern Analytics",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global Styling */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Custom Card Metric */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #38BDF8;
    }
    
    /* Header Customization */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B;
        border-radius: 8px;
        color: #94A3B8;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_mode_configure=True,
)

# 2. HELPER FUNCTIONS
def hitung_nilai_tasmi(total_besar, total_kecil, nilai_dasar=100):
  minus_besar = total_besar * 2
  minus_kecil = total_kecil * 1
  total_minus = minus_besar + minus_kecil
  nilai_akhir = max(0, nilai_dasar - total_minus)
  return total_minus, nilai_akhir


# 3. MOCK DATABASE (Master Data)
DATABASE_MURID = {
    "Kelas 7A": [
        "Ahmad Fauzi - 7A01",
        "Muhammad Kenzie - 7A02",
        "Bilal Ramadhan - 7A03",
    ],
    "Kelas 7B": [
        "Siti Aisyah - 7B01",
        "Nayla Az-Zahra - 7B02",
        "Zahra Amelia - 7B03",
    ],
    "Kelas 7C": [
        "Muh. Fikhi A. - 7C01",
        "Andi Muhammad - 7C02",
        "Rizky Pratama - 7C03",
    ],
}

SURAH_JUZ_30 = [
    "An-Naba'",
    "An-Nazi'at",
    "'Abasa",
    "At-Takwir",
    "Al-Infitar",
    "Al-Mutaffifin",
    "Al-Inshiqaq",
    "Al-Buruj",
    "At-Tariq",
    "Al-A'la",
    "Al-Ghashiyah",
    "Al-Fajr",
    "Al-Balad",
    "Ash-Shams",
    "Al-Lail",
    "Ad-Duha",
    "Ash-Sharh",
    "At-Tin",
    "Al-'Alaq",
    "Al-Qadr",
    "Al-Bayyinah",
    "Az-Zalzalah",
    "Al-'Adiyat",
    "Al-Qari'ah",
    "At-Takathur",
    "Al-'Asr",
    "Al-Humazah",
    "Al-Fil",
    "Quraish",
    "Al-Ma'un",
    "Al-Kawthar",
    "Al-Kafirun",
    "An-Nasr",
    "Al-Masad",
    "Al-Ikhlas",
    "Al-Falaq",
    "An-Nas",
]

# Initialize Session State Storage
if "setoran_db" not in st.session_state:
  st.session_state["setoran_db"] = pd.DataFrame([
      {
          "Tanggal": "2026-09-10",
          "Kelas": "Kelas 7C",
          "Nama": "Muh. Fikhi A. - 7C01",
          "Surah": "Al-Ma'un",
          "Ayat": "1-7",
          "Status": "Lancar",
          "Nilai_Makhraj": 85,
          "Nilai_Tajwid": 80,
          "Nilai_Kelancaran": 75,
          "Poin": 80,
          "Ustadz": "MOH. FAIZ GUFRON, S.H.",
      },
      {
          "Tanggal": "2026-09-12",
          "Kelas": "Kelas 7C",
          "Nama": "Muh. Fikhi A. - 7C01",
          "Surah": "Al-Kafirun",
          "Ayat": "1-6",
          "Status": "Lancar",
          "Nilai_Makhraj": 90,
          "Nilai_Tajwid": 85,
          "Nilai_Kelancaran": 80,
          "Poin": 85,
          "Ustadz": "MOH. FAIZ GUFRON, S.H.",
      },
  ])

# 4. HEADER & SIDEBAR BRANDING
st.markdown(
    '<p class="main-title">📖 TahfidzTrack System</p>', unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-title">Portal Manajemen Hafalan, Analisis Kemajuan &'
    " Penilaian Tasmi' Al-Qur'an</p>",
    unsafe_allow_html=True,
)

with st.sidebar:
  st.image(
      "https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=70
  )
  st.title("TahfidzTrack v2.5")
  st.markdown("---")
  st.write("**Tahun Ajaran:** 2025/2026")
  st.write("**Semester:** II (Genap)")
  st.markdown("---")
  st.success("🟢 Database System Online")

# 5. MAIN NAVIGATION TABS
nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "✦ Presensi Setoran",
    "◈ Analytics & Rekap",
    "🪶 Tracking Portal",
    "📜 Certificate & PDF",
    "🎯 Ujian Tasmi'",
])

# --- TAB 1: PRESENSI SETORAN ---
with nav_tab1:
  st.subheader("✦ Form Input Setoran Harian")

  with st.form("form_setoran", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
      f_kelas = st.selectbox("🏛️ Pilih Kelas", list(DATABASE_MURID.keys()))
      f_nama = st.selectbox("👤 Nama Santri", DATABASE_MURID[f_kelas])
      f_tgl = st.date_input("📅 Tanggal Setoran", datetime.date.today())
    with c2:
      f_surah = st.selectbox("📖 Surah", SURAH_JUZ_30)
      f_ayat = st.text_input("🔢 Ayat (cth: 1-15)", "1-10")
      f_status = st.select_slider(
          "🚦 Status Kelancaran",
          options=["Ulangi", "Cukup", "Lancar", "Sangat Lancar"],
          value="Lancar",
      )
    with c3:
      f_makhraj = st.slider("🔊 Makhraj", 50, 100, 80)
      f_tajwid = st.slider("📜 Tajwid", 50, 100, 80)
      f_lancar = st.slider("⚡ Kelancaran", 50, 100, 80)
      f_ustadz = st.text_input("👨‍🏫 Ust / Penguji", "MOH. FAIZ GUFRON, S.H.")

    btn_submit = st.form_submit_button(
        "💾 SIMPAN DATA SETORAN", use_container_width=True
    )

    if btn_submit:
      poin_rata = int((f_makhraj + f_tajwid + f_lancar) / 3)
      new_entry = {
          "Tanggal": str(f_tgl),
          "Kelas": f_kelas,
          "Nama": f_nama,
          "Surah": f_surah,
          "Ayat": f_ayat,
          "Status": f_status,
          "Nilai_Makhraj": f_makhraj,
          "Nilai_Tajwid": f_tajwid,
          "Nilai_Kelancaran": f_lancar,
          "Poin": poin_rata,
          "Ustadz": f_ustadz,
      }
      st.session_state["setoran_db"] = pd.concat(
          [st.session_state["setoran_db"], pd.DataFrame([new_entry])],
          ignore_index=True,
      )
      st.success(
          f"Setoran **{f_nama.split(' - ')[0]}** ({f_surah}) berhasil disimpan!"
      )

# --- TAB 2: ANALYTICS & REKAP ---
with nav_tab2:
  st.subheader("◈ Analytics & Rekap Progress")
  df = st.session_state["setoran_db"]

  if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Setoran", f"{len(df)} Kali")
    m2.metric("Rata-rata Nilai", f"{int(df['Poin'].mean())} Pts")
    m3.metric(
        "Santri Aktif", f"{df['Nama'].nunique()} Orang"
    )
    m4.metric(
        "Surah Tuntas", f"{df['Surah'].nunique()} Surah"
    )

    st.write("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      fig_status = px.pie(
          df,
          names="Status",
          title="Distribusi Status Kelancaran",
          color_discrete_sequence=px.colors.sequential.RdBu,
      )
      st.plotly_chart(fig_status, use_container_width=True)
    with col_g2:
      fig_poin = px.bar(
          df,
          x="Surah",
          y="Poin",
          color="Status",
          title="Rata-Rata Nilai per Surah",
      )
      st.plotly_chart(fig_poin, use_container_width=True)

    st.markdown("**📋 Data History Setoran**")
    st.dataframe(df, use_container_width=True)
  else:
    st.info("Belum ada data setoran tersimpan.")

# --- TAB 3: TRACKING PORTAL ---
with nav_tab3:
  st.subheader("🪶 Tracking Portal Individual")
  df_track = st.session_state["setoran_db"]

  sel_kelas = st.selectbox("Pilih Kelas", list(DATABASE_MURID.keys()))
  sel_nama = st.selectbox("Pilih Nama Santri", DATABASE_MURID[sel_kelas])

  df_filtered = df_track[df_track["Nama"] == sel_nama]

  if not df_filtered.empty:
    st.write(f"### Report Progress: **{sel_nama.split(' - ')[0]}**")
    st.dataframe(df_filtered, use_container_width=True)
  else:
    st.warning("Belum ada riwayat setoran harian untuk santri ini.")

# --- TAB 4: CERTIFICATE & PDF REPORT ---
with nav_tab4:
  st.subheader("📜 Cetak Laporan PDF / Sertifikat")
  st.caption("Generate laporan resmi hasil hafalan santri")

  pdf_kelas = st.selectbox(
      "Kelas untuk PDF", list(DATABASE_MURID.keys()), key="pdf_k"
  )
  pdf_nama = st.selectbox(
      "Nama Santri untuk PDF", DATABASE_MURID[pdf_kelas], key="pdf_n"
  )

  if st.button("📄 Generate PDF Report"):
    st.success(
        f"Laporan PDF untuk **{pdf_nama.split(' - ')[0]}** siap diunduh."
    )

# --- TAB 5: UJIAN TASMI' (HASIL INTEGRASI FORMAT PENILAIAN BARU) ---
with nav_tab5:
  st.subheader("🎯 Lembar Penilaian Tasmi' Al-Qur'an (Sumatif Akhir)")
  st.caption(
      "Penilaian Ujian Tasmi' Semester: Kesalahan Besar = -2 Poin | Kesalahan"
      " Kecil = -1 Poin"
  )

  with st.form("form_ujian_tasmi"):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
      k_tasmi = st.selectbox(
          "🏛️ Kelas", list(DATABASE_MURID.keys()), key="tasmi_k"
      )
      m_tasmi = st.selectbox(
          "👤 Nama Peserta", DATABASE_MURID[k_tasmi], key="tasmi_m"
      )
    with col_t2:
      periode_tasmi = st.text_input(
          "📅 Periode Ujian", "Sumatif Akhir Semester II T.A. 2025/2026"
      )
      penguji_tasmi = st.text_input("👨‍🏫 Nama Penguji", "MOH. FAIZ GUFRON, S.H.")

    st.write("---")
    st.markdown("**📋 Input Rincian Kesalahan per Surah / Juz**")

    # Matriks Input Kesalahan Surah
    daftar_surah_tasmi = [
        "An-Nas",
        "Al-Falaq",
        "Al-Ikhlas",
        "Al-Lahab",
        "An-Nashr",
        "Al-Kafirun",
        "Al-Kautsar",
        "Al-Ma'un",
        "Al-Quraysh",
    ]

    total_err_besar = 0
    total_err_kecil = 0

    # Header Tabel
    h1, h2, h3, h4 = st.columns([2, 2, 2, 2])
    h1.write("**Nama Surah**")
    h2.write("**Kesalahan Besar (-2)**")
    h3.write("**Kesalahan Kecil (-1)**")
    h4.write("**Catatan Kritis**")

    for idx, surah_name in enumerate(daftar_surah_tasmi):
      c_s1, c_s2, c_s3, c_s4 = st.columns([2, 2, 2, 2])
      c_s1.write(f"**{idx+1}. {surah_name}**")

      # Input Kesalahan Besar (Makhraj, Mad Thabi'i, Kelancaran, Harokat)
      err_b = c_s2.number_input(
          "Besar", min_value=0, step=1, key=f"kb_{idx}", label_visibility="collapsed"
      )
      # Input Kesalahan Kecil (Mad Far'i, Sifat, Tajwid)
      err_k = c_s3.number_input(
          "Kecil", min_value=0, step=1, key=f"kk_{idx}", label_visibility="collapsed"
      )

      c_s4.text_input(
          "Ket",
          placeholder="cth: Kelancaran",
          key=f"note_{idx}",
          label_visibility="collapsed",
      )

      total_err_besar += err_b
      total_err_kecil += err_k

    st.write("---")
    catatan_umum = st.text_area(
        "📝 CATATAN PENGUJI",
        placeholder="Masukkan catatan evaluasi umum santri...",
    )

    # Calculation logic
    total_minus, nilai_akhir = hitung_nilai_tasmi(
        total_err_besar, total_err_kecil
    )

    # Real-time Metric Display
    res1, res2, res3 = st.columns(3)
    res1.metric("Total Kesalahan Besar (-2)", f"{total_err_besar} kali")
    res2.metric("Total Kesalahan Kecil (-1)", f"{total_err_kecil} kali")
    res3.metric(
        "NILAI AKHIR TASMI'",
        f"{nilai_akhir} / 100",
        delta=f"-{total_minus} Poin",
        delta_color="inverse",
    )

    btn_simpan_tasmi = st.form_submit_button(
        "💾 SIMPAN REKAP NILAI TASMI'", use_container_width=True
    )

    if btn_simpan_tasmi:
      st.success(
          f"Data Nilai Tasmi' **{m_tasmi.split(' - ')[0]}** Berhasil Disimpan"
          f" dengan Nilai Akhir: **{nilai_akhir}**!"
      )
