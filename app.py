import base64
import datetime
import hmac
import html
import io
import json
import math
import os
import sqlite3
from contextlib import closing, contextmanager
from importlib.metadata import version as pkg_version
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================================
# AKUN LOGIN BAWAAN — dipakai jika .streamlit/secrets.toml tidak ada
# ============================================================================
BUILTIN_CONFIG = {
    "admin_passkey": "11333356",
    "admins": ["adnanputra@iqis.sch.id", "muh294@admin.smp.belajar.id"],
    "users": {
        "adnanputra@iqis.sch.id": "Tahfizsmp8!",
        "muh294@admin.smp.belajar.id": "Tahfizsmp8!",
        "mohfaizgufran@iqis.sch.id": "Tahfizsmp8!",
        "rafly@iqis.sch.id": "Tahfizsmp8!",
        "bagusammar@iqis.sch.id": "Tahfizsmp8!",
        "huzaifah@iqis.sch.id": "Tahfizsmp8!",
    },
    "nama_guru": {
        "adnanputra@iqis.sch.id": "UST. Achmad Adnan P.H.",
        "mohfaizgufran@iqis.sch.id": "UST. Moh. Faiz Gufran, S.H.",
        "rafly@iqis.sch.id": "UST. Muhammad Rafly Rifadillah",
        "bagusammar@iqis.sch.id": "UST. Muhammad Bagus Ammar",
        "huzaifah@iqis.sch.id": "UST. Hudzaifah",
    },
}

# ============================================================================
# KONFIGURASI NAMA & FILE
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def path(name):
    return os.path.join(BASE_DIR, name)

DB_FILE = os.environ.get("TAHFIDZ_DB", path("tahfidz_track.db"))
LEGACY_SETORAN_CSV = path("tahfidz_track_data.csv")
LEGACY_TASMI_CSV = path("tahfidz_tasmi_data.csv")
LOGO_PATH = path("WhatsApp Image 2026-09-12 at 10.04.17 AM.jpeg")
HEADER_BG_PATH = path("WhatsApp Image 2026-09-16 at 1.57.59 PM.jpeg")
KEPALA_SEKOLAH = "Arief Rahman Syarif, S.Kom., Gr., S.Pd."

JENIS_SETORAN = ["Sabaq", "Murajaah", "Manzil"]
DAFTAR_MUHAFFIDZ = [
    "UST. Rijal, S.Pd.I.",
    "UST. Hudzaifah",
    "UST. Moh. Faiz Gufran, S.H.",
    "UST. Achmad Adnan P.H.",
    "UST. Muhammad Bagus Ammar",
    "UST. Luthfi Dwi Hatmadja Sudiro",
    "UST. Muhammad Rafly Rifadillah",
]

KOORDINATOR_KELAS = {
    "KELAS VII A": "UST. Rijal, S.Pd.I.",
    "KELAS VIIIA": "UST. Moh. Faiz Gufran, S.H.",
    "KELAS IX A": "UST. Hudzaifah",
}
KOORDINATOR_DEFAULT = "UST. Achmad Adnan P.H."

MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Makassar")
except Exception:
    TZ = datetime.timezone(datetime.timedelta(hours=8))

TS_FMT = "%Y-%m-%d %H:%M:%S"

def now_wita():
    return datetime.datetime.now(TZ)

def today_wita():
    return now_wita().date()

def ts_now():
    return now_wita().strftime(TS_FMT)

def naive_now():
    return now_wita().replace(tzinfo=None)

def tanggal_indonesia(d):
    return f"{d.day} {MONTHS_ID[d.month - 1]} {d.year}"

# ----------------------------------------------------------------------------
# DATA REFERENSI MURID & SURAH
# ----------------------------------------------------------------------------
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
        "Zidan Arkana - 2510309",
        "Sultan Asshiddiq - 2510379",
        "Muhammad Fauzan Arief Raaka - 2610457",
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

