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

# Nama File Gambar
LOGO_FILENAME = "WhatsApp Image 2026-09-12 at 10.04.17 AM.jpeg"
HEADER_BG_FILENAME = "WhatsApp Image 2026-09-16 at 1.57.59 PM.jpeg"


def get_image_base64(image_path):
  if os.path.exists(image_path):
    with open(image_path, "rb") as img_file:
      return base64.b64encode(img_file.read()).decode("utf-8")
  return ""


img_logo_base64 = get_image_base64(LOGO_FILENAME)
img_logo_src = (
    f"data:image/jpeg;base64,{img_logo_base64}"
    if img_logo_base64
    else LOGO_FILENAME
)

header_bg_base64 = get_image_base64(HEADER_BG_FILENAME)
header_bg_src = (
    f"data:image/jpeg;base64,{header_bg_base64}"
    if header_bg_base64
    else HEADER_BG_FILENAME
)

st.set_page_config(
    page_title="TahfidzTrack — SMPIT Ibnul Qayyim",
    page_icon=LOGO_FILENAME if os.path.exists(LOGO_FILENAME) else "🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
<style>
    .stApp::before {{
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
    }}
    .stApp::after {{
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
    }}
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), 
                    url("{img_logo_src}") no-repeat center center fixed;
        background-size: cover;
        color: #F8FAFC;
    }}
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {{
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
    }}
    button[data-baseweb="tab"] p {{
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px;
    }}
    button[data-baseweb="tab"][aria-selected="true"] p {{
        color: #34D399 !important;
        font-weight: 800 !important;
    }}
    .main-header {{
        background: linear-gradient(rgba(5, 150, 105, 0.75), rgba(16, 185, 129, 0.85)),
                    url("{header_bg_src}") no-repeat center center;
        background-size: cover;
        padding: 35px 20px;
        border-radius: 20px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.35);
        text-align: center;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(52, 211, 153, 0.4);
    }}
    .main-header h1 {{
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 12px 0 0 0 !important;
        color: #FFFFFF !important;
        letter-spacing: 0.8px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }}
    .main-header p {{
        font-size: 14px;
        margin-top: 6px;
        opacity: 0.95;
        letter-spacing: 0.4px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }}
    .card-box {{
        background-color: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(6px);
    }}
    .metric-value {{
        font-size: 32px;
        font-weight: 800;
        color: #10B981;
    }}
    .metric-label {{
        font-size: 12.5px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        letter-spacing: 0.5px;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.5) !important;
    }}
    .badge-success {{
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
    }}
</style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "tahfidz_track_data.csv"

CREDENTIALS = {
    "mohfaizgufran@iqis.sch.id": "Tahfizsmp8!",
    "adnanputra@iqis.sch.id": "Tahfizsmp8!",
    "rafly@iqis.sch.id": "Tahfizsmp8!",
    "bagusammar@iqis.sch.id": "Tahfizsmp8!",
    "huzaifah@iqis.sch.id": "Tahfizsmp8!",
}

