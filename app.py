import base64
import datetime
import io
import json
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

# Configuration & Constants
LOGO_FILENAME = "WhatsApp Image 2026-09-12 at 10.04.17 AM.jpeg"
HEADER_BG_FILENAME = "WhatsApp Image 2026-09-16 at 1.57.59 PM.jpeg"
DATA_FILE = "tahfidz_track_data.csv"
TASMI_DATA_FILE = "tahfidz_tasmi_data.csv"
SESSIONS_FILE = "active_sessions.json"
KEPALA_SEKOLAH = "Arief Rahman Syarif, S.Kom., Gr., S.Pd."

ADMIN_PANEL_PASSKEY = "11333356"

ADMIN_ACCOUNTS = [
    "adnanputra@iqis.sch.id",
    "muh294@admin.smp.belajar.id",
]

# DATA BASE 114 SURAH DAN JUMLAH AYAT MASING-MASING
DATA_SURAH_AYAT = {
    "1. Al-Fatihah": 7, "2. Al-Baqarah": 286, "3. Ali 'Imran": 200, "4. An-Nisa'": 176, "5. Al-Ma'idah": 120,
    "6. Al-An'am": 165, "7. Al-A'raf": 206, "8. Al-Anfal": 75, "9. At-Taubah": 129, "10. Yunus": 109,
    "11. Hud": 123, "12. Yusuf": 111, "13. Ar-Ra'd": 43, "14. Ibrahim": 52, "15. Al-Hijr": 99,
    "16. An-Nahl": 128, "17. Al-Isra'": 111, "18. Al-Kahf": 110, "19. Maryam": 98, "20. Taha": 135,
    "21. Al-Anbiya'": 112, "22. Al-Hajj": 78, "23. Al-Mu'minun": 118, "24. An-Nur": 64, "25. Al-Furqan": 77,
    "26. Asy-Syu'ara'": 227, "27. An-Naml": 93, "28. Al-Qasas": 88, "29. Al-'Ankabut": 69, "30. Ar-Rum": 60,
    "31. Luqman": 34, "32. As-Sajdah": 30, "33. Al-Ahzab": 73, "34. Saba'": 54, "35. Fatir": 45,
    "36. Yasin": 83, "37. As-Saffat": 182, "38. Sad": 88, "39. Az-Zumar": 75, "40. Ghafir": 85,
    "41. Fussilat": 54, "42. Asy-Syura": 53, "43. Az-Zukhruf": 89, "44. Ad-Dukhan": 59, "45. Al-Jasiyah": 37,
    "46. Al-Ahqaf": 35, "47. Muhammad": 38, "48. Al-Fath": 29, "49. Al-Hujurat": 18, "50. Qaf": 45,
    "51. Az-Zariyat": 60, "52. At-Tur": 49, "53. An-Najm": 62, "54. Al-Qamar": 55, "55. Ar-Rahman": 78,
    "56. Al-Waqi'ah": 96, "57. Al-Hadid": 29, "58. Al-Mujadilah": 22, "59. Al-Hasyr": 24, "60. Al-Mumtahanah": 13,
    "61. As-Saff": 14, "62. Al-Jumu'ah": 11, "63. Al-Munafiqun": 11, "64. At-Taghabun": 18, "65. At-Talaq": 12,
    "66. At-Tahrim": 12, "67. Al-Mulk": 30, "68. Al-Qalam": 52, "69. Al-Haqqah": 52, "70. Al-Ma'arij": 44,
    "71. Nuh": 28, "72. Al-Jinn": 28, "73. Al-Muzzammil": 20, "74. Al-Muddassir": 56, "75. Al-Qiyamah": 40,
    "76. Al-Insan": 31, "77. Al-Mursalat": 50, "78. An-Naba'": 40, "79. An-Nazi'at": 46, "80. 'Abasa": 42,
    "81. At-Takwir": 29, "82. Al-Infitar": 19, "83. Al-Mutaffifin": 36, "84. Al-Inshiqaq": 25, "85. Al-Buruj": 22,
    "86. At-Tariq": 17, "87. Al-A'la": 19, "88. Al-Ghasyiyah": 26, "89. Al-Fajr": 30, "90. Al-Balad": 20,
    "91. Asy-Syams": 15, "92. Al-Lail": 21, "93. Ad-Duha": 11, "94. Asy-Syarh": 8, "95. At-Tin": 8,
    "96. Al-'Alaq": 19, "97. Al-Qadr": 5, "98. Al-Bayyinah": 8, "99. Az-Zalzalah": 8, "100. Al-'Adiyat": 11,
    "101. Al-Qari'ah": 11, "102. At-Takasur": 8, "103. Al-'Asr": 3, "104. Al-Humazah": 9, "105. Al-Fil": 5,
    "106. Quraisy": 4, "107. Al-Ma'un": 7, "108. Al-Kausar": 3, "109. Al-Kafirun": 6, "110. An-Nasr": 3,
    "111. Al-Lahab": 5, "112. Al-Ikhlas": 4, "113. Al-Falaq": 5, "114. An-Nas": 6
}

DAFTAR_114_SURAH = list(DATA_SURAH_AYAT.keys())

TASMI_COLUMNS = [
    "Tanggal", "Periode", "Kelas", "Nama Murid", "Penguji",
    "Rentang Surah", "Err Besar", "Err Kecil", "Nilai Akhir", "Catatan"
]

