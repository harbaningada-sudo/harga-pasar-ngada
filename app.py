import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json
import hashlib
import uuid
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Selamat Datang di Portal Resmi Bagian Perekonomian dan SDA Setda Ngada. Kami hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "about_text": "Bagian Perekonomian dan SDA Setda Ngada. Hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "tren_jumlah": 6,
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                saved_data = json.load(f)
                for key, value in default_data.items():
                    if key not in saved_data: saved_data[key] = value
                return saved_data
        except: return default_data
    return default_data

def save_settings(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def news_key(row):
    raw = f"{row.get('Tanggal','')}-{row.get('Kegiatan','')}"
    return hashlib.md5(raw.encode()).hexdigest()[:10]

# --- 2a. KOMENTAR PERMANEN VIA GOOGLE SHEETS ---
COMMENTS_SHEET_HEADER = ["id", "key_id", "title", "nama", "rating", "isi", "tanggal", "balasan", "balasan_tanggal"]
GSHEET_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource(show_spinner=False)
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=GSHEET_SCOPES
    )
    return gspread.authorize(creds)

@st.cache_resource(show_spinner=False)
def get_comments_ws():
    client = get_gspread_client()
    sheet = client.open_by_url(st.secrets["COMMENTS_SHEET_URL"])
    try:
        ws = sheet.worksheet("Comments")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Comments", rows=2000, cols=len(COMMENTS_SHEET_HEADER))
        ws.append_row(COMMENTS_SHEET_HEADER)
    return ws

def load_comments():
    """Ambil semua komentar dari Google Sheets (di-cache 20 detik) supaya interaksi
    admin yang sering (ketik teks, upload gambar, dll) tidak menembak API Google Sheets
    berkali-kali dan kena limit kuota per menit."""
    try:
        return _load_comments_cached()
    except Exception as e:
        st.session_state["_comments_load_error"] = str(e)
        return None

@st.cache_data(ttl=20, show_spinner=False)
def _load_comments_cached():
    ws = get_comments_ws()
    records = ws.get_all_records()

    data = {}
    for r in records:
        k = str(r.get("key_id", "")).strip()
        if not k:
            continue
        if k not in data:
            data[k] = {"title": r.get("title", k), "entries": []}
        try:
            rating_val = int(r.get("rating", 5) or 5)
        except (ValueError, TypeError):
            rating_val = 5
        data[k]["entries"].append({
            "id": str(r.get("id", "")),
            "nama": r.get("nama", ""),
            "rating": rating_val,
            "isi": r.get("isi", ""),
            "tanggal": r.get("tanggal", ""),
            "balasan": r.get("balasan", ""),
            "balasan_tanggal": r.get("balasan_tanggal", ""),
        })
    return data

def add_comment(key_id, title, nama, rating, isi):
    try:
        ws = get_comments_ws()
        cid = str(uuid.uuid4())[:8]
        tanggal = datetime.now().strftime("%d %b %Y, %H:%M")
        ws.append_row([cid, key_id, title, nama, rating, isi, tanggal, "", ""])
        _load_comments_cached.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan komentar: {e}")
        return False

def update_reply(comment_id, balasan):
    try:
        ws = get_comments_ws()
        cell = ws.find(comment_id)
        if cell:
            tanggal = datetime.now().strftime("%d %b %Y, %H:%M")
            ws.update_cell(cell.row, COMMENTS_SHEET_HEADER.index("balasan") + 1, balasan)
            ws.update_cell(cell.row, COMMENTS_SHEET_HEADER.index("balasan_tanggal") + 1, tanggal)
            _load_comments_cached.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Gagal menyimpan balasan: {e}")
        return False

def delete_comment(comment_id):
    try:
        ws = get_comments_ws()
        cell = ws.find(comment_id)
        if cell:
            ws.delete_rows(cell.row)
            _load_comments_cached.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Gagal menghapus komentar: {e}")
        return False

# --- 2b. GAMBAR YANG DIUPLOAD ADMIN — DISIMPAN PERMANEN DI GOOGLE SHEETS ---
IMAGES_SHEET_HEADER = ["id", "target", "caption", "data_b64", "mime", "tanggal"]

@st.cache_resource(show_spinner=False)
def get_images_ws():
    client = get_gspread_client()
    sheet = client.open_by_url(st.secrets["COMMENTS_SHEET_URL"])
    try:
        ws = sheet.worksheet("Images")
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Images", rows=500, cols=len(IMAGES_SHEET_HEADER))
        ws.append_row(IMAGES_SHEET_HEADER)
    return ws

def load_images():
    try:
        return _load_images_cached()
    except Exception as e:
        st.session_state["_images_load_error"] = str(e)
        return None

@st.cache_data(ttl=20, show_spinner=False)
def _load_images_cached():
    ws = get_images_ws()
    records = ws.get_all_records()
    hero = None
    galeri = {"pertanian": [], "pariwisata": []}
    for r in records:
        target = str(r.get("target", "")).strip()
        entry = {
            "id": str(r.get("id", "")),
            "caption": r.get("caption", ""),
            "data_b64": r.get("data_b64", ""),
            "mime": r.get("mime", "image/jpeg"),
        }
        if target == "hero":
            hero = entry
        elif target == "galeri:pertanian":
            galeri["pertanian"].append(entry)
        elif target == "galeri:pariwisata":
            galeri["pariwisata"].append(entry)
    return {"hero": hero, "galeri": galeri}