SURAH_DATA = {
    "1. Al-Fatihah": {"ayat": 7, "juz": "1"},
    "2. Al-Baqarah": {"ayat": 286, "juz": "1-3"},
    "3. Ali 'Imran": {"ayat": 200, "juz": "3-4"},
    "4. An-Nisa'": {"ayat": 176, "juz": "4-6"},
    "5. Al-Ma'idah": {"ayat": 120, "juz": "6-7"},
    "6. Al-An'am": {"ayat": 165, "juz": "7-8"},
    "7. Al-A'raf": {"ayat": 206, "juz": "8-9"},
    "8. Al-Anfal": {"ayat": 75, "juz": "9-10"},
    "9. At-Taubah": {"ayat": 129, "juz": "10-11"},
    "10. Yunus": {"ayat": 109, "juz": "11"},
    "11. Hud": {"ayat": 123, "juz": "11-12"},
    "12. Yusuf": {"ayat": 111, "juz": "12-13"},
    "13. Ar-Ra'd": {"ayat": 43, "juz": "13"},
    "14. Ibrahim": {"ayat": 52, "juz": "13"},
    "15. Al-Hijr": {"ayat": 99, "juz": "14"},
    "16. An-Nahl": {"ayat": 128, "juz": "14"},
    "17. Al-Isra'": {"ayat": 111, "juz": "15"},
    "18. Al-Kahf": {"ayat": 110, "juz": "15-16"},
    "19. Maryam": {"ayat": 98, "juz": "16"},
    "20. Taha": {"ayat": 135, "juz": "16"},
    "21. Al-Anbiya'": {"ayat": 112, "juz": "17"},
    "22. Al-Hajj": {"ayat": 78, "juz": "17"},
    "23. Al-Mu'minun": {"ayat": 118, "juz": "18"},
    "24. An-Nur": {"ayat": 64, "juz": "18"},
    "25. Al-Furqan": {"ayat": 77, "juz": "18-19"},
    "26. Asy-Syu'ara'": {"ayat": 227, "juz": "19"},
    "27. An-Naml": {"ayat": 93, "juz": "19-20"},
    "28. Al-Qasas": {"ayat": 88, "juz": "20"},
    "29. Al-'Ankabut": {"ayat": 69, "juz": "20-21"},
    "30. Ar-Rum": {"ayat": 60, "juz": "21"},
    "31. Luqman": {"ayat": 34, "juz": "21"},
    "32. As-Sajdah": {"ayat": 30, "juz": "21"},
    "33. Al-Ahzab": {"ayat": 73, "juz": "21-22"},
    "34. Saba'": {"ayat": 54, "juz": "22"},
    "35. Fatir": {"ayat": 45, "juz": "22"},
    "36. Yasin": {"ayat": 83, "juz": "22-23"},
    "37. As-Saffat": {"ayat": 182, "juz": "23"},
    "38. Sad": {"ayat": 88, "juz": "23"},
    "39. Az-Zumar": {"ayat": 75, "juz": "23-24"},
    "40. Ghafir": {"ayat": 85, "juz": "24"},
    "41. Fussilat": {"ayat": 54, "juz": "24-25"},
    "42. Asy-Syura": {"ayat": 53, "juz": "25"},
    "43. Az-Zukhruf": {"ayat": 89, "juz": "25"},
    "44. Ad-Dukhan": {"ayat": 59, "juz": "25"},
    "45. Al-Jasiyah": {"ayat": 37, "juz": "25"},
    "46. Al-Ahqaf": {"ayat": 35, "juz": "26"},
    "47. Muhammad": {"ayat": 38, "juz": "26"},
    "48. Al-Fath": {"ayat": 29, "juz": "26"},
    "49. Al-Hujurat": {"ayat": 18, "juz": "26"},
    "50. Qaf": {"ayat": 45, "juz": "26"},
    "51. Az-Zariyat": {"ayat": 60, "juz": "26-27"},
    "52. At-Tur": {"ayat": 49, "juz": "27"},
    "53. An-Najm": {"ayat": 62, "juz": "27"},
    "54. Al-Qamar": {"ayat": 55, "juz": "27"},
    "55. Ar-Rahman": {"ayat": 78, "juz": "27"},
    "56. Al-Waqi'ah": {"ayat": 96, "juz": "27"},
    "57. Al-Hadid": {"ayat": 29, "juz": "27"},
    "58. Al-Mujadilah": {"ayat": 22, "juz": "28"},
    "59. Al-Hasyr": {"ayat": 24, "juz": "28"},
    "60. Al-Mumtahanah": {"ayat": 13, "juz": "28"},
    "61. As-Saff": {"ayat": 14, "juz": "28"},
    "62. Al-Jumu'ah": {"ayat": 11, "juz": "28"},
    "63. Al-Munafiqun": {"ayat": 11, "juz": "28"},
    "64. At-Taghabun": {"ayat": 18, "juz": "28"},
    "65. At-Talaq": {"ayat": 12, "juz": "28"},
    "66. At-Tahrim": {"ayat": 12, "juz": "28"},
    "67. Al-Mulk": {"ayat": 30, "juz": "29"},
    "68. Al-Qalam": {"ayat": 52, "juz": "29"},
    "69. Al-Haqqah": {"ayat": 52, "juz": "29"},
    "70. Al-Ma'arij": {"ayat": 44, "juz": "29"},
    "71. Nuh": {"ayat": 28, "juz": "29"},
    "72. Al-Jinn": {"ayat": 28, "juz": "29"},
    "73. Al-Muzzammil": {"ayat": 20, "juz": "29"},
    "74. Al-Muddassir": {"ayat": 56, "juz": "29"},
    "75. Al-Qiyamah": {"ayat": 40, "juz": "29"},
    "76. Al-Insan": {"ayat": 31, "juz": "29"},
    "77. Al-Mursalat": {"ayat": 50, "juz": "29"},
    "78. An-Naba'": {"ayat": 40, "juz": "30"},
    "79. An-Nazi'at": {"ayat": 46, "juz": "30"},
    "80. 'Abasa": {"ayat": 42, "juz": "30"},
    "81. At-Takwir": {"ayat": 29, "juz": "30"},
    "82. Al-Infitar": {"ayat": 19, "juz": "30"},
    "83. Al-Mutaffifin": {"ayat": 36, "juz": "30"},
    "84. Al-Inshiqaq": {"ayat": 25, "juz": "30"},
    "85. Al-Buruj": {"ayat": 22, "juz": "30"},
    "86. At-Tariq": {"ayat": 17, "juz": "30"},
    "87. Al-A'la": {"ayat": 19, "juz": "30"},
    "88. Al-Ghasyiyah": {"ayat": 26, "juz": "30"},
    "89. Al-Fajr": {"ayat": 30, "juz": "30"},
    "90. Al-Balad": {"ayat": 20, "juz": "30"},
    "91. Asy-Syams": {"ayat": 15, "juz": "30"},
    "92. Al-Lail": {"ayat": 21, "juz": "30"},
    "93. Ad-Duha": {"ayat": 11, "juz": "30"},
    "94. Asy-Syarh": {"ayat": 8, "juz": "30"},
    "95. At-Tin": {"ayat": 8, "juz": "30"},
    "96. Al-'Alaq": {"ayat": 19, "juz": "30"},
    "97. Al-Qadr": {"ayat": 5, "juz": "30"},
    "98. Al-Bayyinah": {"ayat": 8, "juz": "30"},
    "99. Az-Zalzalah": {"ayat": 8, "juz": "30"},
    "100. Al-'Adiyat": {"ayat": 11, "juz": "30"},
    "101. Al-Qari'ah": {"ayat": 11, "juz": "30"},
    "102. At-Takasur": {"ayat": 8, "juz": "30"},
    "103. Al-'Asr": {"ayat": 3, "juz": "30"},
    "104. Al-Humazah": {"ayat": 9, "juz": "30"},
    "105. Al-Fil": {"ayat": 5, "juz": "30"},
    "106. Quraisy": {"ayat": 4, "juz": "30"},
    "107. Al-Ma'un": {"ayat": 7, "juz": "30"},
    "108. Al-Kausar": {"ayat": 3, "juz": "30"},
    "109. Al-Kafirun": {"ayat": 6, "juz": "30"},
    "110. An-Nasr": {"ayat": 3, "juz": "30"},
    "111. Al-Lahab": {"ayat": 5, "juz": "30"},
    "112. Al-Ikhlas": {"ayat": 4, "juz": "30"},
    "113. Al-Falaq": {"ayat": 5, "juz": "30"},
    "114. An-Nas": {"ayat": 6, "juz": "30"},
}

def split_murid(full):
    parts = full.split(" - ")
    return parts[0], (parts[1] if len(parts) > 1 else "-")

def nilai_setoran(salah):
    return max(0.0, min(100.0, round(100.0 - salah * 2.0, 2)))

def nilai_tasmi(err_besar, err_kecil):
    return max(0.0, min(100.0, round(100.0 - err_besar * 2.0 - err_kecil * 0.5, 2)))

def predikat(nilai):
    if nilai >= 90: return "Mumtaz (Sangat Baik)"
    if nilai >= 75: return "Jayyid Jiddan (Baik)"
    if nilai >= 60: return "Jayyid (Cukup)"
    return "Rasib (Perlu Murajaah)"

# ----------------------------------------------------------------------------
# DATABASE SQLITE
# ----------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS setoran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL, guru_input TEXT, kelas TEXT NOT NULL,
    nama_murid TEXT NOT NULL, juz TEXT, jenis TEXT, surah TEXT,
    ayat_awal INTEGER, ayat_akhir INTEGER, halaman REAL, salah INTEGER,
    nilai REAL, dibuat_oleh TEXT, dibuat_pada TEXT
);
CREATE INDEX IF NOT EXISTS idx_setoran_murid ON setoran(kelas, nama_murid);
CREATE TABLE IF NOT EXISTS tasmi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL, periode TEXT, kelas TEXT NOT NULL,
    nama_murid TEXT NOT NULL, penguji TEXT, rentang_surah TEXT,
    err_besar INTEGER, err_kecil INTEGER, nilai_akhir REAL, catatan TEXT,
    dibuat_oleh TEXT, dibuat_pada TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasmi_murid ON tasmi(kelas, nama_murid);
