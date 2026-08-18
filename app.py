import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json
import hashlib
import uuid
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
        "image_files": {}
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

# --- 3a. GAMBAR YANG BISA DIUPLOAD ADMIN (tanpa perlu push ke GitHub) ---
# Setiap slot punya file default (bawaan dari GitHub). Jika admin upload gambar baru,
# nama file custom disimpan di settings_db.json dan dipakai duluan; jika tidak ada / file
# hilang, otomatis fallback ke file default.
IMAGE_SLOTS = {
    "hero":    {"label": "Foto Beranda (Hero)",              "default": "IMG_20251125_111048.jpg"},
    "cengkeh": {"label": "Pertanian — Cengkeh",               "default": "cengkeh.jpeg"},
    "sawah":   {"label": "Pertanian — Sawah / Hortikultura",  "default": "sawah ngada.webp"},
    "bena":    {"label": "Pariwisata — Kampung Adat Bena",    "default": "bena.webp"},
    "riung":   {"label": "Pariwisata — 17 Pulau Riung",       "default": "17 pulau riung.webp"},
}

def get_image_path(slot):
    """Ambil path gambar aktif untuk sebuah slot: custom upload admin (jika ada & valid), else default."""
    custom = st.session_state.store.get("image_files", {}).get(slot)
    if custom and os.path.exists(custom):
        return custom
    default = IMAGE_SLOTS[slot]["default"]
    if os.path.exists(default):
        return default
    return None

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
        st.subheader("🖼️ Kelola Gambar")
        st.caption("Unggah gambar untuk mengganti foto di halaman Beranda & Potensi — langsung tersimpan di server, tanpa perlu upload ke GitHub.")
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
                    ext = os.path.splitext(uploaded_img.name)[1].lower()
                    new_filename = f"custom_{slot}{ext}"
                    with open(new_filename, "wb") as f:
                        f.write(uploaded_img.getbuffer())
                    st.session_state.store.setdefault("image_files", {})[slot] = new_filename
                    save_settings(st.session_state.store)
                    st.success(f"{info['label']} berhasil diperbarui!")
                    st.rerun()

                if st.session_state.store.get("image_files", {}).get(slot):
                    if st.button("↩️ Kembalikan ke Gambar Default", key=f"reset_img_{slot}", use_container_width=True):
                        st.session_state.store["image_files"].pop(slot, None)
                        save_settings(st.session_state.store)
                        st.rerun()

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
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="news-card">
                <span class="news-date">{row['Tanggal']}</span>
                <div class="news-title">{row['Kegiatan']}</div>
            </div>
            """, unsafe_allow_html=True)

            if "http" in str(row['Link']):
                st.link_button("📖 Selengkapnya", row['Link'], use_container_width=True)

elif st.session_state.page == "Potensi":
    st.markdown('<span class="section-eyebrow">Kekayaan Daerah</span>', unsafe_allow_html=True)
    st.subheader("🏛️ Potensi Daerah Ngada")
    tab1, tab2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with tab1:
        c_a, c_b = st.columns(2)
        with c_a:
            img_cengkeh = get_image_path("cengkeh")
            if img_cengkeh: st.image(img_cengkeh, caption="Cengkeh Ngada")
        with c_b:
            img_sawah = get_image_path("sawah")
            if img_sawah: st.image(img_sawah, caption="Pertanian")
        st.write(store["potensi_pertanian"])
    with tab2:
        c_c, c_d = st.columns(2)
        with c_c:
            img_bena = get_image_path("bena")
            if img_bena: st.image(img_bena, caption="Kampung Bena")
        with c_d:
            img_riung = get_image_path("riung")
            if img_riung: st.image(img_riung, caption="Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.markdown('<span class="section-eyebrow">Profil Instansi</span>', unsafe_allow_html=True)
    st.markdown(f"### Profil Bagian Perekonomian & SDA\n\n{store['about_text']}")

elif st.session_state.page == "Unduh":
    st.markdown('<span class="section-eyebrow">Ekspor Data</span>', unsafe_allow_html=True)
    st.subheader("📥 Unduh Data")
    st.download_button("📥 Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_pasar_ngada.csv", use_container_width=True)