DAFTAR_MUHAFFIDZ = [
    "UST. Rijal, S.Pd.I.",
    "UST. Hudzaifah",
    "UST. Moh. Faiz Gufran, S.H.",
    "UST. Achmad Adnan P.H.",
    "UST. Muhammad Bagus Ammar",
    "UST. Luthfi Dwi Hatmadja Sudiro",
    "UST. Muhammad Rafly Rifadillah",
]

CREDENTIALS = {
    "adnanputra@iqis.sch.id": "Tahfizsmp8!",
    "muh294@admin.smp.belajar.id": "Tahfizsmp8!",
    "mohfaizgufran@iqis.sch.id": "Tahfizsmp8!",
    "rafly@iqis.sch.id": "Tahfizsmp8!",
    "bagusammar@iqis.sch.id": "Tahfizsmp8!",
    "huzaifah@iqis.sch.id": "Tahfizsmp8!",
}

DATABASE_MURID = {
    "KELAS VII A": [
        "Adelard Muhammad Athar - 2610380000", "Adzkhan Zidan Alkhalifi - 73710905",
        "Al Ghazali Hidayat - 144498445", "Anhar Al Ghazali - 2610383000",
        "Aufar Abdillah Pratama - 3147254000", "Azzam Zahran Hasyim - 138357008",
        "Fadrian Ananta Rizkullah - 3132885678", "Fathan Azka Erlangga - 3141007874",
        "Muh Abidzar Ramadhan - 3140775000", "Muh Afif Ismail - 2610389000",
        "Muh Fadlan Khalifah Aqil Haeruddin - 2610390000", "Muh. Arrahfi Abimayudhitya - 3139924000",
        "Muh. Ayyash Triansyah - 3144640000", "Muhammad Abdurahman Putra Subara - 3144238000",
        "Muhammad Afdhal Al Ghiffari Rahmat - 2012070000", "Muhammad Athallah Azka - 2610396000",
        "Muhammad Bilal Qushay - 3137064000", "Muhammad Farid Atallah - 2610397000",
        "Muhammad Fauzan Akbar - 145953134", "Muhammad Raihan Ar Razin - 146047347",
        "Naufal Afkar Narja - 3148227000",
    ],
    "KELAS VII C": [
        "Abdillah Yusuf Putra Asri - 1032000237", "Adelard Rabbani - 149243685",
        "Adhyastha Fauzan Putra Andrianto - 3138085000", "Adskhan Fahmi Fawwaz - 3157157000",
        "Ahmad Rakan Fariz Rani - 3147420000", "Alfatih Muhammad Khawarizmi - 3144939656",
        "Ammar - 3122477000", "Andi Adeeb Abrar Agussalim - 3131498000",
        "Daffa Isya Al Dhabith - 737111000000", "Dzahaby Khalish Akram - 144102228",
        "Ghali Shahijun Khalq - 2610429000", "Haziq Afif Daiyan - 2000249730",
        "Muh Aflah Dzakirin Nasrullah - 3136476000", "Muh Ilham Isyak - 145305229",
        "Muhammad Akhdan Alfarizqi - 143626367", "Muhammad Imran Tsaqieb Rahmat - 2012070002",
        "Muhammad Raziq Hanania - 73711123", "Rafli Azzam Syahril - 2610436000",
        "Uwais Kaisan - 3132325000", "Zayyan Syafiq Shan - 133200784",
    ],
    "KELAS VIIIA": [
        "Achmad Sakha Recca Al Fath - 2510288", "Ahmad Yasin Mubarak - 2510289",
        "Akhdan Dzakwan Ahmad - 2510290", "Al Ahnaf Gani Poetra - 2510291",
        "Andi Muh. Dzaka Dzarwah Alam - 2510292", "Andi Muh. Athallah Azka - 2510293",
        "Bintang Tahta Al Hidayah. T - 2510294", "Danish Darmawan Arsyad - 2510295",
        "Dwi Dzaky Al Ghozaly - 2510296", "Fadel Mubarak Ihsan - 2510297",
        "Iqbal Ghaisan Iskandar - 2510298", "Leon David Alexma Rava - 2510299",
        "Luqman Hakim Rumodar - 2510300", "M. Zayn Adzaky Nawir - 2510301",
        "Muh Al Fabian Syah - 2510302", "Muhammad Reyvan Risani Rahmatullah - 2510303",
        "Muh. Aimar Zahwan - 2510304", "Muh. Alif Arif - 2510305",
        "Muh. Rayyan Ramadhan - 2510306", "Muhammad Ridho Syahrir - 2510307",
        "Muhammad Uswah - 2510308", "Zidan Arkana - 2510309",
        "Sultan Asshiddiq - 2510379", "Muhammad Fauzan Arief Raaka - 2610457",
    ],
    "KELAS VIIIC": [
        "Abdul Khaliq - 2510335", "Andi Al Walid Mappatonang - 2510336",
        "Andrea milan elshaarawi - 2510337", "Bilfaqih Alteza Hasid - 2510338",
        "Dzaky Putra Triatama - 2510339", "Fadhil Abdillah Hasan - 2510340",
        "Faiz Ibrahim - 2510341", "Faizi Almaz Al-Baariqh - 2510342",
        "I Datuk Mirza Hibatullah Zahri - 2510343", "M. Dhafin Harits J - 2510344",
        "Muh Rasya AlFatah S - 2510345", "Muh. Fathin Affandi - 2510346",
        "Muhammad Yasir Az Zuhri - 2510347", "Muhammad Al Furqan - 2510348",
        "Muhammad Ali Kurniawan - 2510349", "Muhammad Danish Achmad - 2510350",
        "Muhammad Fathan Rahman - 2510351", "Muhammad Fikhi Anugrah - 2510352",
        "Muhammad Shafwan - 2510353", "Muhammad Yassar Asman - 2510354",
        "Muhammad Zaid Y - zaq1", "Zayyan Akasyah - 2510356",
    ],
    "KELAS IX A": [
        "Abdullah Azzam Asfar - 3123481089", "Ariq Merdeka Ramadhan - 3115732852",
        "Bintang Anugrah - 0116080905", "Fahreza Hanif Wijaya - 2410238",
        "Ibrahim - 2410239", "Muh. Aisyar Isbal - 2410240",
        "Muh. Darul Tri Akbar - 2410241", "Muh. Rakha Rizqullah - 2410243",
        "Muh. Zaki Zulhilmi - 2410244", "Muhammad Alif Afreiza Herwan - 2410245",
        "Muhammad Arsya Al Husain - 2410246", "Muhammad Cakra Pratama Ompo Massa - 2410247",
        "Muhammad Furqan - 2410248", "Muhammad Ghazian Asfa - 2410249",
        "Muhammad Maulana Ishak - 2410250", "Muhammad Nizarrazzaq Marwan - 2410251",
        "Rahmat Faizi - 2410252", "Wahyu Triyantono. S - 2410253",
        "Dzakwan Fauzan Kalesaran - 2410287", "Azka Faried Athallah Sulkifli - 002610458",
    ],
}