DATABASE_MURID = {
    "KELAS VII A": [
        "Adelard Muhammad Athar - 2610380000",
        "Adzkhan Zidan Alkhalifi - 73710905",
        "Al Ghazali Hidayat - 144498445",
        "Anhar Al Ghazali - 2610383000",
        "Aufar Abdillah Pratama - 3147254000",
        "Azzam Zahran Hasyim - 138357008",
        "Fadrian Ananta Rizkullah - 3132885678",
        "Fathan Azka Erlangga - 3141007874",
        "Muh Abidzar Ramadhan - 3140775000",
        "Muh Afif Ismail - 2610389000",
        "Muh Fadlan Khalifah Aqil Haeruddin - 2610390000",
        "Muh. Arrahfi Abimayudhitya - 3139924000",
        "Muh. Ayyash Triansyah - 3144640000",
        "Muhammad Abdurahman Putra Subara - 3144238000",
        "Muhammad Afdhal Al Ghiffari Rahmat - 2012070000",
        "Muhammad Athallah Azka - 2610396000",
        "Muhammad Bilal Qushay - 3137064000",
        "Muhammad Farid Atallah - 2610397000",
        "Muhammad Fauzan Akbar - 145953134",
        "Muhammad Raihan Ar Razin - 146047347",
        "Naufal Afkar Narja - 3148227000",
    ],
    "KELAS VII C": [
        "Abdillah Yusuf Putra Asri - 1032000237",
        "Adelard Rabbani - 149243685",
        "Adhyastha Fauzan Putra Andrianto - 3138085000",
        "Adskhan Fahmi Fawwaz - 3157157000",
        "Ahmad Rakan Fariz Rani - 3147420000",
        "Alfatih Muhammad Khawarizmi - 3144939656",
        "Ammar - 3122477000",
        "Andi Adeeb Abrar Agussalim - 3131498000",
        "Daffa Isya Al Dhabith - 737111000000",
        "Dzahaby Khalish Akram - 144102228",
        "Ghali Shahijun Khalq - 2610429000",
        "Haziq Afif Daiyan - 2000249730",
        "Muh Aflah Dzakirin Nasrullah - 3136476000",
        "Muh Ilham Isyak - 145305229",
        "Muhammad Akhdan Alfarizqi - 143626367",
        "Muhammad Imran Tsaqieb Rahmat - 2012070002",
        "Muhammad Raziq Hanania - 73711123",
        "Rafli Azzam Syahril - 2610436000",
        "Uwais Kaisan - 3132325000",
        "Zayyan Syafiq Shan - 133200784",
    ],
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
    "KELAS IX A": [
        "Abdullah Azzam Asfar - 3123481089",
        "Ariq Merdeka Ramadhan - 3115732852",
        "Bintang Anugrah - 0116080905",
        "Fahreza Hanif Wijaya - 2410238",
        "Ibrahim - 2410239",
        "Muh. Aisyar Isbal - 2410240",
        "Muh. Darul Tri Akbar - 2410241",
        "Muh. Rakha Rizqullah - 2410243",
        "Muh. Zaki Zulhilmi - 2410244",
        "Muhammad Alif Afreiza Herwan - 2410245",
        "Muhammad Arsya Al Husain - 2410246",
        "Muhammad Cakra Pratama Ompo Massa - 2410247",
        "Muhammad Furqan - 2410248",
        "Muhammad Ghazian Asfa - 2410249",
        "Muhammad Maulana Ishak - 2410250",
        "Muhammad Nizarrazzaq Marwan - 2410251",
        "Rahmat Faizi - 2410252",
        "Wahyu Triyantono. S - 2410253",
        "Dzakwan Fauzan Kalesaran - 2410287",
        "Azka Faried Athallah Sulkifli - 002610458",
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

  if os.path.exists(LOGO_FILENAME):
    img = RLImage(LOGO_FILENAME, width=60, height=60)
    img.hAlign = "CENTER"
    elements.append(img)
    elements.append(Spacer(1, 8))

  elements.append(
      Paragraph("LAPORAN REKAPITULASI BULANAN TAHFIDZ QURAN", title_style)
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

  if "VII A" in nama_kelas:
    koordinator = "Ustadz Rijal, S.Pd.I"
  elif "IX A" in nama_kelas or "IXA" in nama_kelas:
    koordinator = "Ustadz Hudzaifah"
  elif "VIIIA" in nama_kelas or "VIII A" in nama_kelas:
    koordinator = "Ustadz Muh. Faiz Gufran, S.H."
  else:
    koordinator = "Ustadz Achmad Adnan P.H."

  ttd_text = (
      f"Makassar, {datetime.date.today().strftime('%d %B %Y')}\n"
      f"Koordinator Halaqah Tahfidz Kelas,\n\n\n\n({koordinator})"
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


def render_header(title, subtitle):
  st.markdown(
      f"""
      <div class="main-header">
          <img src="{img_logo_src}" width="75" style="border-radius: 50%; background: white; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
          <h1>{title}</h1>
          <p>{subtitle}</p>
      </div>
  """,
      unsafe_allow_html=True,
  )


@st.dialog("🛠️ Modifikasi Record Setoran")
def modal_edit_setoran(orig_idx, row_data):
  st.write(
      f"**Update Entri Santri: {str(row_data['Nama Murid']).split(' - ')[0]}**"
  )
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


def render_interactive_table(
    df_subset, prefix_key="tb", show_student_col=True
):
  if df_subset.empty:
    st.info("Tidak ada record data setoran.")
    return

  cols_weight = (
      [1.2, 2.2, 1.2, 2.2, 1.2, 0.8, 0.8]
      if show_student_col
      else [1.2, 1.5, 2.5, 1.2, 0.8, 0.8]
  )

  for idx, row in df_subset.iterrows():
    c_list = st.columns(cols_weight)
    c_i = 0

    with c_list[c_i]:
      st.write(f"🗓️ **{row['Tanggal']}**")
    c_i += 1

    if show_student_col:
      with c_list[c_i]:
        st.write(f"👤 **{str(row['Nama Murid']).split(' - ')[0]}**")
      c_i += 1

    with c_list[c_i]:
      st.write(f"🏷️ {row['Jenis Setoran']}")
    c_i += 1

    with c_list[c_i]:
      st.write(
          f"🪷 **{row['Surah']}** ({row['Ayat Awal']}-{row['Ayat Akhir']}) —"
          f" {row['Halaman']} Hlm"
      )
    c_i += 1

    with c_list[c_i]:
      st.write(f"💎 **{row['Nilai']}**")
    c_i += 1

    with c_list[c_i]:
      if st.button("🛠️ Edit", key=f"{prefix_key}_edit_{idx}"):
        modal_edit_setoran(idx, row)
    c_i += 1

    with c_list[c_i]:
      if st.button("🗑️ Hapus", key=f"{prefix_key}_del_{idx}"):
        df_all = load_data()
        df_all = df_all.drop(idx).reset_index(drop=True)
        save_data(df_all)
        st.toast("Record setoran telah dihapus", icon="🗑️")
        st.rerun()

    st.markdown(
        "<hr style='margin: 4px 0 10px 0; border-color: rgba(255,255,255,0.1);'>",
        unsafe_allow_html=True,
    )


# Helper Tasmi Calculation
def hitung_nilai_tasmi(total_besar, total_kecil, nilai_dasar=100):
  minus_besar = total_besar * 2
  minus_kecil = total_kecil * 1
  total_minus = minus_besar + minus_kecil
  nilai_akhir = max(0, nilai_dasar - total_minus)
  return total_minus, nilai_akhir


# Session State Login
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
  st.session_state["user_email"] = ""

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

  # NAVIGASI UTAMA DENGAN TAB UJIAN TASMI'
  nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
      "✦ Presensi Setoran",
      "◈ Analytics & Rekap",
      "🪶 Tracking Portal",
      "📜 Certificate & PDF",
      "🎯 Ujian Tasmi'",
  ])

  # TAB 1: INPUT SETORAN
  with nav_tab1:
    st.subheader("✨ Form Input Setoran Harian")
    st.caption("Pencatatan progres hafalan harian murid secara real-time")

    with st.container():
      c1, c2 = st.columns(2)
      with c1:
        kelas_sel = st.selectbox(
            "🏛️ Rombongan Belajar", list(DATABASE_MURID.keys())
        )
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

    st.subheader("📑 Matriks Riwayat Setoran Keseluruhan")
    render_interactive_table(
        df_data, prefix_key="analytics_tb", show_student_col=True
    )

  # TAB 3: DASHBOARD MURID
  with nav_tab3:
    st.subheader("🪶 Monitoring Progres Santri")
    st.caption("Evaluasi individual serta penyesuaian riwayat hafalan")

    c_k, c_s = st.columns(2)
    with c_k:
      k_sel = st.selectbox(
          "Pilih Kelas", list(DATABASE_MURID.keys()), key="dash_kelas"
      )
    with c_s:
      s_sel = st.selectbox(
          "Pilih Nama Murid", DATABASE_MURID[k_sel], key="dash_murid"
      )

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
      render_interactive_table(
          df_filtered, prefix_key="student_tb", show_student_col=False
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

      tab_list = st.tabs(list(DATABASE_MURID.keys()))

      for idx_tab, nama_k in enumerate(DATABASE_MURID.keys()):
        with tab_list[idx_tab]:
          st.write(f"### Dokumen Resmi — {nama_k}")
          df_k = df_data[df_data["Kelas"] == nama_k]

          if not df_k.empty:
            b_pdf_k = st.selectbox(
                f"Periode Laporan ({nama_k})",
                df_k["Bulan_Tahun"].unique(),
                key=f"pdf_select_{nama_k}",
            )
            df_pdf_k = df_k[df_k["Bulan_Tahun"] == b_pdf_k]

            st.write(f"**Pratinjau Data {nama_k} ({len(df_pdf_k)} entri):**")
            render_interactive_table(
                df_pdf_k, prefix_key=f"pdf_{nama_k}_tb", show_student_col=True
            )

            pdf_bytes_k = generate_pdf(df_pdf_k, b_pdf_k, nama_k)

            st.write("")
            st.download_button(
                label=f"📥 UNDUH LAPORAN PDF ({nama_k})",
                data=pdf_bytes_k,
                file_name=(
                    f"Laporan_Tahfidz_{nama_k.replace(' ', '_')}_{b_pdf_k}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
                key=f"btn_dl_{nama_k}",
            )
          else:
            st.warning(f"Belum ada data setoran untuk {nama_k}.")
    else:
      st.info("Sistem belum memiliki data setoran untuk dicetak.")

  # TAB 5: UJIAN TASMI'
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
        penguji_tasmi = st.text_input(
            "👨‍🏫 Nama Penguji", "MOH. FAIZ GUFRON, S.H."
        )

      st.write("---")
      st.markdown("**📋 Input Rincian Kesalahan per Surah / Juz**")

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

      h1, h2, h3, h4 = st.columns([2, 2, 2, 2])
      h1.write("**Nama Surah**")
      h2.write("**Kesalahan Besar (-2)**")
      h3.write("**Kesalahan Kecil (-1)**")
      h4.write("**Catatan Kritis**")

      for idx, surah_name in enumerate(daftar_surah_tasmi):
        c_s1, c_s2, c_s3, c_s4 = st.columns([2, 2, 2, 2])
        c_s1.write(f"**{idx+1}. {surah_name}**")

        err_b = c_s2.number_input(
            "Besar",
            min_value=0,
            step=1,
            key=f"kb_{idx}",
            label_visibility="collapsed",
        )
        err_k = c_s3.number_input(
            "Kecil",
            min_value=0,
            step=1,
            key=f"kk_{idx}",
            label_visibility="collapsed",
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

      total_minus, nilai_akhir = hitung_nilai_tasmi(
          total_err_besar, total_err_kecil
      )

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