CREATE TABLE IF NOT EXISTS sessions (
    email TEXT PRIMARY KEY, status TEXT, last_active TEXT, login_time TEXT
);
CREATE TABLE IF NOT EXISTS login_attempts (
    email TEXT PRIMARY KEY, fails INTEGER, locked_until TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TEXT, email TEXT, aksi TEXT, detail TEXT
);
"""

def connect():
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.execute("PRAGMA busy_timeout=15000")
    return conn

@contextmanager
def tx():
    conn = connect()
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def _t(v, default=""):
    try:
        if pd.isna(v): return default
    except (TypeError, ValueError): pass
    return str(v)

def _f(v, default=0.0):
    try:
        return default if pd.isna(v) else float(v)
    except (TypeError, ValueError): return default

def _i(v, default=0):
    return int(round(_f(v, default)))

def init_db():
    with closing(connect()) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
    migrate_csv()

def migrate_csv():
    with closing(connect()) as conn:
        n_set = conn.execute("SELECT COUNT(*) FROM setoran").fetchone()[0]
        n_tas = conn.execute("SELECT COUNT(*) FROM tasmi").fetchone()[0]

    if n_set == 0 and os.path.exists(LEGACY_SETORAN_CSV):
        df = pd.read_csv(LEGACY_SETORAN_CSV, dtype={"Juz": str})
        df = df.rename(columns={"Nama Santri": "Nama Murid"})
        if "Juz" not in df.columns: df["Juz"] = "-"
        rows = [
            (
                _t(r.get("Tanggal")), _t(r.get("Guru Input")), _t(r.get("Kelas")),
                _t(r.get("Nama Murid")), _t(r.get("Juz"), "-"), _t(r.get("Jenis Setoran")),
                _t(r.get("Surah")).replace("8. At-Taubah", "9. At-Taubah"),
                _i(r.get("Ayat Awal")), _i(r.get("Ayat Akhir")), _f(r.get("Halaman")),
                _i(r.get("Salah")), _f(r.get("Nilai")), "migrasi-csv", ts_now(),
            ) for r in df.to_dict("records")
        ]
        with tx() as conn:
            conn.executemany(
                "INSERT INTO setoran(tanggal,guru_input,kelas,nama_murid,juz,jenis,surah,"
                "ayat_awal,ayat_akhir,halaman,salah,nilai,dibuat_oleh,dibuat_pada) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows,
            )

    if n_tas == 0 and os.path.exists(LEGACY_TASMI_CSV):
        df = pd.read_csv(LEGACY_TASMI_CSV)
        rows = [
            (
                _t(r.get("Tanggal")), _t(r.get("Periode")), _t(r.get("Kelas")),
                _t(r.get("Nama Murid")), _t(r.get("Penguji")), _t(r.get("Rentang Surah")),
                _i(r.get("Err Besar")), _i(r.get("Err Kecil")), _f(r.get("Nilai Akhir")),
                _t(r.get("Catatan")), "migrasi-csv", ts_now(),
            ) for r in df.to_dict("records")
        ]
        with tx() as conn:
            conn.executemany(
                "INSERT INTO tasmi(tanggal,periode,kelas,nama_murid,penguji,rentang_surah,"
                "err_besar,err_kecil,nilai_akhir,catatan,dibuat_oleh,dibuat_pada) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", rows,
            )

SETORAN_SELECT = (
    'SELECT id AS ID, tanggal AS Tanggal, guru_input AS "Guru Input", kelas AS Kelas, '
    'nama_murid AS "Nama Murid", juz AS Juz, jenis AS "Jenis Setoran", surah AS Surah, '
    'ayat_awal AS "Ayat Awal", ayat_akhir AS "Ayat Akhir", halaman AS Halaman, '
    'salah AS Salah, nilai AS Nilai, dibuat_oleh AS "Dibuat Oleh" FROM setoran'
)
TASMI_SELECT = (
    'SELECT id AS ID, tanggal AS Tanggal, periode AS Periode, kelas AS Kelas, '
    'nama_murid AS "Nama Murid", penguji AS Penguji, rentang_surah AS "Rentang Surah", '
    'err_besar AS "Err Besar", err_kecil AS "Err Kecil", nilai_akhir AS "Nilai Akhir", '
    'catatan AS Catatan, dibuat_oleh AS "Dibuat Oleh" FROM tasmi'
)

def _read(select_sql, kelas=None, murid=None):
    where, params = [], []
    if kelas:
        where.append("kelas = ?")
        params.append(kelas)
    if murid:
        where.append("nama_murid = ?")
        params.append(murid)
    sql = select_sql + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY tanggal, id"
    with closing(connect()) as conn:
        return pd.read_sql_query(sql, conn, params=params)

def get_setoran(kelas=None, murid=None): return _read(SETORAN_SELECT, kelas, murid)
def get_tasmi(kelas=None, murid=None): return _read(TASMI_SELECT, kelas, murid)

def setoran_exists(rec):
    with closing(connect()) as conn:
        row = conn.execute(
            "SELECT 1 FROM setoran WHERE tanggal=? AND nama_murid=? AND jenis=? "
            "AND surah=? AND ayat_awal=? AND ayat_akhir=? LIMIT 1",
            (rec["tanggal"], rec["nama_murid"], rec["jenis"], rec["surah"],
             rec["ayat_awal"], rec["ayat_akhir"]),
        ).fetchone()
    return row is not None

def insert_setoran(rec, email):
    with tx() as conn:
        conn.execute(
            "INSERT INTO setoran(tanggal,guru_input,kelas,nama_murid,juz,jenis,surah,"
            "ayat_awal,ayat_akhir,halaman,salah,nilai,dibuat_oleh,dibuat_pada) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rec["tanggal"], rec["guru_input"], rec["kelas"], rec["nama_murid"], rec["juz"],
             rec["jenis"], rec["surah"], rec["ayat_awal"], rec["ayat_akhir"], rec["halaman"],
             rec["salah"], rec["nilai"], email, ts_now()),
        )

def tasmi_exists(rec):
    with closing(connect()) as conn:
        row = conn.execute(
            "SELECT 1 FROM tasmi WHERE tanggal=? AND periode=? AND nama_murid=? "
            "AND rentang_surah=? AND err_besar=? AND err_kecil=? LIMIT 1",
            (rec["tanggal"], rec["periode"], rec["nama_murid"], rec["rentang_surah"],
             rec["err_besar"], rec["err_kecil"]),
        ).fetchone()
    return row is not None

def insert_tasmi(rec, email):
    with tx() as conn:
        conn.execute(
            "INSERT INTO tasmi(tanggal,periode,kelas,nama_murid,penguji,rentang_surah,"
            "err_besar,err_kecil,nilai_akhir,catatan,dibuat_oleh,dibuat_pada) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (rec["tanggal"], rec["periode"], rec["kelas"], rec["nama_murid"], rec["penguji"],
             rec["rentang_surah"], rec["err_besar"], rec["err_kecil"], rec["nilai_akhir"],
             rec["catatan"], email, ts_now()),
        )

def delete_record(table, record_id, admin_email):
    assert table in ("setoran", "tasmi")
    with tx() as conn:
        cur = conn.execute(f"SELECT * FROM {table} WHERE id=?", (record_id,))
        row = cur.fetchone()
        if row is None: return False
        cols = [d[0] for d in cur.description]
        conn.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
    log_audit(admin_email, f"hapus_{table}", json.dumps(dict(zip(cols, row)), ensure_ascii=False))
    return True

def log_audit(email, aksi, detail=""):
    with tx() as conn:
        conn.execute(
            "INSERT INTO audit_log(waktu,email,aksi,detail) VALUES(?,?,?,?)",
            (ts_now(), email, aksi, detail),
        )

def get_audit(limit=50):
    with closing(connect()) as conn:
        return pd.read_sql_query(
            "SELECT waktu AS Waktu, email AS Email, aksi AS Aksi, detail AS Detail "
            "FROM audit_log ORDER BY id DESC LIMIT ?",
            conn, params=[limit],
        )

ONLINE_WINDOW_MIN = 15
MAX_FAILS = 5
LOCK_MINUTES = 5

def touch_session(email, new_login=False):
    now = ts_now()
    with tx() as conn:
        if new_login:
            conn.execute(
                "INSERT INTO sessions(email,status,last_active,login_time) VALUES(?,?,?,?) "
                "ON CONFLICT(email) DO UPDATE SET status='online', last_active=excluded.last_active, "
                "login_time=excluded.login_time", (email, "online", now, now),
            )
        else:
            conn.execute("UPDATE sessions SET status='online', last_active=? WHERE email=?", (now, email))

def end_session(email):
    with tx() as conn:
        conn.execute("UPDATE sessions SET status='offline', last_active=? WHERE email=?", (ts_now(), email))

def get_sessions():
    with closing(connect()) as conn:
        rows = conn.execute("SELECT email,status,last_active,login_time FROM sessions ORDER BY last_active DESC").fetchall()
    now = naive_now()
    out = []
    for email, status, last_active, login_time in rows:
        online = False
        if status == "online" and last_active:
            try:
                age = (now - datetime.datetime.strptime(last_active, TS_FMT)).total_seconds()
                online = age <= ONLINE_WINDOW_MIN * 60
            except ValueError: pass
        out.append({
            "Email Guru": email, "Status": "Online 🟢" if online else "Offline 🔴",
            "Aktivitas Terakhir": last_active, "Waktu Login": login_time,
        })
    return pd.DataFrame(out, columns=["Email Guru", "Status", "Aktivitas Terakhir", "Waktu Login"])

def lock_remaining_seconds(email):
    with closing(connect()) as conn:
        row = conn.execute("SELECT locked_until FROM login_attempts WHERE email=?", (email,)).fetchone()
    if not row or not row[0]: return 0
    try: until = datetime.datetime.strptime(row[0], TS_FMT)
    except ValueError: return 0
    return max(0, int((until - naive_now()).total_seconds()))

def register_failed_login(email):
    with tx() as conn:
        row = conn.execute("SELECT fails FROM login_attempts WHERE email=?", (email,)).fetchone()
        fails = (row[0] if row else 0) + 1
        locked = None
        if fails >= MAX_FAILS:
            locked = (naive_now() + datetime.timedelta(minutes=LOCK_MINUTES)).strftime(TS_FMT)
            fails = 0
        conn.execute(
            "INSERT INTO login_attempts(email,fails,locked_until) VALUES(?,?,?) "
            "ON CONFLICT(email) DO UPDATE SET fails=excluded.fails, locked_until=excluded.locked_until",
            (email, fails, locked),
        )
    return locked is not None

def clear_failed_logins(email):
    with tx() as conn:
        conn.execute("DELETE FROM login_attempts WHERE email=?", (email,))

def build_rekap(df, nama_kelas):
    rows = []
    for idx, full in enumerate(DATABASE_MURID.get(nama_kelas, []), 1):
        nama, nis = split_murid(full)
        d = df[(df["Kelas"] == nama_kelas) & (df["Nama Murid"] == full)]
        if d.empty:
            rows.append({"No": idx, "NIS": nis, "Nama Lengkap": nama, "Jumlah Setoran": 0,
                         "Total Halaman": 0.0, "Rata-Rata Nilai": 0.0,
                         "Setoran Terakhir": "-", "Surah Terakhir": "-"})
            continue
        last = d.sort_values(["Tanggal", "ID"]).iloc[-1]
        rows.append({"No": idx, "NIS": nis, "Nama Lengkap": nama, "Jumlah Setoran": len(d),
                     "Total Halaman": round(float(d["Halaman"].sum()), 2),
                     "Rata-Rata Nilai": round(float(d["Nilai"].mean()), 2),
                     "Setoran Terakhir": last["Tanggal"], "Surah Terakhir": last["Surah"]})
    return pd.DataFrame(rows)

def build_detail_matrix(df, nama_kelas, n_terakhir=10):
    rows = []
    for idx, full in enumerate(DATABASE_MURID.get(nama_kelas, []), 1):
        nama, nis = split_murid(full)
        d = df[(df["Kelas"] == nama_kelas) & (df["Nama Murid"] == full)].sort_values(["Tanggal", "ID"])
        d = d.tail(n_terakhir).reset_index(drop=True)
        row = {"No": idx, "NIS": nis, "Nama Lengkap": nama}
        for k in range(n_terakhir):
            if k < len(d):
                row[f"S{k + 1} Tanggal"] = d.loc[k, "Tanggal"]
                row[f"S{k + 1} Surah"] = d.loc[k, "Surah"]
                row[f"S{k + 1} Nilai"] = float(d.loc[k, "Nilai"])
            else:
                row[f"S{k + 1} Tanggal"] = row[f"S{k + 1} Surah"] = row[f"S{k + 1} Nilai"] = "-"
        rows.append(row)
    return pd.DataFrame(rows)

def build_tasmi_matrix(df, nama_kelas, maks=10):
    rows = []
    for idx, full in enumerate(DATABASE_MURID.get(nama_kelas, []), 1):
        nama, nis = split_murid(full)
        d = df[(df["Kelas"] == nama_kelas) & (df["Nama Murid"] == full)].sort_values(["Tanggal", "ID"])
        d = d.reset_index(drop=True)
        row = {"No": idx, "NIS": nis, "Nama Lengkap": nama,
               "Status": "Sudah Tasmi'" if not d.empty else "Belum Tasmi'"}
        scores = []
        for k in range(maks):
            if k < len(d):
                row[f"Tasmi' {k + 1} - Surah"] = _t(d.loc[k, "Rentang Surah"], "-")
                row[f"Tasmi' {k + 1} - Err Besar"] = _i(d.loc[k, "Err Besar"])
                row[f"Tasmi' {k + 1} - Err Kecil"] = _i(d.loc[k, "Err Kecil"])
                row[f"Tasmi' {k + 1} - Nilai"] = _f(d.loc[k, "Nilai Akhir"])
                scores.append(_f(d.loc[k, "Nilai Akhir"]))
            else:
                for suf in ("Surah", "Err Besar", "Err Kecil", "Nilai"):
                    row[f"Tasmi' {k + 1} - {suf}"] = "-"
        row["Rata-Rata Tasmi'"] = round(sum(scores) / len(scores), 2) if scores else 0.0
        rows.append(row)
    return pd.DataFrame(rows)

def generate_pdf(df, periode, nama_kelas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=24, bottomMargin=24,
        title=f"Laporan Tahfidz {nama_kelas} {periode}", author="TahfidzTrack",
    )
    olive, sage, bone, moss, cocoa = (colors.HexColor(c) for c in ("#2F3A2E", "#8E9A86", "#ECE7DC", "#BBC7A4", "#5D4538"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Heading1"], fontName="Helvetica-Bold",
                                 fontSize=13, textColor=olive, alignment=1, spaceAfter=4)
    sub_style = ParagraphStyle("S", parent=styles["Normal"], fontName="Helvetica-Bold",
                               fontSize=10, textColor=cocoa, alignment=1, spaceAfter=14)
    section_style = ParagraphStyle("Sec", parent=styles["Normal"], fontName="Helvetica-Bold",
                                   fontSize=9.5, textColor=olive, spaceAfter=4)
    cell = ParagraphStyle("C", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=9)
    cell_c = ParagraphStyle("CC", parent=cell, alignment=1)
    head = ParagraphStyle("H", parent=cell, fontName="Helvetica-Bold", fontSize=8, textColor=bone, alignment=1)
    bold = ParagraphStyle("B", parent=styles["Normal"], fontName="Helvetica-Bold")

    def p(text, style=cell): return Paragraph(escape(str(text)), style)

    def table_style():
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), olive),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [bone, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, moss),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])

    elements = []
    if os.path.exists(LOGO_PATH):
        try:
            img = RLImage(LOGO_PATH, width=50, height=50)
            img.hAlign = "CENTER"
            elements += [img, Spacer(1, 6)]
        except Exception: pass

    elements.append(Paragraph("LAPORAN REKAPITULASI BULANAN TAHFIDZ QURAN", title_style))
    elements.append(Paragraph(escape(f"SMPIT IBNUL QAYYIM MAKASSAR — {nama_kelas} | Periode: {periode}"), sub_style))

    df = df.reset_index(drop=True)
    data = [[p(h, head) for h in ["No", "Tanggal", "Nama Murid", "Jenis", "Surah (Ayat)", "Hlm", "Nilai"]]]
    for i, r in df.iterrows():
        data.append([
            p(i + 1, cell_c), p(r["Tanggal"], cell_c), p(split_murid(str(r["Nama Murid"]))[0]),
            p(r["Jenis Setoran"], cell_c), p(f"{r['Surah']} ({_i(r['Ayat Awal'])}-{_i(r['Ayat Akhir'])})"),
            p(f"{_f(r['Halaman']):g}", cell_c), p(f"{_f(r['Nilai']):g}", cell_c),
        ])
    t = Table(data, colWidths=[24, 58, 140, 52, 148, 45, 48], repeatRows=1)
    t.setStyle(table_style())
    elements += [t, Spacer(1, 16)]

    elements.append(Paragraph("Ringkasan per Murid", section_style))
    summ = [[p(h, head) for h in ["No", "Nama Murid", "Jumlah Setoran", "Total Halaman", "Rata-Rata Nilai"]]]
    grp = df.groupby("Nama Murid").agg(n=("ID", "count"), hlm=("Halaman", "sum"), nilai=("Nilai", "mean"))
    for i, (full, row) in enumerate(grp.sort_index().iterrows(), 1):
        summ.append([p(i, cell_c), p(split_murid(str(full))[0]), p(int(row["n"]), cell_c),
                     p(f"{row['hlm']:g}", cell_c), p(f"{row['nilai']:.2f}", cell_c)])
    st_ = Table(summ, colWidths=[30, 230, 85, 85, 85], repeatRows=1)
    st_.setStyle(table_style())
    elements += [st_, Spacer(1, 22)]

    koordinator = KOORDINATOR_KELAS.get(nama_kelas, KOORDINATOR_DEFAULT)
    ttd = Table(
        [
            [Paragraph("Mengetahui,", styles["Normal"]), "", Paragraph(f"Makassar, {tanggal_indonesia(today_wita())}", styles["Normal"])],
            [Paragraph("Kepala Sekolah SMPIT Ibnul Qayyim", styles["Normal"]), "", Paragraph("Koordinator Tahfidz Kelas", styles["Normal"])],
            ["", "", ""],
            ["", "", ""],
            [Paragraph(escape(KEPALA_SEKOLAH), bold), "", Paragraph(escape(koordinator), bold)],
        ],
        colWidths=[220, 60, 220],
    )
    ttd.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(KeepTogether(ttd))

    doc.build(elements)
    return buffer.getvalue()

# ============================================================================
# TAMPILAN (Streamlit)
# ============================================================================
st.set_page_config(
    page_title="TahfidzTrack — SMPIT Ibnul Qayyim",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def _st_version():
    try: return tuple(int(x) for x in pkg_version("streamlit").split(".")[:2])
    except Exception: return (0, 0)

STRETCH = {"width": "stretch"} if _st_version() >= (1, 50) else {"use_container_width": True}

def load_config():
    try:
        users = {str(k).strip().lower(): str(v) for k, v in dict(st.secrets["users"]).items()}
        admins = {str(a).strip().lower() for a in st.secrets["admins"]}
        passkey = str(st.secrets["admin_passkey"])
        try: nama_guru = {str(k).strip().lower(): str(v) for k, v in dict(st.secrets["nama_guru"]).items()}
        except Exception: nama_guru = {}
        return {"users": users, "admins": admins, "passkey": passkey, "nama_guru": nama_guru, "builtin": False}
    except Exception:
        b = BUILTIN_CONFIG
        return {"users": dict(b["users"]), "admins": set(b["admins"]), "passkey": b["admin_passkey"],
                "nama_guru": dict(b["nama_guru"]), "builtin": True}

def safe_equal(a, b):
    return hmac.compare_digest(str(a).encode("utf-8"), str(b).encode("utf-8"))

@st.cache_resource(show_spinner=False)
def img_src(file_path, max_px):
    if not os.path.exists(file_path): return ""
    try:
        from PIL import Image
        im = Image.open(file_path).convert("RGB")
        im.thumbnail((max_px, max_px))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=78, optimize=True)
        data = buf.getvalue()
    except Exception:
        with open(file_path, "rb") as f: data = f.read()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")

# ----------------------------------------------------------------------------
# CSS TEMA CERAH (BACKGROUND #E5E4E2 & KONTRASTING TEXT)
# ----------------------------------------------------------------------------
CSS = """
<style>
:root {
  --bg-main: #E5E4E2;
  --dark-text: #1E293B;
  --olive-primary: #2F3A2E;
  --card-white: #FFFFFF;
  --sub-text: #475569;
  --border-color: #CBD5E1;
}