def compress_image_for_sheets(file_bytes, max_chars=45000):
    """Resize & kompres gambar supaya base64-nya muat di 1 sel Google Sheets (limit 50.000 karakter)."""
    from PIL import Image
    import io as _io
    img = Image.open(_io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    max_width, quality = 1000, 82
    for _ in range(12):
        if img.size[0] > max_width:
            ratio = max_width / float(img.size[0])
            resized = img.resize((max_width, max(1, int(img.size[1] * ratio))))
        else:
            resized = img
        buf = _io.BytesIO()
        resized.save(buf, format="JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if len(b64) <= max_chars:
            return b64, "image/jpeg"
        if quality > 30:
            quality -= 15
        else:
            max_width = int(max_width * 0.75)
            quality = 60
    return b64, "image/jpeg"

def add_image_record(target, caption, file_bytes):
    try:
        b64, mime = compress_image_for_sheets(file_bytes)
        ws = get_images_ws()
        rid = str(uuid.uuid4())[:8]
        tanggal = datetime.now().strftime("%d %b %Y, %H:%M")
        ws.append_row([rid, target, caption, b64, mime, tanggal])
        _load_images_cached.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan gambar: {e}")
        return False

def delete_image_record(record_id):
    try:
        ws = get_images_ws()
        cell = ws.find(record_id)
        if cell:
            ws.delete_rows(cell.row)
            _load_images_cached.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Gagal menghapus gambar: {e}")
        return False

def set_hero_image(file_bytes):
    """Ganti foto hero: hapus baris 'hero' lama dulu (biar sheet tidak menumpuk), lalu simpan yang baru."""
    try:
        ws = get_images_ws()
        for cell in sorted(ws.findall("hero"), key=lambda c: c.row, reverse=True):
            if cell.col == 2:
                ws.delete_rows(cell.row)
        b64, mime = compress_image_for_sheets(file_bytes)
        rid = str(uuid.uuid4())[:8]
        tanggal = datetime.now().strftime("%d %b %Y, %H:%M")
        ws.append_row([rid, "hero", "", b64, mime, tanggal])
        _load_images_cached.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan foto beranda: {e}")
        return False

def reset_hero_image():
    try:
        ws = get_images_ws()
        for cell in sorted(ws.findall("hero"), key=lambda c: c.row, reverse=True):
            if cell.col == 2:
                ws.delete_rows(cell.row)
        _load_images_cached.clear()
        return True
    except Exception as e:
        st.error(f"Gagal mereset foto beranda: {e}")
        return False

IMAGE_SLOTS = {
    "hero": {"label": "Foto Beranda (Hero)", "default": "IMG_20251125_111048.jpg"},
}

def get_image_path(slot):
    images_data = load_images()
    if images_data and images_data.get("hero") and slot == "hero":
        try:
            return base64.b64decode(images_data["hero"]["data_b64"])
        except Exception:
            pass
    default = IMAGE_SLOTS[slot]["default"]
    if os.path.exists(default):
        return default
    return None

# --- 2c. GALERI POTENSI (Pertanian & Pariwisata) ---
GALERI_DEFAULT = {
    "pertanian": [
        {"file": "cengkeh.jpeg", "caption": "Cengkeh Ngada"},
        {"file": "sawah ngada.webp", "caption": "Pertanian"},
    ],
    "pariwisata": [
        {"file": "bena.webp", "caption": "Kampung Bena"},
        {"file": "17 pulau riung.webp", "caption": "Riung"},
    ],
}
GALERI_LABELS = {"pertanian": "🌾 Pertanian", "pariwisata": "🏞️ Pariwisata"}

def get_galeri(category):
    items = []
    for it in GALERI_DEFAULT.get(category, []):
        if os.path.exists(it["file"]):
            items.append({"src": it["file"], "caption": it["caption"], "record_id": None})
    images_data = load_images()
    if images_data:
        for entry in images_data["galeri"].get(category, []):
            try:
                items.append({
                    "src": base64.b64decode(entry["data_b64"]),
                    "caption": entry.get("caption", ""),
                    "record_id": entry["id"],
                })
            except Exception:
                pass
    return items

# ============================================================================
# --- 2d. INFLASI & IHK — DIAMBIL LANGSUNG DARI SPREADSHEET ANDA ---
# Tidak lagi scraping BPS. Data diambil live dari Google Sheet milik user,
# sheet "Inflasi 2026" (angka inflasi + keterangan/penyebab) dan
# "IHK 2026" (Indeks Harga Konsumen), digabung berdasarkan kolom "Bulan".
#
# PENTING: spreadsheet sumber harus di-Share ke email service account yang
# sama dipakai untuk Comments/Images (lihat st.secrets["gcp_service_account"]),
# minimal akses "Viewer", supaya bisa dibaca oleh aplikasi ini.
# ============================================================================

INFLASI_SPREADSHEET_URL = st.secrets.get(
    "INFLASI_SHEET_URL",
    "https://docs.google.com/spreadsheets/d/1KZg710gSU-5pAQoqJIlwxKLEeAlIQbTbAOjjeGwy0iw/edit?usp=sharing",
)
SHEET_NAME_INFLASI = "Inflasi 2026"
SHEET_NAME_IHK = "IHK 2026"

BULAN_ID = ["januari", "februari", "maret", "april", "mei", "juni", "juli",
            "agustus", "september", "oktober", "november", "desember"]

@st.cache_resource(show_spinner=False)
def get_inflasi_spreadsheet():
    client = get_gspread_client()
    return client.open_by_url(INFLASI_SPREADSHEET_URL)

def _parse_id_number(value):
    v = str(value).replace(",", ".").replace("%", "").strip()
    try:
        return float(v)
    except ValueError:
        return None

def _bulan_sort_key(bulan_text):
    low = str(bulan_text).strip().lower()
    for i, nama in enumerate(BULAN_ID):
        if nama in low:
            return i
    return 99

def _cell(row, idx):
    return str(row[idx]).strip() if idx < len(row) else ""

def _match_year_header(text, tahun="2026"):
    """Cek apakah sebuah sel adalah header tahun/bulan-tahun yang mengarah ke
    `tahun` (mis. '2026', 'Juni 2026', 'Juni Tahun 2026'). Mengembalikan
    (cocok: bool, nama_bulan_atau_None)."""
    t = str(text).strip()
    if not t:
        return False, None
    if re.fullmatch(r"\d{4}", t):
        return t == tahun, None
    m = re.match(r"^([A-Za-zÀ-ÿ]+)\s*(?:Tahun)?\s*(\d{4})$", t, re.IGNORECASE)
    if m and m.group(2) == tahun:
        return True, m.group(1).strip().capitalize()
    return False, None

def _parse_inflasi_2026_sheet(values, tahun="2026"):
    """Sheet 'Inflasi 2026' berpola: header 'Bulan Tahun 2026' di kolom C/D,
    lalu baris di bawahnya berlabel 'Inflasi (Yoy)' / 'Inflasi (MtM)' (kolom B)
    dengan nilai persen di kolom yang sama dengan header. Kembalikan dict:
    bulan -> {"yoy":.., "mtm":.., "keterangan":..}."""
    hasil = {}
    n = len(values)
    for i, row in enumerate(values):
        for j, cell in enumerate(row):
            is_match, bulan = _match_year_header(cell, tahun)
            if not (is_match and bulan):
                continue
            for k in range(i + 1, min(i + 6, n)):
                label = _cell(values[k], 1)
                val = _cell(values[k], j)
                if not label or not val:
                    continue
                low = label.lower()
                entry = hasil.setdefault(bulan, {})
                if "yoy" in low:
                    entry["yoy"] = val
                elif "mtm" in low:
                    entry["mtm"] = val
                elif any(kw in low for kw in ["keterangan", "penyebab", "catatan"]):
                    entry["keterangan"] = val
    return hasil

def _parse_ihk_2026_sheet(values, tahun="2026"):
    """Sheet 'IHK 2026' punya dua pola sekaligus:
    (a) header cuma tahun ('2026') diikuti banyak baris nama bulan+nilai, atau
    (b) header 'Bulan 2026' langsung diikuti 1 baris berlabel 'IHK'+nilai.
    Kembalikan dict: bulan -> nilai IHK."""
    hasil = {}
    n = len(values)
    i = 0
    while i < n:
        row = values[i]
        matched_col, bulan_header = None, None
        for j, cell in enumerate(row):
            is_match, bulan = _match_year_header(cell, tahun)
            if is_match:
                matched_col, bulan_header = j, bulan
                break
        if matched_col is None:
            i += 1
            continue

        if bulan_header:
            for k in range(i + 1, min(i + 4, n)):
                label = _cell(values[k], 1)
                val = _cell(values[k], matched_col)
                if label and val and "ihk" in label.lower():
                    hasil[bulan_header] = val
                    break
        else:
            k = i + 1
            while k < n:
                label = _cell(values[k], 1)
                val = _cell(values[k], matched_col)
                low = label.lower()
                if any(b in low for b in BULAN_ID):
                    if val:
                        hasil[label.capitalize()] = val
                    k += 1
                    continue
                break
        i += 1
    return hasil

def _auto_keterangan(bulan, inf, ihk_val):
    """Susun kalimat keterangan otomatis dari angka Yoy/MtM/IHK yang tersedia,
    dipakai kalau tidak ada kolom Keterangan/Penyebab manual di spreadsheet."""
    if inf.get("keterangan"):
        return inf["keterangan"]
    kalimat = []
    if inf.get("yoy"):
        kalimat.append(f"Inflasi tahun ke tahun (year on year) {bulan} 2026 tercatat sebesar {inf['yoy']}.")
    if inf.get("mtm"):
        v = _parse_id_number(inf["mtm"])
        if v is not None:
            arah = "naik" if v > 0 else ("turun" if v < 0 else "stabil")
            kalimat.append(f"Secara bulanan (month to month), harga {arah} {abs(v):.2f}% dibanding bulan sebelumnya.")
        else:
            kalimat.append(f"Inflasi bulanan (month to month) tercatat {inf['mtm']}.")
    if ihk_val:
        kalimat.append(f"Indeks Harga Konsumen (IHK) bulan ini sebesar {ihk_val}.")
    return " ".join(kalimat)

def _build_inflasi_gabungan():
    ss = get_inflasi_spreadsheet()

    values_inf, values_ihk = [], []
    try:
        values_inf = ss.worksheet(SHEET_NAME_INFLASI).get_all_values()
    except gspread.WorksheetNotFound:
        pass
    try:
        values_ihk = ss.worksheet(SHEET_NAME_IHK).get_all_values()
    except gspread.WorksheetNotFound:
        pass

    inflasi_map = _parse_inflasi_2026_sheet(values_inf) if values_inf else {}
    ihk_map = _parse_ihk_2026_sheet(values_ihk) if values_ihk else {}

    all_bulan = set(inflasi_map.keys()) | set(ihk_map.keys())
    rows = []
    for bulan in all_bulan:
        inf = inflasi_map.get(bulan, {})
        ihk_val = ihk_map.get(bulan, "")
        yoy, mtm = inf.get("yoy", ""), inf.get("mtm", "")
        rows.append({
            "Bulan": bulan,
            "Inflasi (%)": yoy if yoy else mtm,
            "Inflasi YoY (%)": yoy,
            "Inflasi MtM (%)": mtm,
            "IHK": ihk_val,
            "Keterangan": _auto_keterangan(bulan, inf, ihk_val),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["Inflasi_num"] = df["Inflasi (%)"].apply(_parse_id_number)
    df["_urut"] = df["Bulan"].apply(_bulan_sort_key)
    df = df.sort_values("_urut").drop(columns="_urut").reset_index(drop=True)
    return df

# TTL diperpendek dari 60 -> 30 detik supaya perubahan di spreadsheet
# (bulan baru, angka yang diedit, dsb) lebih cepat muncul otomatis di aplikasi.
@st.cache_data(ttl=30, show_spinner=False)
def _load_inflasi_gabungan_cached():
    return _build_inflasi_gabungan()

def load_inflasi_gabungan():
    """Ambil data inflasi+IHK gabungan (di-cache 30 detik supaya perubahan di
    spreadsheet cepat terbaca tapi API Google Sheets tidak dibebani tiap klik).
    Kalau gagal, simpan pesan error untuk ditampilkan ke admin."""
    try:
        return _load_inflasi_gabungan_cached()
    except Exception as e:
        st.session_state["_inflasi_load_error"] = str(e)
        return pd.DataFrame()


# Inisialisasi State agar tidak NameError
if "store" not in st.session_state:
    st.session_state.store = load_settings()

# Jika API sedang kena limit kuota, JANGAN timpa komentar lama dengan kosong —
# pertahankan data terakhir yang berhasil dimuat supaya tampilan tidak "hilang" tiba-tiba.
_new_comments = load_comments()
if _new_comments is not None:
    st.session_state.comments = _new_comments
elif "comments" not in st.session_state:
    st.session_state.comments = {}

if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

is_admin = st.query_params.get("status") == "set"

# Kalau tadi gagal ambil komentar (mis. kena limit kuota Google Sheets sesaat),
# beri tahu admin saja secara halus — pengunjung biasa tidak perlu lihat pesan teknis ini.
if is_admin and st.session_state.pop("_comments_load_error", None):
    st.caption("⚠️ Komentar terbaru belum sempat dimuat ulang (server Google Sheets sedang sibuk). Menampilkan data terakhir yang tersimpan — coba lagi sebentar.")

# --- 3. HELPER GAMBAR & CSS ---
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_pimpinan = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
img_logo = get_base64("logo_ngada.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {{
        --ngd-forest: #1B4332;
        --ngd-forest-deep: #0F2E22;
        --ngd-gold: #B8863B;
        --ngd-gold-light: #E4C888;
        --ngd-terracotta: #A6432B;
        --ngd-paper: #F7F3EA;
        --ngd-paper-warm: #F1EADA;
        --ngd-ink: #22201B;
        --ngd-slate: #5B6660;
    }}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(1200px 600px at 100% -10%, rgba(184,134,59,0.08), transparent),
            linear-gradient(180deg, var(--ngd-paper) 0%, var(--ngd-paper-warm) 100%) !important;
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    html, body, [data-testid="stWidgetLabel"], .stText, p, span, div, li {{
        color: var(--ngd-ink) !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Fraunces', serif !important;
        color: var(--ngd-forest-deep) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }}

    /* ===== IKAT MOTIF DIVIDER ===== */
    .ikat-rule {{
        height: 8px;
        margin: 4px 0 22px 0;
        border-radius: 4px;
        background: repeating-linear-gradient(
            135deg,
            var(--ngd-gold) 0px, var(--ngd-gold) 10px,
            var(--ngd-terracotta) 10px, var(--ngd-terracotta) 20px,
            var(--ngd-forest) 20px, var(--ngd-forest) 30px
        );
        opacity: 0.85;
    }}

    /* ===== HEADER ===== */
    .header-banner {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, var(--ngd-forest-deep) 0%, var(--ngd-forest) 65%, #2D5A46 100%);
        border-radius: 18px;
        padding: 24px 30px;
        box-shadow: 0 14px 30px rgba(15,46,34,0.28);
        margin-bottom: 6px;
        border: 1px solid rgba(228,200,136,0.25);
    }}
    .header-banner::after {{
        content: "";
        position: absolute; top: 0; right: 0; bottom: 0; width: 10px;
        background: repeating-linear-gradient(
            180deg, var(--ngd-gold) 0px, var(--ngd-gold) 8px,
            var(--ngd-terracotta) 8px, var(--ngd-terracotta) 16px
        );
        opacity: 0.9;
    }}
    .header-banner h2, .header-banner p {{ color: #FBF6EA !important; }}
    .header-banner h2 {{
        margin: 0; font-weight: 700 !important; letter-spacing: 0.2px; font-size: 1.65rem;
        font-family: 'Fraunces', serif !important;
    }}
    .header-banner .eyebrow {{
        display:inline-block; background: var(--ngd-gold); color: #23200F !important;
        padding: 3px 12px; border-radius: 20px; margin-right: 10px; font-size: 0.72em;
        font-weight: 800; letter-spacing: 0.6px; vertical-align: middle;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}
    .header-banner p {{
        margin: 6px 0 0 0; font-size: 0.98rem; opacity: 0.92; font-weight: 500;
    }}

    .pimpinan-frame {{
        width: 94px; height: 94px; border-radius: 16px; border: 3px solid var(--ngd-gold-light);
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
        box-shadow: 0 8px 18px rgba(15,46,34,0.3);
    }}
    .logo-mini {{
        position: absolute; bottom: -6px; right: -6px; width: 34px; height: 34px;
        background: #FBF6EA; border-radius: 8px; padding: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        border: 1px solid var(--ngd-gold);
    }}

    /* ===== NAV BUTTONS ===== */
    .stButton button {{
        background-color: #FFFFFF !important; color: var(--ngd-forest-deep) !important;
        border: 1.5px solid #DDD3BC !important;
        border-radius: 10px !important; transition: 0.25s; padding: 9px 10px;
        font-weight: 700 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: 0.2px;
    }}
    .stButton button:hover {{
        background-color: var(--ngd-forest) !important; color: #FBF6EA !important;
        border-color: var(--ngd-forest) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(27,67,50,0.28);
    }}
    div[data-testid="stDownloadButton"] button {{
        background: linear-gradient(120deg, var(--ngd-forest-deep), var(--ngd-forest)) !important;
        color: #FBF6EA !important; border: 1px solid var(--ngd-gold) !important; font-weight: 700 !important;
        border-radius: 10px !important; padding: 10px !important;
    }}
    .stForm button[kind="formSubmit"], button[kind="primary"] {{
        background: linear-gradient(120deg, var(--ngd-terracotta), var(--ngd-gold)) !important;
        color: #FBF6EA !important; border: none !important;
    }}

    /* ===== CARDS ===== */
    .price-card {{
        background: #FFFDF8 !important; padding: 16px 18px; border-radius: 14px;
        box-shadow: 0 4px 12px rgba(34,32,27,0.06); margin-bottom: 12px;
        border-left: 5px solid var(--ngd-forest); border: 1px solid #EDE4CE;
        transition: 0.2s;
    }}
    .price-card:hover {{ box-shadow: 0 10px 22px rgba(34,32,27,0.1); transform: translateY(-2px); }}
    .flex-container {{ display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }}

    .news-card {{
        background: #FFFDF8; border-radius: 16px; padding: 20px 22px; margin-bottom: 16px;
        box-shadow: 0 6px 16px rgba(34,32,27,0.07); border-top: 4px solid var(--ngd-terracotta);
        border: 1px solid #EDE4CE; border-top: 4px solid var(--ngd-terracotta);
        transition: 0.25s;
    }}
    .news-card:hover {{ box-shadow: 0 12px 24px rgba(34,32,27,0.12); transform: translateY(-3px); }}
    .news-date {{
        display:inline-block; background: var(--ngd-forest); color:#FBF6EA !important; font-weight:700;
        font-size:0.72rem; padding:4px 12px; border-radius:20px; margin-bottom:10px; letter-spacing: 0.3px;
    }}
    .news-title {{ font-size: 1.08rem; font-weight: 700; color: var(--ngd-forest-deep) !important; line-height:1.4;
        font-family: 'Fraunces', serif !important; }}

    .rating-badge {{
        display:inline-block; background: #FCEFD9; color: var(--ngd-terracotta) !important; font-weight:800;
        font-size:0.82rem; padding:5px 14px; border-radius:20px; margin-top:10px; border: 1px solid #F1D9AC;
    }}

    .comment-box {{
        background:#FFFDF8; border-radius:12px; padding:12px 16px; margin-top:10px;
        border-left: 3px solid var(--ngd-terracotta); border: 1px solid #EDE4CE; border-left: 3px solid var(--ngd-terracotta);
    }}
    .comment-name {{ font-weight:700; color: var(--ngd-forest) !important; font-size:0.9rem; }}
    .comment-date {{ color:#9A9082 !important; font-size:0.7rem; }}

    .reply-box {{
        background:#F2F6F3; border-radius:12px; padding:12px 16px; margin-top:8px;
        margin-left: 24px; border-left: 3px solid var(--ngd-forest); border: 1px solid #DEE8E1; border-left: 3px solid var(--ngd-forest);
    }}
    .reply-label {{
        font-weight:800; color: var(--ngd-forest) !important; font-size:0.85rem;
        display:flex; align-items:center; gap:6px;
    }}
    .reply-date {{ color:#9A9082 !important; font-size:0.7rem; }}

    .section-eyebrow {{
        display:inline-block; color: var(--ngd-terracotta) !important; font-weight: 800;
        font-size: 0.78rem; letter-spacing: 1.6px; text-transform: uppercase; margin-bottom: 2px;
    }}

    section[data-testid="stExpander"] {{
        background:#FFFDF8; border-radius:14px !important; border: 1px solid #EDE4CE !important;
        box-shadow: 0 4px 10px rgba(34,32,27,0.06); margin-bottom: 14px;
    }}

    [data-testid="stForm"] {{
        background: #FFFDF8; border: 1px solid #EDE4CE; border-radius: 16px; padding: 18px 20px 6px 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_b = pd.DataFrame(), pd.DataFrame()
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])

        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_b = pd.read_csv(url_b, skiprows=2)
        raw_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = raw_b.dropna(subset=['Kegiatan']).fillna("")
    except: pass
    return df_h, df_b

df_harga, df_berita = load_all_data()

# --- 5. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="header-banner" style="margin-left:-10px;">
            <h2><span class="eyebrow">SI-PARI</span>KABUPATEN NGADA</h2>
            <p>Sistem Informasi Publikasi Harga &middot; Bagian Perekonomian &amp; SDA Setda</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
st.markdown('<div class="ikat-rule"></div>', unsafe_allow_html=True)

# --- 6. ADMIN PANEL ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        st.session_state.store["hero_title"] = st.text_input("Judul Utama", st.session_state.store["hero_title"])
        st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])

        st.session_state.store["tren_jumlah"] = st.number_input(
            "Jumlah Komoditas Trending Ditampilkan", min_value=3, max_value=15,
            value=st.session_state.store.get("tren_jumlah", 6), step=1,
            help="Komoditas dipilih otomatis berdasarkan persentase perubahan harga terbesar — tidak perlu dipilih manual."
        )

        st.session_state.store["potensi_pertanian"] = st.text_area("Teks Pertanian", st.session_state.store["potensi_pertanian"])
        st.session_state.store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", st.session_state.store["potensi_pariwisata"])
        st.session_state.store["about_text"] = st.text_area("Tentang Kami", st.session_state.store["about_text"])

        if st.button("💾 SIMPAN DATA PERMANEN", type="primary", use_container_width=True):
            save_settings(st.session_state.store)
            st.success("Tersimpan!")
            st.balloons()

        st.divider()
        st.subheader("🖼️ Foto Beranda")
        st.caption("Foto disimpan permanen di Google Sheets (sama seperti komentar) — tidak akan hilang meski aplikasi tidur/redeploy.")
        for slot, info in IMAGE_SLOTS.items():
            with st.expander(info["label"]):
                current_path = get_image_path(slot)
                if current_path:
                    st.image(current_path, width=220)
                else:
                    st.caption("Belum ada gambar untuk slot ini.")

                uploaded_img = st.file_uploader(
                    f"Unggah gambar baru — {info['label']}",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"upload_{slot}"
                )
                if uploaded_img is not None:
                    if set_hero_image(uploaded_img.getvalue()):
                        st.success(f"{info['label']} berhasil diperbarui & tersimpan permanen!")
                        st.rerun()

                _hero_data = load_images()
                if _hero_data and _hero_data.get("hero"):
                    if st.button("↩️ Kembalikan ke Gambar Default", key=f"reset_img_{slot}", use_container_width=True):
                        if reset_hero_image():
                            st.rerun()

        st.divider()
        st.subheader("🌄 Galeri Foto Potensi")
        st.caption("Tambahkan foto baru beserta keterangannya ke halaman Potensi — tersimpan permanen di Google Sheets. Foto bawaan (dari repo) tidak akan terhapus.")
        for category, label in GALERI_LABELS.items():
            with st.expander(label, expanded=False):
                current_items = get_galeri(category)
                if current_items:
                    for idx, item in enumerate(current_items):
                        gcol1, gcol2 = st.columns([1, 2])
                        with gcol1:
                            st.image(item["src"], width=110)
                        with gcol2:
                            st.caption(item.get("caption", ""))
                            if item.get("record_id"):
                                if st.button("🗑️ Hapus", key=f"del_galeri_{category}_{idx}"):
                                    if delete_image_record(item["record_id"]):
                                        st.rerun()
                            else:
                                st.caption("_(foto bawaan repo, tidak bisa dihapus dari sini)_")
                else:
                    st.caption("Belum ada foto di galeri ini.")

                st.markdown("**➕ Tambah foto baru**")
                new_img = st.file_uploader(
                    f"Pilih foto — {label}",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"galeri_upload_{category}"
                )
                new_caption = st.text_input(
                    "Keterangan foto (mis. nama tempat/kegiatan)",
                    key=f"galeri_caption_{category}"
                )
                if st.button(f"➕ Tambah ke Galeri {label}", key=f"galeri_add_{category}", use_container_width=True):
                    if new_img is not None and new_caption.strip():
                        if add_image_record(f"galeri:{category}", new_caption.strip(), new_img.getvalue()):
                            st.success("Foto berhasil ditambahkan & tersimpan permanen!")
                            st.rerun()
                    else:
                        st.warning("Pilih foto dan isi keterangannya terlebih dahulu.")

        st.divider()
        st.subheader("📊 Data Inflasi & IHK (dari Spreadsheet)")
        st.caption("Diambil langsung dari sheet 'Inflasi 2026' & 'IHK 2026' di spreadsheet Anda. Edit angka/keterangannya di spreadsheet — aplikasi akan otomatis membaca ulang tiap 30 detik, atau klik refresh di bawah untuk langsung memuat ulang.")
        st.link_button("📝 Buka Spreadsheet Sumber Data", INFLASI_SPREADSHEET_URL, use_container_width=True)

        if st.session_state.pop("_inflasi_load_error", None):
            st.warning("⚠️ Gagal membaca data dari spreadsheet. Pastikan: (1) spreadsheet sudah di-Share ke email service account (lihat Google Cloud service account di secrets), (2) nama sheet persis 'Inflasi 2026' dan 'IHK 2026', (3) masing-masing sheet punya kolom yang memuat kata 'Bulan'.")

        if st.button("🔄 Muat Ulang dari Spreadsheet", use_container_width=True):
            _load_inflasi_gabungan_cached.clear()
            st.rerun()

        df_inflasi_admin = load_inflasi_gabungan()
        if not df_inflasi_admin.empty:
            st.dataframe(
                df_inflasi_admin[["Bulan", "Inflasi YoY (%)", "Inflasi MtM (%)", "IHK", "Keterangan"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("Belum ada data terbaca. Pastikan sheet 'Inflasi 2026' dan 'IHK 2026' sudah terisi dan spreadsheet sudah dibagikan ke service account.")

        st.divider()
        st.subheader("💬 Moderasi & Balasan Komentar")
        if st.session_state.comments:
            for k, item in st.session_state.comments.items():
                title = item.get("title", k)
                jumlah = len(item.get("entries", []))
                with st.expander(f"{title} ({jumlah} komentar)"):
                    for cmt in item.get("entries", []):
                        cid = cmt["id"]
                        st.write(f"⭐ {cmt['rating']} — **{cmt['nama']}**: {cmt['isi']}")

                        balasan_existing = cmt.get("balasan", "")
                        if balasan_existing:
                            st.caption(f"↳ Balasan admin: {balasan_existing}")

                        balasan_baru = st.text_area(
                            "Tulis / edit balasan admin",
                            value=balasan_existing,
                            key=f"reply_{cid}",
                            height=80
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📨 Kirim Balasan", key=f"send_reply_{cid}", use_container_width=True):
                                if update_reply(cid, balasan_baru.strip()):
                                    st.success("Balasan tersimpan!")
                                    st.rerun()
                        with col_b:
                            if st.button("🗑️ Hapus Komentar", key=f"del_{cid}", use_container_width=True):
                                if delete_comment(cid):
                                    st.rerun()
                        st.divider()
        else:
            st.caption("Belum ada komentar masuk.")

# --- 7. FUNGSI FORMAT HARGA ---
def format_price_ui(ini, kmrn):
    diff = ini - kmrn
    if diff > 0: color, status, icon = "#B3261E", "NAIK", "▲"
    elif diff < 0: color, status, icon = "#1B4332", "TURUN", "▼"
    else: color, status, icon = "#8A8272", "STABIL", "—"

    return (
        f'<div style="line-height:1.2; margin-top:5px;">'
        f'<div style="font-size: 0.75rem; color: #8A8272;">Hari Ini:</div>'
        f'<div style="font-size: 1.12rem; font-weight: 800; color: #22201B;">Rp {ini:,}</div>'
        f'<div style="font-size: 0.7rem; color: #9A9082;">Lalu: Rp {kmrn:,}</div>'
        f'<div style="margin-top: 6px; padding: 2px 8px; border-radius: 4px; background: {color}18; display: inline-block;">'
        f'<span style="color:{color}; font-weight:800; font-size: 0.7rem;">{icon} {status}</span>'
        f'</div></div>'
    )

# --- 7a. FUNGSI TREN OTOMATIS ---
def compute_trending(df, n=6):
    if df.empty:
        return df
    d = df[(df['SATUAN'] != 0) & (df['SATUAN'].astype(str) != "0")].copy()
    if d.empty:
        return d

    def pct_change(now, prev):
        return ((now - prev) / prev.replace(0, pd.NA)) * 100

    d['pct_k'] = pct_change(d['K_INI'], d['K_KMRN'])
    d['pct_b'] = pct_change(d['B_INI'], d['B_KMRN'])
    d['pct'] = d[['pct_k', 'pct_b']].abs().max(axis=1)
    d = d.dropna(subset=['pct'])
    d = d[d['pct'] > 0]
    d = d.sort_values('pct', ascending=False)
    return d.head(n)

# --- 7b. FUNGSI KOMENTAR & RATING ---
def render_stars(value):
    full = int(round(value))
    return "⭐" * full + "☆" * (5 - full)

def render_comment_section(key_id, title):
    section = st.session_state.comments.get(key_id, {"title": title, "entries": []})
    entries = section.get("entries", [])

    with st.form(key=f"form_{key_id}", clear_on_submit=True):
        nama = st.text_input("Nama Anda", key=f"nama_{key_id}", placeholder="Masukkan nama...")
        rating = st.radio(
            "Beri Rating", options=[1, 2, 3, 4, 5], index=4, horizontal=True,
            format_func=lambda x: "⭐" * x, key=f"rating_{key_id}"
        )
        isi = st.text_area("Komentar Anda", key=f"isi_{key_id}", placeholder="Tulis tanggapan atau masukan Anda...")
        submitted = st.form_submit_button("Kirim Komentar", use_container_width=True)
        if submitted:
            if nama.strip() and isi.strip():
                if add_comment(key_id, title, nama.strip(), rating, isi.strip()):
                    st.success("Terima kasih atas komentar Anda!")
                    st.rerun()
            else:
                st.warning("Nama dan komentar tidak boleh kosong.")

    st.write("")

    if entries:
        avg = sum(e["rating"] for e in entries) / len(entries)
        st.markdown(
            f'<span class="rating-badge">{render_stars(avg)} {avg:.1f}/5 dari {len(entries)} komentar</span>',
            unsafe_allow_html=True
        )
    else:
        st.caption("Belum ada komentar. Jadilah yang pertama memberi tanggapan!")

    for e in entries[::-1]:
        st.markdown(f"""
        <div class="comment-box">
            <span class="comment-name">{e['nama']}</span> &nbsp;
            <span style="color:#B8863B;">{render_stars(e['rating'])}</span><br>
            <span>{e['isi']}</span><br>
            <span class="comment-date">{e['tanggal']}</span>
        </div>
        """, unsafe_allow_html=True)

        balasan = e.get("balasan", "")
        if balasan:
            balasan_tanggal = e.get("balasan_tanggal", "")
            st.markdown(f"""
            <div class="reply-box">
                <span class="reply-label">🏛️ Balasan Admin</span><br>
                <span>{balasan}</span><br>
                <span class="reply-date">{balasan_tanggal}</span>
            </div>
            """, unsafe_allow_html=True)

# --- 8. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.markdown('<span class="section-eyebrow">Portal Resmi</span>', unsafe_allow_html=True)
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    hero_img = get_image_path("hero")
    if hero_img:
        st.image(hero_img, use_container_width=True)

    # ------------------------------------------------------------------
    # INFLASI & IHK KABUPATEN NGADA (sumber: spreadsheet pribadi)
    # Cache di-refresh otomatis tiap 30 detik + tombol refresh manual
    # yang bisa dipakai siapa saja (bukan hanya admin) agar grafik
    # langsung menampilkan angka bulan terbaru begitu spreadsheet diedit.
    # ------------------------------------------------------------------
    st.write("")
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown('<span class="section-eyebrow">Data Inflasi</span>', unsafe_allow_html=True)
        st.markdown("### 📊 Inflasi & IHK Kabupaten Ngada 2026")
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", key="refresh_inflasi_public", use_container_width=True):
            _load_inflasi_gabungan_cached.clear()
            st.rerun()

    df_inflasi = load_inflasi_gabungan()
    if is_admin and st.session_state.get("_inflasi_load_error"):
        st.caption("⚠️ Data inflasi belum sempat dimuat dari spreadsheet — lihat detail error di panel Admin.")

    if df_inflasi.empty:
        st.info("Data inflasi belum tersedia. Pastikan sheet 'Inflasi 2026' dan 'IHK 2026' pada spreadsheet Anda sudah terisi dan sudah dibagikan ke akun aplikasi.")
    else:
        # Ambil baris bulan terakhir yang benar-benar punya data (bukan baris kosong
        # yang mungkin ikut kebawa kalau ada sel header ganjil di spreadsheet).
        df_valid = df_inflasi[
            df_inflasi["Inflasi_num"].notna()
            | df_inflasi["IHK"].astype(str).str.strip().ne("")
        ]
        terakhir = df_valid.iloc[-1] if not df_valid.empty else df_inflasi.iloc[-1]

        c1, c2, c3 = st.columns(3)
        if str(terakhir.get("Inflasi YoY (%)", "")).strip():
            c1.metric(f"Inflasi YoY — {terakhir['Bulan']}", f"{terakhir['Inflasi YoY (%)']}")
        if str(terakhir.get("Inflasi MtM (%)", "")).strip():
            c2.metric("Inflasi MtM", f"{terakhir['Inflasi MtM (%)']}")
        if str(terakhir.get("IHK", "")).strip():
            c3.metric("Indeks Harga Konsumen (IHK)", f"{terakhir['IHK']}")

        if df_inflasi["Inflasi_num"].notna().sum() >= 1:
            fig_inf = px.line(
                df_inflasi, x="Bulan", y="Inflasi_num", markers=True,
                labels={"Bulan": "", "Inflasi_num": "Inflasi (%)"},
            )
            fig_inf.update_traces(line_color="#A6432B")
            fig_inf.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#22201B"),
                height=280, margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_inf, use_container_width=True)

        keterangan = str(terakhir.get("Keterangan", "")).strip()
        if keterangan:
            st.markdown(f"""
            <div class="price-card">
                <strong>Keterangan — Inflasi {terakhir['Bulan']} 2026:</strong><br>{keterangan}
            </div>
            """, unsafe_allow_html=True)

        with st.expander("📋 Lihat rincian tiap bulan"):
            st.dataframe(
                df_inflasi[["Bulan", "Inflasi YoY (%)", "Inflasi MtM (%)", "IHK", "Keterangan"]],
                use_container_width=True, hide_index=True,
            )

    # ------------------------------------------------------------------

    st.write("")
    st.markdown('<span class="section-eyebrow">Suara Pengunjung</span>', unsafe_allow_html=True)
    st.markdown("### 💬 Komentar & Rating Pengunjung")
    st.caption("Berikan penilaian dan masukan Anda terhadap website Portal Ekonomi Ngada ini.")
    render_comment_section("website_umum", "Portal Ekonomi Ngada")

elif st.session_state.page == "Harga":
    st.markdown('<span class="section-eyebrow">Data Pasar Terkini</span>', unsafe_allow_html=True)
    st.markdown("### 🛍️ Pantauan Harga Pasar")
    query = st.text_input("🔍 Cari Nama Komoditas...", "").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<div style='background:linear-gradient(120deg,#0F2E22,#1B4332); color:#FBF6EA; padding:9px 16px; border-radius:8px; margin-top:22px; font-weight:700; letter-spacing:0.3px;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div class="flex-container">
                        <div style="flex: 1.2; min-width:100px;">
                            <div style="font-size: 1.1rem; font-weight: 800; color: #1B4332; line-height:1.2; font-family:'Fraunces',serif;">{r['KOMODITAS']}</div>
                            <div style="font-size: 0.85rem; color: #8A8272; margin-top:4px;">Satuan: {r['SATUAN']}</div>
                        </div>
                        <div style="flex: 1; border-left: 1px solid #EDE4CE; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: 800; color: #5B6660; letter-spacing:0.5px;">PEDAGANG BESAR</div>
                            {format_price_ui(r['B_INI'], r['B_KMRN'])}
                        </div>
                        <div style="flex: 1; border-left: 1px solid #EDE4CE; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: 800; color: #5B6660; letter-spacing:0.5px;">PEDAGANG KECIL</div>
                            {format_price_ui(r['K_INI'], r['K_KMRN'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.markdown('<span class="section-eyebrow">Analitik Harga</span>', unsafe_allow_html=True)
    st.subheader("📈 Tren Harga Otomatis")
    st.caption("Komoditas berikut dipilih otomatis oleh sistem berdasarkan persentase perubahan harga terbesar dari data terbaru — tidak perlu diatur manual.")
    if not df_harga.empty:
        n = store.get("tren_jumlah", 6)
        trending = compute_trending(df_harga, n)
        if trending.empty:
            st.info("Belum ada perubahan harga signifikan yang tercatat saat ini.")
        else:
            cols = st.columns(3)
            for i, (_, r) in enumerate(trending.iterrows()):
                diff = r['K_INI'] - r['K_KMRN']
                if diff > 0: color, icon, status = "#B3261E", "▲", "NAIK"
                elif diff < 0: color, icon, status = "#1B4332", "▼", "TURUN"
                else: color, icon, status = "#8A8272", "—", "STABIL"
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="price-card" style="border-left-color:{color};">
                        <div style="font-weight:800; color:#1B4332; font-size:0.95rem; font-family:'Fraunces',serif;">{r['KOMODITAS']}</div>
                        <div style="font-size:1.45rem; font-weight:800; color:{color}; margin-top:4px;">{icon} {r['pct']:.1f}%</div>
                        <div style="font-size:0.75rem; color:#8A8272; margin-top:2px;">{status} · Rp {r['K_INI']:,} /satuan</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.write("")
            fig = px.bar(
                trending, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group',
                labels={'value': 'Harga (Rp)', 'variable': 'Waktu'},
                color_discrete_sequence=['#B8863B', '#1B4332']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Plus Jakarta Sans, sans-serif", color="#22201B"),
                legend_title_text=''
            )
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Media":
    st.markdown('<span class="section-eyebrow">Publikasi</span>', unsafe_allow_html=True)
    st.subheader("📰 Berita Ekonomi & SDA")

    def _is_youtube(url):
        return bool(re.search(r"(youtube\.com/watch|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)", url, re.I))

    def _drive_file_id(url):
        m = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
        return m.group(1) if m else None

    def _is_pdf(url, tipe):
        return url.lower().endswith(".pdf") or "pdf" in tipe

    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="news-card">
                <span class="news-date">{row['Tanggal']}</span>
                <div class="news-title">{row['Kegiatan']}</div>
            </div>
            """, unsafe_allow_html=True)

            link = str(row.get('Link', '')).strip()
            tipe = str(row.get('Tipe', '')).strip().lower()

            if link and "http" in link:
                if _is_youtube(link):
                    st.video(link)
                elif _is_pdf(link, tipe):
                    drive_id = _drive_file_id(link)
                    embed_src = f"https://drive.google.com/file/d/{drive_id}/preview" if drive_id else link
                    st.markdown(
                        f'<iframe src="{embed_src}" width="100%" height="480" '
                        f'style="border:none;border-radius:12px;margin-top:6px;"></iframe>',
                        unsafe_allow_html=True
                    )
                    st.link_button("⬇️ Buka / Unduh PDF", link, use_container_width=True)
                else:
                    st.link_button("📖 Selengkapnya", link, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.markdown('<span class="section-eyebrow">Kekayaan Daerah</span>', unsafe_allow_html=True)
    st.subheader("🏛️ Potensi Daerah Ngada")
    tab1, tab2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with tab1:
        galeri_pertanian = get_galeri("pertanian")
        if galeri_pertanian:
            cols = st.columns(3)
            for i, item in enumerate(galeri_pertanian):
                with cols[i % 3]:
                    st.image(item["src"], caption=item.get("caption", ""), use_container_width=True)
        else:
            st.caption("Belum ada foto di galeri Pertanian.")
        st.write(store["potensi_pertanian"])
    with tab2:
        galeri_pariwisata = get_galeri("pariwisata")
        if galeri_pariwisata:
            cols = st.columns(3)
            for i, item in enumerate(galeri_pariwisata):
                with cols[i % 3]:
                    st.image(item["src"], caption=item.get("caption", ""), use_container_width=True)
        else:
            st.caption("Belum ada foto di galeri Pariwisata.")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.markdown('<span class="section-eyebrow">Profil Instansi</span>', unsafe_allow_html=True)
    st.markdown(f"### Profil Bagian Perekonomian & SDA\n\n{store['about_text']}")

elif st.session_state.page == "Unduh":
    st.markdown('<span class="section-eyebrow">Ekspor Data</span>', unsafe_allow_html=True)
    st.subheader("📥 Unduh Data")
    st.download_button("📥 Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_pasar_ngada.csv", use_container_width=True)
