import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json
import hashlib
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE (PERMANEN) ---
DB_FILE = "settings_db.json"
COMMENTS_FILE = "comments_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Selamat Datang di Portal Resmi Bagian Perekonomian dan SDA Setda Ngada. Kami hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "about_text": "Bagian Perekonomian dan SDA Setda Ngada. Hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "tren_jumlah": 6
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

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        try:
            with open(COMMENTS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_comments(data):
    with open(COMMENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def news_key(row):
    """Bikin ID unik & stabil untuk tiap berita berdasarkan judul+tanggal."""
    raw = f"{row.get('Tanggal','')}-{row.get('Kegiatan','')}"
    return hashlib.md5(raw.encode()).hexdigest()[:10]

# Inisialisasi State agar tidak NameError
if "store" not in st.session_state:
    st.session_state.store = load_settings()

if "comments" not in st.session_state:
    st.session_state.comments = load_comments()

if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

is_admin = st.query_params.get("status") == "set"

# --- 3. HELPER GAMBAR & CSS ---
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_pimpinan = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
img_logo = get_base64("logo_ngada.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(180deg, #EAF6FF 0%, #E0F2FE 40%, #F0F9FF 100%) !important;
    }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    html, body, [data-testid="stWidgetLabel"], .stText, p, h1, h2, h3, h4, h5, h6, span, div, li {{
        color: #0F172A !important;
    }}

    /* ===== HEADER ===== */
    .header-banner {{
        background: linear-gradient(120deg, #0369a1 0%, #059669 100%);
        border-radius: 20px;
        padding: 22px 28px;
        box-shadow: 0 10px 25px rgba(3,105,161,0.25);
        margin-bottom: 6px;
    }}
    .header-banner h2, .header-banner p {{ color: #FFFFFF !important; }}
    .header-banner h2 {{
        margin: 0; font-weight: 800; letter-spacing: 0.5px; font-size: 1.6rem;
    }}
    .header-banner p {{
        margin: 2px 0 0 0; font-size: 1rem; opacity: 0.95; font-weight: 500;
    }}

    .pimpinan-frame {{
        width: 92px; height: 92px; border-radius: 18px; border: 3px solid #FFFFFF;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
        box-shadow: 0 6px 14px rgba(0,0,0,0.2);
    }}
    .logo-mini {{
        position: absolute; bottom: -6px; right: -6px; width: 34px; height: 34px;
        background: white; border-radius: 8px; padding: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }}

    /* ===== NAV BUTTONS ===== */
    .stButton button {{
        background-color: #FFFFFF !important; color: #0369a1 !important;
        border: 1.5px solid #BAE6FD !important;
        border-radius: 10px !important; transition: 0.25s; padding: 8px 10px;
        font-weight: 600 !important;
    }}
    .stButton button:hover {{
        background-color: #0369a1 !important; color: #FFFFFF !important;
        border-color: #0369a1 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(3,105,161,0.3);
    }}
    div[data-testid="stDownloadButton"] button {{
        background: linear-gradient(120deg, #0369a1, #059669) !important;
        color: white !important; border: none !important; font-weight: 700 !important;
        border-radius: 10px !important; padding: 10px !important;
    }}

    /* ===== CARDS ===== */
    .price-card {{
        background: #FFFFFF !important; padding: 15px; border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06); margin-bottom: 12px; border-left: 5px solid #0369a1;
        transition: 0.2s;
    }}
    .price-card:hover {{ box-shadow: 0 8px 18px rgba(0,0,0,0.1); transform: translateY(-2px); }}
    .flex-container {{ display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }}

    .news-card {{
        background: #FFFFFF; border-radius: 16px; padding: 18px 20px; margin-bottom: 16px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.07); border-top: 4px solid #059669;
        transition: 0.25s;
    }}
    .news-card:hover {{ box-shadow: 0 10px 22px rgba(0,0,0,0.12); transform: translateY(-3px); }}
    .news-date {{
        display:inline-block; background:#E0F2FE; color:#0369a1 !important; font-weight:700;
        font-size:0.75rem; padding:3px 10px; border-radius:20px; margin-bottom:8px;
    }}
    .news-title {{ font-size: 1.05rem; font-weight: 700; color:#0F172A !important; line-height:1.35; }}

    .rating-badge {{
        display:inline-block; background:#FEF3C7; color:#92400E !important; font-weight:700;
        font-size:0.8rem; padding:3px 10px; border-radius:20px; margin-top:8px;
    }}

    .comment-box {{
        background:#F8FAFC; border-radius:12px; padding:10px 14px; margin-top:8px;
        border-left: 3px solid #059669;
    }}
    .comment-name {{ font-weight:700; color:#0369a1 !important; font-size:0.9rem; }}
    .comment-date {{ color:#94A3B8 !important; font-size:0.7rem; }}

    section[data-testid="stExpander"] {{
        background:#FFFFFF; border-radius:14px !important; border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06); margin-bottom: 14px;
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
            <h2><span style="background:rgba(255,255,255,0.25); padding:2px 10px; border-radius:8px; margin-right:8px; font-size:0.85em;">SI-PARI</span>KABUPATEN NGADA</h2>
            <p>Bagian Perekonomian & SDA Setda</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
st.divider()

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
        st.subheader("💬 Moderasi Komentar")
        if st.session_state.comments:
            for k, item in st.session_state.comments.items():
                title = item.get("title", k)
                jumlah = len(item.get("entries", []))
                with st.expander(f"{title} ({jumlah} komentar)"):
                    for idx, cmt in enumerate(item.get("entries", [])):
                        st.write(f"⭐ {cmt['rating']} — **{cmt['nama']}**: {cmt['isi']}")
                        if st.button("🗑️ Hapus", key=f"del_{k}_{idx}"):
                            item["entries"].pop(idx)
                            save_comments(st.session_state.comments)
                            st.rerun()
        else:
            st.caption("Belum ada komentar masuk.")

# --- 7. FUNGSI FORMAT HARGA ---
def format_price_ui(ini, kmrn):
    diff = ini - kmrn
    if diff > 0: color, status, icon = "#EF4444", "NAIK", "▲"
    elif diff < 0: color, status, icon = "#10B981", "TURUN", "▼"
    else: color, status, icon = "#64748B", "STABIL", "—"

    return (
        f'<div style="line-height:1.2; margin-top:5px;">'
        f'<div style="font-size: 0.75rem; color: #64748B;">Hari Ini:</div>'
        f'<div style="font-size: 1.1rem; font-weight: bold; color: #1E293B;">Rp {ini:,}</div>'
        f'<div style="font-size: 0.7rem; color: #94A3B8;">Lalu: Rp {kmrn:,}</div>'
        f'<div style="margin-top: 5px; padding: 2px 6px; border-radius: 4px; background: {color}15; display: inline-block;">'
        f'<span style="color:{color}; font-weight:bold; font-size: 0.7rem;">{icon} {status}</span>'
        f'</div></div>'
    )

# --- 7a. FUNGSI TREN OTOMATIS ---
def compute_trending(df, n=6):
    """Ambil komoditas dengan persentase perubahan harga terbesar (naik/turun) secara otomatis."""
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
    if key_id not in st.session_state.comments:
        st.session_state.comments[key_id] = {"title": title, "entries": []}

    entries = st.session_state.comments[key_id]["entries"]

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
            <span style="color:#F59E0B;">{render_stars(e['rating'])}</span><br>
            <span>{e['isi']}</span><br>
            <span class="comment-date">{e['tanggal']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
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
                entries.append({
                    "nama": nama.strip(),
                    "rating": rating,
                    "isi": isi.strip(),
                    "tanggal": datetime.now().strftime("%d %b %Y, %H:%M")
                })
                save_comments(st.session_state.comments)
                st.success("Terima kasih atas komentar Anda!")
                st.rerun()
            else:
                st.warning("Nama dan komentar tidak boleh kosong.")

# --- 8. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

    st.write("")
    st.markdown("### 💬 Komentar & Rating Pengunjung")
    st.caption("Berikan penilaian dan masukan Anda terhadap website Portal Ekonomi Ngada ini.")
    render_comment_section("website_umum", "Portal Ekonomi Ngada")

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Pasar")
    query = st.text_input("🔍 Cari Nama Komoditas...", "").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<div style='background:#0369a1; color:white; padding:8px 15px; border-radius:8px; margin-top:20px; font-weight:bold;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div class="flex-container">
                        <div style="flex: 1.2; min-width:100px;">
                            <div style="font-size: 1.1rem; font-weight: bold; color: #0369a1; line-height:1.2;">{r['KOMODITAS']}</div>
                            <div style="font-size: 0.85rem; color: #64748B; margin-top:4px;">Satuan: {r['SATUAN']}</div>
                        </div>
                        <div style="flex: 1; border-left: 1px solid #eee; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: bold; color: #475569; letter-spacing:0.5px;">PEDAGANG BESAR</div>
                            {format_price_ui(r['B_INI'], r['B_KMRN'])}
                        </div>
                        <div style="flex: 1; border-left: 1px solid #eee; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: bold; color: #475569; letter-spacing:0.5px;">PEDAGANG KECIL</div>
                            {format_price_ui(r['K_INI'], r['K_KMRN'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.page == "Tren":
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
                if diff > 0: color, icon, status = "#EF4444", "▲", "NAIK"
                elif diff < 0: color, icon, status = "#10B981", "▼", "TURUN"
                else: color, icon, status = "#64748B", "—", "STABIL"
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="price-card" style="border-left-color:{color};">
                        <div style="font-weight:700; color:#0369a1; font-size:0.95rem;">{r['KOMODITAS']}</div>
                        <div style="font-size:1.4rem; font-weight:800; color:{color}; margin-top:4px;">{icon} {r['pct']:.1f}%</div>
                        <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">{status} · Rp {r['K_INI']:,} /satuan</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.write("")
            fig = px.bar(
                trending, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group',
                labels={'value': 'Harga (Rp)', 'variable': 'Waktu'},
                color_discrete_sequence=['#94A3B8', '#0369a1']
            )
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Media":
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
    st.subheader("🏛️ Potensi Daerah Ngada")
    tab1, tab2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with tab1:
        c_a, c_b = st.columns(2)
        with c_a:
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Cengkeh Ngada")
        with c_b:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Pertanian")
        st.write(store["potensi_pertanian"])
    with tab2:
        c_c, c_d = st.columns(2)
        with c_c:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena")
        with c_d:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.markdown(f"### Profil Bagian Perekonomian & SDA\n\n{store['about_text']}")

elif st.session_state.page == "Unduh":
    st.download_button("📥 Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_pasar_ngada.csv", use_container_width=True)