@keyframes fadeIn { 0% { opacity: 0; transform: translateY(12px); } 100% { opacity: 1; transform: translateY(0); } }

/* Main App Container */
.stApp {
  background-color: var(--bg-main) !important;
  color: var(--dark-text) !important;
}

.stMainBlockContainer {
  animation: fadeIn 0.4s ease-out;
  padding-top: 1.5rem !important;
}

/* Typography Overrides */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMetricLabel"] p,
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stCheckbox"] p {
  color: var(--dark-text) !important;
}

.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {
  color: var(--sub-text) !important;
}

/* Modern Header Box */
.main-header {
  background: #FFFFFF;
  padding: 22px;
  border-radius: 16px;
  margin-bottom: 24px;
  text-align: center;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.main-header h1 {
  font-size: 26px !important;
  font-weight: 800 !important;
  color: var(--olive-primary) !important;
  margin: 10px 0 2px 0 !important;
}
.main-header p {
  font-size: 13.5px;
  color: var(--sub-text) !important;
  font-weight: 600;
}

/* Category Title */
.category-header {
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #64748B;
  margin: 22px 0 10px 2px;
}

/* Cards & Containers */
.card-box, div[data-testid="stForm"] {
  background: var(--card-white) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 16px !important;
  padding: 20px !important;
  margin-bottom: 16px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
}

/* Custom Grid Menu Card UI */
.grid-card-body {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  box-shadow: 0 4px 14px rgba(0,0,0,0.04);
  transition: all 0.25s ease;
  min-height: 170px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.grid-card-icon-bg {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  margin-bottom: 10px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
.grid-card-title {
  font-size: 16px;
  font-weight: 800;
  color: #1E293B;
  margin-bottom: 4px;
}
.grid-card-desc {
  font-size: 12px;
  color: #64748B;
  line-height: 1.35;
  margin-bottom: 12px;
}

/* Inputs & Form Controls */
div[data-baseweb="input"]>div, div[data-baseweb="select"]>div, div[data-baseweb="textarea"]>div {
  background-color: #FFFFFF !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 10px !important;
}
div[data-baseweb="select"] *, div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
  color: var(--dark-text) !important;
}

/* Buttons Styling */
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"]>button {
  background: var(--olive-primary) !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 10px 18px !important;
  box-shadow: 0 4px 12px rgba(47,58,46,0.2) !important;
  transition: all 0.2s ease !important;
}
.stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover {
  background: #3B4A3A !important;
  transform: translateY(-2px);
}

/* Custom Badges */
.badge-success { background: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #BBF7D0; }
.badge-admin { background: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #FDE68A; }
</style>
"""

def render_header(title, subtitle):
    logo = img_src(LOGO_PATH, 160)
    logo_tag = f'<img src="{logo}" width="65" style="border-radius:50%;background:#FFFFFF;padding:3px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">' if logo else ""
    st.markdown(
        f'<div class="main-header">{logo_tag}<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )

def kpi(label, value):
    return (f'<div class="card-box" style="text-align:center;"><div style="font-size:12px;font-weight:700;color:#64748B;text-transform:uppercase;">{html.escape(label)}</div>'
            f'<div style="font-size:26px;font-weight:800;color:#1E293B;margin-top:4px;">{html.escape(str(value))}</div></div>')

def metric_box(label, value, small=False):
    style = ' style="font-size:20px;"' if small else ""
    return (f'<div class="card-box" style="text-align:center;background:#F8FAFC !important;"><div style="font-size:12px;font-weight:800;color:#2F3A2E;text-transform:uppercase;">{html.escape(label)}</div>'
            f'<div style="font-size:26px;font-weight:800;color:#2F3A2E;margin-top:4px;"{style}>{html.escape(str(value))}</div></div>')

def require_admin():
    if not st.session_state.get("is_admin"):
        st.error("🔒 Akses ditolak. Bagian ini khusus admin.")
        st.stop()

# ----------------------------------------------------------------------------
# COMPONENT LANDING PAGE / MENU GRID (SEPERTI DI GAMBAR)
# ----------------------------------------------------------------------------
def render_landing_dashboard(is_admin):
    st.markdown('<div class="category-header">MENU UTAMA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''
        <div class="grid-card-body">
            <div class="grid-card-icon-bg">📋</div>
            <div class="grid-card-title">Presensi Setoran</div>
            <div class="grid-card-desc">Input setoran hafalan harian santri secara real-time</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Buka Form Presensi ➔", key="btn_nav_setoran", **STRETCH):
            st.session_state["current_page"] = "✦ Presensi Setoran"
            st.rerun()

    with col2:
        st.markdown('''
        <div class="grid-card-body">
            <div class="grid-card-icon-bg">👤</div>
            <div class="grid-card-title">Tracking Portal</div>
            <div class="grid-card-desc">Pantau perkembangan & riwayat hafalan per murid</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Buka Tracking Portal ➔", key="btn_nav_tracking", **STRETCH):
            st.session_state["current_page"] = "🪶 Tracking Portal"
            st.rerun()

    st.markdown('<div class="category-header">EVALUASI & REKAP LAPORAN</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('''
        <div class="grid-card-body">
            <div class="grid-card-icon-bg">🎯</div>
            <div class="grid-card-title">Ujian Tasmi'</div>
            <div class="grid-card-desc">Form penilaian & catatan evaluasi ujian Tasmi'</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Buka Form Tasmi' ➔", key="btn_nav_tasmi", **STRETCH):
            st.session_state["current_page"] = "🎯 Ujian Tasmi'"
            st.rerun()

    with col4:
        st.markdown('''
        <div class="grid-card-body">
            <div class="grid-card-icon-bg">📊</div>
            <div class="grid-card-title">Laporan PDF</div>
            <div class="grid-card-desc">Cetak & unduh berkas rekapitulasi bulanan PDF</div>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("Buka Laporan PDF ➔", key="btn_nav_pdf", **STRETCH):
            st.session_state["current_page"] = "📜 Laporan PDF"
            st.rerun()

    if is_admin:
        st.markdown('<div class="category-header">ADMINISTRASI & DATABASE 🔒</div>', unsafe_allow_html=True)
        col5, col6, col7 = st.columns(3)
        with col5:
            st.markdown('''
            <div class="grid-card-body">
                <div class="grid-card-icon-bg">📂</div>
                <div class="grid-card-title">Database Setoran</div>
                <div class="grid-card-desc">Rekap & matriks seluruh data setoran</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Database Setoran ➔", key="btn_nav_db_s", **STRETCH):
                st.session_state["current_page"] = "◈ Database Setoran 🔒"
                st.rerun()

        with col6:
            st.markdown('''
            <div class="grid-card-body">
                <div class="grid-card-icon-bg">🗂️</div>
                <div class="grid-card-title">Database Tasmi'</div>
                <div class="grid-card-desc">Matriks evaluasi & rekap ujian Tasmi'</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Database Tasmi' ➔", key="btn_nav_db_t", **STRETCH):
                st.session_state["current_page"] = "📂 Database Tasmi' 🔒"
                st.rerun()

        with col7:
            st.markdown('''
            <div class="grid-card-body">
                <div class="grid-card-icon-bg">🛡️</div>
                <div class="grid-card-title">Admin Board</div>
                <div class="grid-card-desc">Sesi aktif, backup data CSV & audit</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Admin Board ➔", key="btn_nav_admin", **STRETCH):
                st.session_state["current_page"] = "🛡️ Admin Board"
                st.rerun()

# ----------------------------------------------------------------------------
# SUB-HALAMAN APLIKASI
# ----------------------------------------------------------------------------
def tab_setoran(cfg, email):
    st.subheader("✨ Form Input Setoran Harian")
    st.caption("Pencatatan progres hafalan harian murid secara real-time")
    surah_names = list(SURAH_DATA.keys())
    c1, c2 = st.columns(2)
    with c1:
        tanggal = st.date_input("📅 Tanggal Setoran", value=today_wita(), max_value=today_wita(), key="s_tgl")
        kelas = st.selectbox("🏛️ Rombongan Belajar", list(DATABASE_MURID.keys()), key="s_kelas")
        murid = st.selectbox("👤 Profil Murid", DATABASE_MURID[kelas], key=f"s_murid_{kelas}")
        nama_login = cfg["nama_guru"].get(email)
        idx_guru = DAFTAR_MUHAFFIDZ.index(nama_login) if nama_login in DAFTAR_MUHAFFIDZ else 0
        guru = st.selectbox("👨‍🏫 Guru Muhaffidz / Penguji", DAFTAR_MUHAFFIDZ, index=idx_guru, key="s_guru")
        jenis = st.selectbox("📌 Kategori Setoran", JENIS_SETORAN, key="s_jenis")

    with c2:
        surah = st.selectbox("🪷 Nama Surah Al-Qur'an", surah_names, index=surah_names.index("2. Al-Baqarah"), key="s_surah")
        info = SURAH_DATA[surah]
        juz = st.text_input("📖 Juz (Contoh: 30, 29, dll)", value=info["juz"], key=f"s_juz_{surah}")
        max_ayat = info["ayat"]
        st.caption(f"ℹ️ Surah **{surah}** memiliki **1 sampai {max_ayat} Ayat**.")
        opsi = list(range(1, max_ayat + 1))
        a1, a2 = st.columns(2)
        with a1: ayat_awal = st.selectbox("🧮 Ayat Awal", opsi, index=0, key=f"a_awal_{surah}")
        with a2: ayat_akhir = st.selectbox("🧮 Ayat Akhir", opsi, index=min(ayat_awal + 8, max_ayat - 1), key=f"a_akhir_{surah}")
        valid = ayat_akhir >= ayat_awal
        if not valid: st.error("⚠️ Ayat Akhir tidak boleh lebih kecil dari Ayat Awal!")
        halaman = st.number_input("📄 Volume (Halaman)", min_value=0.1, value=1.0, step=0.5, key="s_hlm")
        salah = st.number_input("⚡ Catatan Kekurangan/Bantuan", min_value=0, value=0, key="s_salah")

    nilai = nilai_setoran(salah)
    m1, m2 = st.columns(2)
    m1.markdown(metric_box("Indeks Kelancaran Hafalan", f"{nilai} / 100"), unsafe_allow_html=True)
    m2.markdown(metric_box("Predikat Evaluasi", predikat(nilai), small=True), unsafe_allow_html=True)

    if st.button("🛡️ SIMPAN RECORD SETORAN", disabled=not valid, key="btn_simpan_setoran", type="primary"):
        rec = {
            "tanggal": tanggal.strftime("%Y-%m-%d"), "guru_input": guru, "kelas": kelas,
            "nama_murid": murid, "juz": juz, "jenis": jenis, "surah": surah,
            "ayat_awal": int(ayat_awal), "ayat_akhir": int(ayat_akhir),
            "halaman": float(halaman), "salah": int(salah), "nilai": nilai,
        }
        if setoran_exists(rec): st.warning("Setoran yang identik sudah tercatat pada tanggal tersebut.")
        else:
            insert_setoran(rec, email)
            st.snow()
            st.toast(f"Data setoran {split_murid(murid)[0]} berhasil disimpan.", icon="🕌")

def tab_tracking():
    st.subheader("🪶 Tracking Portal Murid")
    c1, c2 = st.columns(2)
    with c1: kelas = st.selectbox("Pilih Kelas", list(DATABASE_MURID.keys()), key="track_k")
    with c2: murid = st.selectbox("Pilih Murid", DATABASE_MURID[kelas], key=f"track_m_{kelas}")

    df = get_setoran(kelas, murid)
    if df.empty:
        st.info("Belum ada riwayat setoran.")
        return
    m1, m2, m3 = st.columns(3)
    m1.markdown(kpi("Jumlah Setoran", len(df)), unsafe_allow_html=True)
    m2.markdown(kpi("Total Halaman", round(float(df["Halaman"].sum()), 2)), unsafe_allow_html=True)
    m3.markdown(kpi("Rata-Rata Nilai", round(float(df["Nilai"].mean()), 2)), unsafe_allow_html=True)
    st.line_chart(df.reset_index(drop=True)["Nilai"], height=160, color="#2F3A2E")
    st.dataframe(df.drop(columns=["ID", "Dibuat Oleh"]).iloc[::-1], hide_index=True, **STRETCH)

def tab_pdf():
    st.subheader("📜 Generator Laporan PDF")
    today = today_wita()
    c1, c2, c3 = st.columns(3)
    with c1: kelas = st.selectbox("Kelas Target", list(DATABASE_MURID.keys()), key="pdf_k")
    with c2: bulan = st.selectbox("Bulan", MONTHS_ID, index=today.month - 1, key="pdf_b")
    with c3: tahun = st.number_input("Tahun", min_value=2020, max_value=2100, value=today.year, step=1, key="pdf_t")

    periode = f"{bulan} {int(tahun)}"
    prefix = f"{int(tahun)}-{MONTHS_ID.index(bulan) + 1:02d}"
    sel = (kelas, periode)

    if st.button("📄 Siapkan Berkas PDF", key="btn_pdf"):
        df = get_setoran(kelas)
        df = df[df["Tanggal"].astype(str).str.startswith(prefix)]
        if df.empty:
            st.session_state.pop("pdf_ready", None)
            st.warning(f"Tidak ada setoran {kelas} pada {periode}.")
        else:
            st.session_state["pdf_ready"] = {
                "sel": sel, "n": len(df),
                "data": generate_pdf(df, periode, kelas),
                "name": f"Laporan_{kelas}_{periode}.pdf".replace(" ", "_"),
            }

    ready = st.session_state.get("pdf_ready")
    if ready and ready["sel"] == sel:
        st.success(f"Laporan siap: {ready['n']} setoran pada {periode}.")
        st.download_button("⬇️ Unduh PDF", data=ready["data"], file_name=ready["name"], mime="application/pdf", key="dl_pdf")

def tab_tasmi(email):
    st.subheader("🎯 Form Input Ujian Tasmi'")
    c1, c2 = st.columns(2)
    with c1:
        tanggal = st.date_input("📅 Tanggal Ujian", value=today_wita(), max_value=today_wita(), key="t_tgl")
        periode = st.text_input("Periode Ujian", "Triwulan I - 2026", key="t_periode")
        kelas = st.selectbox("Kelas Ujian", list(DATABASE_MURID.keys()), key="tas_k")
        murid = st.selectbox("Nama Murid Ujian", DATABASE_MURID[kelas], key=f"tas_m_{kelas}")
        penguji = st.selectbox("Penguji Tasmi'", DAFTAR_MUHAFFIDZ, key="tas_p")
    with c2:
        rentang = st.text_input("Rentang Surah/Juz", "Juz 30 (An-Naba' - An-Nas)", key="t_rentang")
        err_besar = st.number_input("Kesalahan Besar (Salah/Lupa)", min_value=0, value=0, key="t_eb")
        err_kecil = st.number_input("Kesalahan Kecil (Tajwid/Makhraj)", min_value=0, value=0, key="t_ek")
        catatan = st.text_area("Catatan Penguji", placeholder="Catatan evaluasi kelancaran dan makhraj...", key="t_cat")

    nilai = nilai_tasmi(err_besar, err_kecil)
    st.markdown(metric_box("Nilai Akhir Ujian Tasmi'", f"{nilai} / 100"), unsafe_allow_html=True)

    if st.button("🎯 SIMPAN RECORD TASMI'", key="btn_simpan_tasmi", type="primary"):
        rec = {
            "tanggal": tanggal.strftime("%Y-%m-%d"), "periode": periode, "kelas": kelas,
            "nama_murid": murid, "penguji": penguji, "rentang_surah": rentang,
            "err_besar": int(err_besar), "err_kecil": int(err_kecil),
            "nilai_akhir": nilai, "catatan": catatan,
        }
        if tasmi_exists(rec): st.warning("Record Tasmi' yang identik sudah tercatat.")
        else:
            insert_tasmi(rec, email)
            st.snow()
            st.toast(f"Data ujian Tasmi' {split_murid(murid)[0]} berhasil disimpan.", icon="🎯")

def tab_db_setoran():
    require_admin()
    st.subheader("◈ Database Setoran")
    st.caption("🔒 Khusus admin — rekap dan seluruh record setoran")
    df = get_setoran()
    k1, k2, k3 = st.columns(3)
    k1.markdown(kpi("Total Setoran", len(df)), unsafe_allow_html=True)
    k2.markdown(kpi("Total Halaman", round(float(df["Halaman"].sum()), 2) if not df.empty else 0), unsafe_allow_html=True)
    k3.markdown(kpi("Rata-Rata Nilai", round(float(df["Nilai"].mean()), 2) if not df.empty else 0.0), unsafe_allow_html=True)

    kelas = st.selectbox("🔍 Pilih Kelas", list(DATABASE_MURID.keys()), key="db_s_kelas")
    st.markdown("##### Rekap per murid")
    st.dataframe(build_rekap(df, kelas), hide_index=True, height=380, **STRETCH)

    with st.expander("Matriks horizontal — setoran terakhir per murid"):
        n = st.slider("Jumlah setoran terakhir yang ditampilkan", 3, 50, 10, key="db_s_n")
        st.dataframe(build_detail_matrix(df, kelas, n), hide_index=True, height=380, **STRETCH)

    with st.expander("Seluruh record setoran"):
        st.dataframe(df.iloc[::-1], hide_index=True, height=380, **STRETCH)

def tab_db_tasmi():
    require_admin()
    st.subheader("📂 Matriks Database Ujian Tasmi'")
    st.caption("🔒 Khusus admin — rekapitulasi nilai dan kesalahan ujian Tasmi' murid")
    df = get_tasmi()
    kelas = st.selectbox("🔍 Pilih Kelas Matriks Tasmi'", list(DATABASE_MURID.keys()), key="db_t_kelas")
    st.dataframe(build_tasmi_matrix(df, kelas), hide_index=True, height=380, **STRETCH)
    with st.expander("Seluruh record Tasmi'"):
        st.dataframe(df.iloc[::-1], hide_index=True, height=380, **STRETCH)

def tab_admin(cfg, email):
    require_admin()
    st.title("🛡️ Control Panel & System Governance")
    st.caption("Pusat kendali sesi pengguna, pemeliharaan, cadangan data, dan jejak audit.")

    st.subheader("🟢 Monitoring Sesi Aktif")
    sessions = get_sessions()
    if sessions.empty: st.info("Belum ada log sesi pengguna yang terekam.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Total Sesi Terdaftar", len(sessions))
        m2.metric(f"Online (aktif <{ONLINE_WINDOW_MIN} menit)", int((sessions["Status"] == "Online 🟢").sum()))
        st.dataframe(sessions, hide_index=True, **STRETCH)

    st.divider()
    st.subheader("💾 Cadangan Data")
    b1, b2 = st.columns(2)
    stamp = today_wita().strftime("%Y%m%d")
    with b1:
        st.download_button("⬇️ Ekspor Setoran (CSV)", get_setoran().to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"setoran_{stamp}.csv", mime="text/csv", key="dl_set", **STRETCH)
    with b2:
        st.download_button("⬇️ Ekspor Tasmi' (CSV)", get_tasmi().to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"tasmi_{stamp}.csv", mime="text/csv", key="dl_tas", **STRETCH)

    st.divider()
    st.subheader("⚠️ Manajemen Pemeliharaan Data")
    if not st.session_state["admin_board_unlocked"]:
        with st.container(border=True):
            st.warning("Fitur hapus data dikunci. Masukkan sandi keamanan admin untuk membuka otorisasi.")
            with st.form("form_unlock_admin"):
                passkey = st.text_input("Sandi Keamanan Admin", type="password", key="admin_unlock_pass")
                if st.form_submit_button("🔓 Buka Otorisasi Fitur Sensitif"):
                    if safe_equal(passkey, cfg["passkey"]):
                        st.session_state["admin_board_unlocked"] = True
                        log_audit(email, "buka_otorisasi_admin")
                        st.rerun()
                    else:
                        log_audit(email, "gagal_otorisasi_admin")
                        st.error("Kata sandi salah! Akses ditolak.")
    else:
        st.success("Sistem terbuka — Anda memiliki hak akses penuh untuk menghapus data.", icon="🔓")
        col1, col2 = st.columns(2)
        with col1:
            delete_panel("setoran", get_setoran(), email,
                         lambda r: f"#{r['ID']} | {r['Tanggal']} | {split_murid(r['Nama Murid'])[0]} | {r['Surah']}")
        with col2:
            delete_panel("tasmi", get_tasmi(), email,
                         lambda r: f"#{r['ID']} | {r['Tanggal']} | {split_murid(r['Nama Murid'])[0]} | {r['Rentang Surah']}")
        if st.button("🔒 Kunci Kembali Panel Admin", key="btn_lock", **STRETCH):
            st.session_state["admin_board_unlocked"] = False
            st.rerun()

    st.divider()
    st.subheader("📜 Jejak Audit (50 terakhir)")
    st.dataframe(get_audit(50), hide_index=True, **STRETCH)

def delete_panel(table, df, email, label_fn):
    title = "Setoran Harian" if table == "setoran" else "Record Tasmi'"
    with st.container(border=True):
        st.markdown(f"##### 🗑️ Hapus {title}")
        if df.empty:
            st.info("Tidak ada data.")
            return
        labels = {int(r["ID"]): label_fn(r) for r in df.to_dict("records")}
        rid = st.selectbox("Pilih record:", list(reversed(list(labels))), format_func=lambda x: labels[x], key=f"del_sel_{table}")
        yakin = st.checkbox("Saya yakin ingin menghapus record ini (tercatat di audit)", key=f"del_ok_{table}")
        if st.button(f"🚨 Hapus Record {title}", type="primary", disabled=not yakin, key=f"btn_del_{table}", **STRETCH):
            if delete_record(table, rid, email): st.toast("Record berhasil dihapus.", icon="🗑️")
            st.rerun()

# ----------------------------------------------------------------------------
# EKSEKUSI UTAMA APP
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def init_once():
    init_db()
    return True

st.markdown(CSS, unsafe_allow_html=True)
cfg = load_config()

if cfg is None:
    render_header("TahfidzTrack — SMPIT Ibnul Qayyim", "Sistem Management & Monitoring Hafalan Qur'an Murid")
    st.error("Konfigurasi login belum ditemukan. Buat berkas `.streamlit/secrets.toml`.")
    st.stop()

init_once()

if "logged_in" not in st.session_state:
    st.session_state.update(logged_in=False, user_email="", is_admin=False)
if "admin_board_unlocked" not in st.session_state:
    st.session_state["admin_board_unlocked"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

if not st.session_state["logged_in"]:
    render_header("TahfidzTrack — SMPIT Ibnul Qayyim", "Sistem Management & Monitoring Hafalan Qur'an Murid")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.form("login_form"):
            st.subheader("🔑 Autentikasi Pengampu")
            email_in = st.text_input("Alamat Email Akademik", placeholder="contoh: nama@iqis.sch.id")
            pass_in = st.text_input("Sandi Keamanan", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Akses Portal ➔")

        if submit:
            email_clean = email_in.strip().lower()[:120]
            remaining = lock_remaining_seconds(email_clean)
            expected = cfg["users"].get(email_clean)
            ok = safe_equal(pass_in.strip(), expected if expected is not None else "\x00invalid")
            if remaining > 0:
                st.error(f"Terlalu banyak percobaan gagal. Coba lagi dalam {math.ceil(remaining / 60)} menit.")
            elif ok and expected is not None:
                clear_failed_logins(email_clean)
                st.session_state.update(logged_in=True, user_email=email_clean, is_admin=email_clean in cfg["admins"])
                touch_session(email_clean, new_login=True)
                log_audit(email_clean, "login")
                st.session_state["current_page"] = "Dashboard"
                st.rerun()
            else:
                terkunci = register_failed_login(email_clean)
                st.error("Terlalu banyak percobaan gagal. Akun dikunci sementara." if terkunci else "Kredensial tidak terverifikasi.")
else:
    email = st.session_state["user_email"]
    is_admin = st.session_state["is_admin"]

    # Heartbeat Sesi
    last_beat = st.session_state.get("_heartbeat")
    if last_beat is None or (naive_now() - last_beat).total_seconds() >= 60:
        touch_session(email)
        st.session_state["_heartbeat"] = naive_now()

    render_header("TahfidzTrack — SMPIT Ibnul Qayyim", "Sistem Management & Monitoring Hafalan Qur'an Murid")

    c_user, c_logout = st.columns([4, 1])
    with c_user:
        badge = "badge-admin" if is_admin else "badge-success"
        role = " [ADMIN]" if is_admin else ""
        st.markdown(f"⚡ **User Active:** <span class='{badge}'>{html.escape(email)}{role}</span>", unsafe_allow_html=True)
    with c_logout:
        if st.button("🚪 Keluar", key="btn_logout", **STRETCH):
            end_session(email)
            log_audit(email, "logout")
            for k in ("logged_in", "is_admin", "admin_board_unlocked", "_heartbeat", "pdf_ready", "current_page"):
                st.session_state.pop(k, None)
            st.session_state["user_email"] = ""
            st.rerun()

    st.write("")

    # Daftar Halaman yang Tersedia
    page_map = {
        "✦ Presensi Setoran": lambda: tab_setoran(cfg, email),
        "🪶 Tracking Portal": tab_tracking,
        "📜 Laporan PDF": tab_pdf,
        "🎯 Ujian Tasmi'": lambda: tab_tasmi(email),
    }
    if is_admin:
        page_map["◈ Database Setoran 🔒"] = tab_db_setoran
        page_map["📂 Database Tasmi' 🔒"] = tab_db_tasmi
        page_map["🛡️ Admin Board"] = lambda: tab_admin(cfg, email)

    current = st.session_state.get("current_page", "Dashboard")

    # Baris Navigasi Atas jika sedang di sub-halaman
    if current != "Dashboard":
        n_col1, n_col2 = st.columns([1, 3])
        with n_col1:
            if st.button("⬅️ Kembali ke Dashboard", key="btn_back_home", **STRETCH):
                st.session_state["current_page"] = "Dashboard"
                st.rerun()
        with n_col2:
            all_pages = list(page_map.keys())
            idx_curr = all_pages.index(current) if current in all_pages else 0
            selected_p = st.selectbox("Pindah Halaman Cepat:", all_pages, index=idx_curr, key="quick_page_nav")
            if selected_p != current:
                st.session_state["current_page"] = selected_p
                st.rerun()
        st.divider()

    # RENDER HALAMAN
    if current == "Dashboard":
        render_landing_dashboard(is_admin)
    elif current in page_map:
        page_map[current]()