def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

img_logo_base64 = get_image_base64(LOGO_FILENAME)
img_logo_src = f"data:image/jpeg;base64,{img_logo_base64}" if img_logo_base64 else LOGO_FILENAME

header_bg_base64 = get_image_base64(HEADER_BG_FILENAME)
header_bg_src = f"data:image/jpeg;base64,{header_bg_base64}" if header_bg_base64 else HEADER_BG_FILENAME

st.set_page_config(
    page_title="TahfidzTrack — SMPIT Ibnul Qayyim",
    page_icon=LOGO_FILENAME if os.path.exists(LOGO_FILENAME) else "🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
<style>
    @keyframes techFadeIn {{
        0% {{ opacity: 0; transform: translateY(20px) scale(0.98); filter: blur(8px); }}
        100% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0px); }}
    }}

    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 15px rgba(187, 199, 164, 0.2); }}
        50% {{ box-shadow: 0 0 30px rgba(187, 199, 164, 0.5); }}
        100% {{ box-shadow: 0 0 15px rgba(187, 199, 164, 0.2); }}
    }}

    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.82)), 
                    url("{img_logo_src}") no-repeat center center fixed !important;
        background-size: cover !important;
        color: #FFFFFF !important;
    }}

    .stMainBlockContainer {{ animation: techFadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}

    /* WARNA TEKS UMUM UTAMA */
    h1, h2, h3, h4, h5, h6, p, span, label, div,
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stWidgetLabel"] span, 
    .stCaption, .stCaption p, .stMarkdown, .stMarkdown p {{
        color: #FFFFFF !important; 
        font-weight: 700 !important; 
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8) !important;
    }}

    button[data-baseweb="tab"] p {{
        color: #FFFFFF !important; font-weight: 600 !important; font-size: 14px !important; transition: all 0.3s ease;
    }}
    button[data-baseweb="tab"][aria-selected="true"] p {{
        color: #FFFFFF !important; font-weight: 800 !important; text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }}
    div[data-baseweb="tab-highlight"] {{ background-color: #FFFFFF !important; }}

    .main-header {{
        background: linear-gradient(135deg, rgba(61, 74, 47, 0.45), rgba(187, 199, 164, 0.35)),
                    url("{header_bg_src}") no-repeat center center !important;
        background-size: cover !important; padding: 30px 20px; border-radius: 16px; color: #FFFFFF; margin-bottom: 20px;
        text-align: center; border: 2px solid #bbc7a4; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        animation: techFadeIn 0.7s ease-out, pulseGlow 4s infinite ease-in-out;
    }}
    .main-header h1 {{
        font-size: 28px !important; font-weight: 800 !important; margin: 12px 0 0 0 !important; color: #FFFFFF !important;
        letter-spacing: 0.5px; text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8) !important;
    }}
    .main-header p {{
        font-size: 14px; margin-top: 6px; color: #FFFFFF !important; font-weight: 600; text-shadow: 0 1px 6px rgba(0, 0, 0, 0.8) !important;
    }}

    /* KOTAK KARTU DENGAN WARNA BARU #bbc7a4 DAN TEKS GELAP AGAR CONTRAS DAN JELAS */
    .card-box, div[data-testid="stForm"] {{
        background-color: #bbc7a4 !important; border: 1.5px solid #a3b28b !important; border-radius: 14px !important;
        padding: 20px !important; margin-bottom: 15px !important; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
        animation: techFadeIn 0.8s ease-out; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .card-box:hover, div[data-testid="stForm"]:hover {{
        border-color: #FFFFFF !important; box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5) !important; transform: translateY(-2px);
    }}

    /* Penyesuaian warna teks di dalam card-box & form agar terlihat kontras dengan background #bbc7a4 */
    .card-box h3, div[data-testid="stForm"] h3, 
    .card-box p, div[data-testid="stForm"] p,
    .card-box span, div[data-testid="stForm"] span,
    .card-box label, div[data-testid="stForm"] label,
    div[data-testid="stForm"] div[data-testid="stWidgetLabel"] p,
    div[data-testid="stForm"] div[data-testid="stWidgetLabel"] span {{ 
        color: #1E293B !important; 
        text-shadow: none !important;
    }}

    .metric-value {{ font-size: 28px; font-weight: 800; color: #1E293B !important; text-shadow: none !important; }}
    .metric-label {{ font-size: 12px; color: #334155 !important; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; text-shadow: none !important; }}

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
        background-color: #1E293B !important; border: 1px solid #bbc7a4 !important; color: #FFFFFF !important; border-radius: 8px !important;
    }}
    div[data-baseweb="input"] input {{ color: #FFFFFF !important; }}

    .stButton > button {{
        background: #bbc7a4 !important; color: #1E293B !important; font-weight: 800 !important; border-radius: 10px !important; border: none !important;
        padding: 10px 16px !important; box-shadow: 0 4px 12px rgba(187, 199, 164, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; width: 100%; position: relative; overflow: hidden;
    }}
    .stButton > button:hover {{
        background: #a3b28b !important; color: #0F172A !important; transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 18px rgba(163, 178, 139, 0.5) !important;
    }}
    .stButton > button:active {{ transform: translateY(1px) scale(0.99); }}

    .badge-success {{ background-color: #bbc7a4; color: #1E293B !important; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #3D4A2F; }}
    .badge-admin {{ background-color: #6A4C3B; color: #FFFFFF !important; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #3D4A2F; }}
</style>
""",
    unsafe_allow_html=True,
)

def update_user_session(email, status="online"):
    sessions = {}
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                sessions = json.load(f)
        except Exception:
            sessions = {}
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "online":
        sessions[email] = {
            "status": "Online 🟢",
            "last_active": now_str,
            "login_time": sessions.get(email, {}).get("login_time", now_str)
        }
    else:
        if email in sessions:
            sessions[email]["status"] = "Offline 🔴"
            sessions[email]["last_active"] = now_str
            
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=4)

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def load_data():
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(
            columns=[
                "Tanggal", "Guru Input", "Kelas", "Nama Murid",
                "Juz", "Jenis Setoran", "Surah", "Ayat Awal",
                "Ayat Akhir", "Halaman", "Salah", "Nilai",
            ]
        )
        df_init.to_csv(DATA_FILE, index=False)
        return df_init
    df = pd.read_csv(DATA_FILE)
    if "Nama Santri" in df.columns:
        df.rename(columns={"Nama Santri": "Nama Murid"}, inplace=True)
    if "Juz" not in df.columns:
        df["Juz"] = "-"
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_tasmi_data():
    if not os.path.exists(TASMI_DATA_FILE):
        df_init = pd.DataFrame(columns=TASMI_COLUMNS)
        df_init.to_csv(TASMI_DATA_FILE, index=False)
        return df_init
    df = pd.read_csv(TASMI_DATA_FILE)
    for col in TASMI_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[TASMI_COLUMNS]

def save_tasmi_data(df):
    df = df.reindex(columns=TASMI_COLUMNS)
    df.to_csv(TASMI_DATA_FILE, index=False)

def build_spreadsheet_matrix(df_raw, nama_kelas):
    santri_list = DATABASE_MURID.get(nama_kelas, [])
    records = []

    for idx, s_full in enumerate(santri_list, 1):
        parts = s_full.split(" - ")
        s_nama = parts[0]
        s_nis = parts[1] if len(parts) > 1 else "-"

        df_s = df_raw[(df_raw["Kelas"] == nama_kelas) & (df_raw["Nama Murid"] == s_full)]

        row_data = {
            "No": idx,
            "NIS": s_nis,
            "Nama Lengkap": s_nama,
            "Status Target": "Selesai" if len(df_s) >= 300 else "Progres",
        }

        scores = []
        for col_idx in range(1, 301):
            if col_idx - 1 < len(df_s):
                s_row = df_s.iloc[col_idx - 1]
                juz_val = s_row.get("Juz", "-")
                surah_val = s_row.get("Surah", "-")
                nilai_val = s_row.get("Nilai", 0.0)

                row_data[f"Setoran {col_idx} (Juz)"] = "-" if pd.isna(juz_val) or str(juz_val) == "" else str(juz_val)
                row_data[f"Setoran {col_idx} (Surah)"] = str(surah_val)
                row_data[f"Setoran {col_idx} (Nilai)"] = float(nilai_val)
                scores.append(float(nilai_val))
            else:
                row_data[f"Setoran {col_idx} (Juz)"] = "-"
                row_data[f"Setoran {col_idx} (Surah)"] = "-"
                row_data[f"Setoran {col_idx} (Nilai)"] = "-"

        row_data["Rata-Rata Nilai"] = round(sum(scores) / len(scores), 2) if scores else 0.0
        records.append(row_data)

    return pd.DataFrame(records)

def build_tasmi_matrix(df_tasmi_raw, nama_kelas):
    santri_list = DATABASE_MURID.get(nama_kelas, [])
    records = []

    for idx, s_full in enumerate(santri_list, 1):
        parts = s_full.split(" - ")
        s_nama = parts[0]
        s_nis = parts[1] if len(parts) > 1 else "-"

        df_s = df_tasmi_raw[(df_tasmi_raw["Kelas"] == nama_kelas) & (df_tasmi_raw["Nama Murid"] == s_full)]

        row_data = {
            "No": idx,
            "NIS": s_nis,
            "Nama Lengkap": s_nama,
            "Status Target": "Selesai" if not df_s.empty else "Belum Tasmi'",
        }

        scores = []
        for col_idx in range(1, 11):
            if col_idx - 1 < len(df_s):
                s_row = df_s.iloc[col_idx - 1]
                surah_val = s_row.get("Rentang Surah", "-")
                err_b = s_row.get("Err Besar", 0)
                err_k = s_row.get("Err Kecil", 0)
                nilai_val = s_row.get("Nilai Akhir", 0.0)

                row_data[f"Tasmi' {col_idx} - Surah"] = str(surah_val)
                row_data[f"Tasmi' {col_idx} - Err Besar"] = int(err_b)
                row_data[f"Tasmi' {col_idx} - Err Kecil"] = int(err_k)
                row_data[f"Tasmi' {col_idx} - Nilai"] = float(nilai_val)
                scores.append(float(nilai_val))
            else:
                row_data[f"Tasmi' {col_idx} - Surah"] = "-"
                row_data[f"Tasmi' {col_idx} - Err Besar"] = "-"
                row_data[f"Tasmi' {col_idx} - Err Kecil"] = "-"
                row_data[f"Tasmi' {col_idx} - Nilai"] = "-"

        row_data["Rata-Rata Tasmi'"] = round(sum(scores) / len(scores), 2) if scores else 0.0
        records.append(row_data)

    return pd.DataFrame(records)

def generate_pdf(df_filtered, bulan_tahun, nama_kelas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13,
        textColor=colors.HexColor("#3D4A2F"), alignment=1, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.HexColor("#6A4C3B"), alignment=1, spaceAfter=15
    )
    bold_text_style = ParagraphStyle("BoldTextStyle", parent=styles["Normal"], fontName="Helvetica-Bold")

    if os.path.exists(LOGO_FILENAME):
        img = RLImage(LOGO_FILENAME, width=50, height=50)
        img.hAlign = "CENTER"
        elements.append(img)
        elements.append(Spacer(1, 6))

    elements.append(Paragraph("LAPORAN REKAPITULASI BULANAN TAHFIDZ QURAN", title_style))
    elements.append(Paragraph(f"SMPIT IBNUL QAYYIM MAKASSAR — {nama_kelas} | Periode: {bulan_tahun}", subtitle_style))

    table_data = [["No", "Tanggal", "Nama Murid", "Jenis", "Surah (Ayat)", "Hlm", "Nilai"]]
    for idx, row in df_filtered.reset_index(drop=True).iterrows():
        a_awal = str(row["Ayat Awal"]).split(".")[0] if pd.notna(row.get("Ayat Awal")) else "-"
        a_akhir = str(row["Ayat Akhir"]).split(".")[0] if pd.notna(row.get("Ayat Akhir")) else "-"
        
        table_data.append([
            str(idx + 1), str(row["Tanggal"]), str(row["Nama Murid"]).split(" - ")[0][:18],
            str(row["Jenis Setoran"]), f"{row['Surah']} ({a_awal}-{a_akhir})",
            f"{row['Halaman']}", f"{row['Nilai']}",
        ])

    t = Table(table_data, colWidths=[25, 65, 140, 55, 140, 35, 45])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3D4A2F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#ECE7DC")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECE7DC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbc7a4")),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    kelas_clean = nama_kelas.upper().replace(" ", "")
    if "VIIA" in kelas_clean:
        koordinator = "UST. Rijal, S.Pd.I."
    elif "IXA" in kelas_clean:
        koordinator = "UST. Hudzaifah"
    elif "VIIIA" in kelas_clean:
        koordinator = "UST. Moh. Faiz Gufran, S.H."
    else:
        koordinator = "UST. Achmad Adnan P.H."

    tgl_str = datetime.date.today().strftime("%d %B %Y")
    p_left_1 = Paragraph("Mengetahui,", styles["Normal"])
    p_left_2 = Paragraph("Kepala Sekolah SMPIT Ibnul Qayyim", styles["Normal"])
    p_left_name = Paragraph(KEPALA_SEKOLAH, bold_text_style)

    p_right_1 = Paragraph(f"Makassar, {tgl_str}", styles["Normal"])
    p_right_2 = Paragraph("Koordinator Tahfidz Kelas", styles["Normal"])
    p_right_name = Paragraph(koordinator, bold_text_style)

    ttd_table = Table(
        [
            [p_left_1, "", p_right_1],
            [p_left_2, "", p_right_2],
            ["", "", ""],
            ["", "", ""],
            [p_left_name, "", p_right_name],
        ],
        colWidths=[220, 60, 220],
    )
    ttd_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(ttd_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def render_header(title, subtitle):
    st.markdown(
        f"""
        <div class="main-header">
            <img src="{img_logo_src}" width="65" style="border-radius: 50%; background: #ECE7DC; padding: 3px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = ""
    st.session_state["is_admin"] = False
if "admin_board_unlocked" not in st.session_state:
    st.session_state["admin_board_unlocked"] = False

if not st.session_state["logged_in"]:
    render_header("TahfidzTrack — SMPIT Ibnul Qayyim", "Sistem Management & Monitoring Hafalan Qur'an Murid")

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        with st.form("login_form"):
            st.subheader("🔑 Autentikasi Pengampu")
            email = st.text_input("Alamat Email Akademik", placeholder="contoh: adnanputra@iqis.sch.id")
            password = st.text_input("Sandi Keamanan", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Akses Portal ➔")

            if submit:
                email_clean = email.strip().lower()
                pass_clean = password.strip()
                if email_clean in CREDENTIALS and CREDENTIALS[email_clean] == pass_clean:
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = email_clean
                    st.session_state["is_admin"] = email_clean in ADMIN_ACCOUNTS
                    update_user_session(email_clean, "online")
                    st.success("Otentikasi berhasil!")
                    st.rerun()
                else:
                    st.error("Kredensial tidak terverifikasi.")

else:
    update_user_session(st.session_state["user_email"], "online")
    render_header("TahfidzTrack — SMPIT Ibnul Qayyim", "Sistem Management & Monitoring Hafalan Qur'an Murid")

    c_user, c_logout = st.columns([4, 1])
    with c_user:
        badge_cls = "badge-admin" if st.session_state["is_admin"] else "badge-success"
        role_label = " [ADMIN]" if st.session_state["is_admin"] else ""
        st.markdown(
            f"⚡ **User Active:** <span class='{badge_cls}'>{st.session_state['user_email']}{role_label}</span>",
            unsafe_allow_html=True,
        )
    with c_logout:
        if st.button("🚪 Keluar"):
            update_user_session(st.session_state["user_email"], "offline")
            st.session_state["logged_in"] = False
            st.session_state["user_email"] = ""
            st.session_state["is_admin"] = False
            st.session_state["admin_board_unlocked"] = False
            st.rerun()

    st.write("")
    df_data = load_data()
    df_tasmi = load_tasmi_data()

    tab_list = [
        "✦ Presensi Setoran",
        "◈ Analytics & Rekap Matrix",
        "🪶 Tracking Portal",
        "📜 Certificate & PDF",
        "🎯 Ujian Tasmi'",
        "📂 Database Tasmi'",
    ]
    if st.session_state["is_admin"]:
        tab_list.append("🛡️ Admin Board")

    tabs = st.tabs(tab_list)

    # --- TAB 1: INPUT SETORAN ---
    with tabs[0]:
        st.subheader("✨ Form Input Setoran Harian")
        st.caption("Pencatatan progres hafalan harian murid secara real-time")

        c1, c2 = st.columns(2)
        with c1:
            kelas_sel = st.selectbox("🏛️ Rombongan Belajar", list(DATABASE_MURID.keys()))
            murid_sel = st.selectbox("👤 Profil Murid", DATABASE_MURID[kelas_sel])
            penguji_setoran = st.selectbox("👨‍🏫 Guru Muhaffidz / Penguji", DAFTAR_MUHAFFIDZ)
            jenis_sel = st.selectbox("📌 Kategori Setoran", ["Sabaq", "Murajaah", "Manzil"])

        with c2:
            juz_sel = st.text_input("📖 Juz (Contoh: 30, 29, dll)", "30")
            surah_sel = st.selectbox("🪷 Nama Surah Al-Qur'an", DAFTAR_114_SURAH, index=1)
            
            # HITUNG MAKSIMAL AYAT SESUAI SURAH
            max_ayat_surah = DATA_SURAH_AYAT.get(surah_sel, 286)
            st.caption(f"ℹ️ Surah **{surah_sel}** memiliki **1 sampai {max_ayat_surah} Ayat**.")

            # LIST DROPDOWN AYAT PERSISI HANYA SAMPAI JUMLAH AYAT SURAHNYA
            list_opsi_ayat = list(range(1, max_ayat_surah + 1))

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                ayat_awal = st.selectbox(
                    "🧮 Ayat Awal", 
                    options=list_opsi_ayat,
                    index=0,
                    key=f"a_awal_{surah_sel}"
                )
            with col_a2:
                # DEFAULT AYAT AKHIR MENYESUAIKAN
                default_idx_akhir = min(ayat_awal + 8, max_ayat_surah - 1)
                ayat_akhir = st.selectbox(
                    "🧮 Ayat Akhir", 
                    options=list_opsi_ayat,
                    index=default_idx_akhir,
                    key=f"a_akhir_{surah_sel}"
                )

            # VALIDASI JIKA PILIHAN AYAT TERBALIK
            is_valid_ayat = (ayat_akhir >= ayat_awal)
            if not is_valid_ayat:
                st.error("⚠️ (data yang anda masukkan tidak sesuai) — Ayat Akhir tidak boleh lebih kecil dari Ayat Awal!")

            halaman = st.number_input("📄 Volume (Halaman)", min_value=0.1, value=1.0, step=0.5)
            salah = st.number_input("⚡ Catatan Kekurangan/Bantuan", min_value=0, value=0)

        nilai_calc = max(0.0, min(100.0, round(100.0 - (salah * 2.0), 2)))

        st.write("")
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="metric-label">Indeks Kelancaran Hafalan</div>
                    <div class="metric-value">{nilai_calc} <span style="font-size:16px; color:#1E293B;">/ 100</span></div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        with m2:
            kualitas = "Mumtaz (Sangat Baik)" if nilai_calc >= 90 else ("Jayyid Jiddan (Baik)" if nilai_calc >= 75 else ("Jayyid (Cukup)" if nilai_calc >= 60 else "Rasib (Perlu Murajaah)"))
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="metric-label">Predikat Evaluasi</div>
                    <div class="metric-value" style="font-size: 20px; color: #1E293B; padding-top:6px;">{kualitas}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # TOMBOL DISERTAI PROTECTION AGAR TDK BISA DIKLIK JIKA INPUT TIDAK SUAI
        if st.button("🛡️ SIMPAN RECORD SETORAN", disabled=not is_valid_ayat):
            new_record = {
                "Tanggal": datetime.date.today().strftime("%Y-%m-%d"),
                "Guru Input": penguji_setoran,
                "Kelas": kelas_sel,
                "Nama Murid": murid_sel,
                "Juz": juz_sel,
                "Jenis Setoran": jenis_sel,
                "Surah": surah_sel,
                "Ayat Awal": int(ayat_awal),
                "Ayat Akhir": int(ayat_akhir),
                "Halaman": halaman,
                "Salah": salah,
                "Nilai": nilai_calc,
            }
            df_updated = pd.concat([df_data, pd.DataFrame([new_record])], ignore_index=True)
            save_data(df_updated)
            st.snow()
            st.toast(f"Data setoran {murid_sel.split(' - ')[0]} berhasil disimpan.", icon="🕌")

    # --- TAB 2: REKAPAN & SPREADSHEET MATRIX ---
    with tabs[1]:
        st.subheader("◈ Matriks Spreadsheet Tahfidz")
        st.caption("Matriks horizontal riwayat setoran siswa")

        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f'<div class="card-box"><div class="metric-label">Total Setoran</div><div class="metric-value">{len(df_data)}</div></div>', unsafe_allow_html=True)
        with k2:
            total_hlm = round(df_data["Halaman"].sum(), 2) if not df_data.empty else 0
            st.markdown(f'<div class="card-box"><div class="metric-label">Total Halaman</div><div class="metric-value">{total_hlm}</div></div>', unsafe_allow_html=True)
        with k3:
            rata_nilai = round(df_data["Nilai"].mean(), 2) if not df_data.empty else 0.0
            st.markdown(f'<div class="card-box"><div class="metric-label">Rata-Rata Nilai</div><div class="metric-value">{rata_nilai}</div></div>', unsafe_allow_html=True)

        kelas_matrix_sel = st.selectbox("🔍 Pilih Kelas Matriks", list(DATABASE_MURID.keys()), key="matrix_kelas_select")
        df_matrix_result = build_spreadsheet_matrix(df_data, kelas_matrix_sel)
        st.dataframe(df_matrix_result, use_container_width=True, height=400)

    # --- TAB 3: TRACKING PORTAL ---
    with tabs[2]:
        st.subheader("🪶 Tracking Portal Murid")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            k_track = st.selectbox("Pilih Kelas", list(DATABASE_MURID.keys()), key="track_k")
        with col_t2:
            m_track = st.selectbox("Pilih Murid", DATABASE_MURID[k_track], key="track_m")

        df_single = df_data[(df_data["Kelas"] == k_track) & (df_data["Nama Murid"] == m_track)]
        if df_single.empty:
            st.info("Belum ada riwayat setoran.")
        else:
            st.dataframe(df_single, use_container_width=True)

    # --- TAB 4: CERTIFICATE & PDF ---
    with tabs[3]:
        st.subheader("📜 Generator Laporan PDF")
        c_pdf1, c_pdf2 = st.columns(2)
        with c_pdf1:
            pdf_kelas = st.selectbox("Kelas Target", list(DATABASE_MURID.keys()), key="pdf_k")
        with c_pdf2:
            pdf_periode = st.text_input("Periode Laporan", "September 2026")

        df_pdf_data = df_data[df_data["Kelas"] == pdf_kelas]
        if st.button("📄 Generate Berkas PDF"):
            if df_pdf_data.empty:
                st.warning("Data setoran kosong.")
            else:
                pdf_bytes = generate_pdf(df_pdf_data, pdf_periode, pdf_kelas)
                st.download_button("⬇️ Unduh PDF", data=pdf_bytes, file_name=f"Laporan_{pdf_kelas}_{pdf_periode}.pdf", mime="application/pdf")

    # --- TAB 5: UJIAN TASMI' ---
    with tabs[4]:
        st.subheader("🎯 Form Input Ujian Tasmi'")
        with st.form("form_tasmi"):
            col_tas1, col_tas2 = st.columns(2)
            with col_tas1:
                t_periode = st.text_input("Periode Ujian", "Triwulan I - 2026")
                t_kelas = st.selectbox("Kelas Ujian", list(DATABASE_MURID.keys()), key="tas_k")
                t_murid = st.selectbox("Nama Murid Ujian", DATABASE_MURID[t_kelas], key="tas_m")
                t_penguji = st.selectbox("Penguji Tasmi'", DAFTAR_MUHAFFIDZ, key="tas_p")

            with col_tas2:
                t_surah = st.text_input("Rentang Surah/Juz", "Juz 30 (Al-Naba' - An-Nas)")
                err_besar = st.number_input("Kesalahan Besar (Salah/Lupa)", min_value=0, value=0)
                err_kecil = st.number_input("Kesalahan Kecil (Tajwid/Makhraj)", min_value=0, value=0)
                t_catatan = st.text_area("Catatan Penguji", placeholder="Catatan evaluasi kelancaran dan makhraj...")

            nilai_tasmi = max(0.0, min(100.0, round(100.0 - (err_besar * 2.0) - (err_kecil * 0.5), 2)))
            
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="metric-label">Nilai Akhir Ujian Tasmi'</div>
                    <div class="metric-value">{nilai_tasmi} <span style="font-size:16px; color:#1E293B;">/ 100</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            submit_tasmi = st.form_submit_button("🎯 SIMPAN RECORD TASMI'")

            if submit_tasmi:
                new_tasmi_record = {
                    "Tanggal": datetime.date.today().strftime("%Y-%m-%d"),
                    "Periode": t_periode,
                    "Kelas": t_kelas,
                    "Nama Murid": t_murid,
                    "Penguji": t_penguji,
                    "Rentang Surah": t_surah,
                    "Err Besar": err_besar,
                    "Err Kecil": err_kecil,
                    "Nilai Akhir": nilai_tasmi,
                    "Catatan": t_catatan,
                }
                df_tasmi_updated = pd.concat([df_tasmi, pd.DataFrame([new_tasmi_record])], ignore_index=True)
                save_tasmi_data(df_tasmi_updated)
                st.snow()
                st.toast(f"Data ujian Tasmi' {t_murid.split(' - ')[0]} berhasil disimpan.", icon="🎯")

    # --- TAB 6: DATABASE TASMI' ---
    with tabs[5]:
        st.subheader("📂 Matriks Database Ujian Tasmi'")
        st.caption("Rekapitulasi nilai dan kesalahan ujian Tasmi' murid")

        tasmi_k_matrix = st.selectbox("🔍 Pilih Kelas Matriks Tasmi'", list(DATABASE_MURID.keys()), key="tasmi_matrix_kelas_select")
        df_tasmi_matrix_result = build_tasmi_matrix(df_tasmi, tasmi_k_matrix)
        st.dataframe(df_tasmi_matrix_result, use_container_width=True, height=400)

    # --- TAB 7: ADMIN BOARD ---
    if st.session_state["is_admin"]:
        with tabs[6]:
            st.title("🛡️ Control Panel & System Governance")
            st.caption("Pusat kendali sesi pengguna dan manajemen pemeliharaan basis data.")

            st.subheader("🟢 Monitoring Sesi Aktif")
            sessions_data = load_sessions()
            
            if sessions_data:
                df_sessions = pd.DataFrame.from_dict(sessions_data, orient="index").reset_index()
                df_sessions.columns = ["Email Guru", "Status", "Aktivitas Terakhir", "Waktu Login"]

                total_aktif = len(df_sessions[df_sessions["Status"] == "Online 🟢"]) if "Status" in df_sessions.columns else len(df_sessions)
                m1, m2 = st.columns(2)
                m1.metric("Total Sesi Terdaftar", len(df_sessions))
                m2.metric("Sesi Aktif / Online", total_aktif)

                st.dataframe(
                    df_sessions,
                    use_container_width=True,
                    column_config={
                        "Email Guru": st.column_config.TextColumn("Email Pengguna"),
                        "Status": st.column_config.TextColumn("Status Sesi"),
                        "Waktu Login": st.column_config.TextColumn("Waktu Login"),
                        "Aktivitas Terakhir": st.column_config.TextColumn("Aktivitas Terakhir"),
                    },
                    hide_index=True
                )
            else:
                st.info("Belum ada log sesi pengguna yang terekam.")

            st.divider()

            st.subheader("⚠️ Manajemen Pemeliharaan Data")
            
            if not st.session_state["admin_board_unlocked"]:
                with st.container(border=True):
                    st.warning("Akses fitur hapus data dibatasi. Masukkan kata sandi admin khusus untuk membuka otorisasi.")
                    
                    with st.form("form_unlock_admin"):
                        admin_pass_input = st.text_input("Sandi Keamanan Admin", type="password", key="admin_unlock_pass")
                        btn_unlock = st.form_submit_button("🔓 Buka Otorisasi Fitur Sensitive", type="primary")

                        if btn_unlock:
                            if admin_pass_input == ADMIN_PANEL_PASSKEY:
                                st.session_state["admin_board_unlocked"] = True
                                st.success("Otorisasi berhasil. Akses kontrol terbuka.")
                                st.rerun()
                            else:
                                st.error("Kata sandi salah! Akses ditolak.")
            else:
                st.success("Sistem Terbuka (Unlocked) — Anda memiliki hak akses penuh untuk menghapus data.", icon="🔓")
                
                col_adm1, col_adm2 = st.columns(2)

                with col_adm1:
                    with st.container(border=True):
                        st.markdown("##### 🗑️ Hapus Setoran Harian")
                        if not df_data.empty:
                            record_to_delete = st.selectbox(
                                "Pilih Record Setoran:",
                                df_data.index.tolist(),
                                format_func=lambda x: f"{df_data.loc[x, 'Tanggal']} | {df_data.loc[x, 'Nama Murid'].split(' - ')[0]} | {df_data.loc[x, 'Surah']}"
                            )
                            if st.button("🚨 Hapus Record Setoran", type="primary", use_container_width=True, key="btn_del_setoran"):
                                df_data_updated = df_data.drop(index=record_to_delete).reset_index(drop=True)
                                save_data(df_data_updated)
                                st.toast("Record setoran harian berhasil dihapus.", icon="🗑️")
                                st.rerun()
                        else:
                            st.info("Tidak ada data setoran harian.")

                with col_adm2:
                    with st.container(border=True):
                        st.markdown("##### 🗑️ Hapus Record Tasmi'")
                        if not df_tasmi.empty:
                            tasmi_to_delete = st.selectbox(
                                "Pilih Record Tasmi':",
                                df_tasmi.index.tolist(),
                                format_func=lambda x: f"{df_tasmi.loc[x, 'Tanggal']} | {df_tasmi.loc[x, 'Nama Murid'].split(' - ')[0]} | {df_tasmi.loc[x, 'Rentang Surah']}"
                            )
                            if st.button("🚨 Hapus Record Tasmi'", type="primary", use_container_width=True, key="btn_del_tasmi"):
                                df_tasmi_updated = df_tasmi.drop(index=tasmi_to_delete).reset_index(drop=True)
                                save_tasmi_data(df_tasmi_updated)
                                st.toast("Record Tasmi' berhasil dihapus.", icon="🗑️")
                                st.rerun()
                        else:
                            st.info("Tidak ada data ujian Tasmi'.")

                st.write("")
                if st.button("🔒 Kunci Kembali Panel Admin", use_container_width=True):
                    st.session_state["admin_board_unlocked"] = False
                    st.rerun()
