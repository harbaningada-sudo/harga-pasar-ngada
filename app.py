import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Digital Ngada",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOGIKA MEMORI ---
@st.cache_resource
def get_global_settings():
    return {
        "pilihan_admin": [],
        "hero_title": "Smart Economy Ngada",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat."
    }

global_settings = get_global_settings()
is_admin = st.query_params.get("status") == "set"

# State navigasi — None = halaman beranda
if "halaman" not in st.session_state:
    st.session_state.halaman = None

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Open+Sans:wght@400;600&display=swap');

    html, body, [class*="css"], .stMarkdown, p, span, div, label {
        font-family: 'Open Sans', sans-serif;
        color: #1a1a2e !important;
    }
    .stApp { background-color: #f0f4f8 !important; }

    /* Sembunyikan header & sidebar */
    header[data-testid="stHeader"] { background: transparent !important; height: 0px; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* ===== TOPBAR ===== */
    .topbar {
        background: #0a2240;
        padding: 7px 30px;
        display: flex; justify-content: space-between; align-items: center;
        font-size: 0.75rem;
    }
    .topbar span { color: #9db5cc !important; }
    .topbar-links a {
        color: #f59e0b !important; margin-left: 14px;
        text-decoration: none; font-weight: 700;
        font-size: 0.72rem; letter-spacing: 0.5px; text-transform: uppercase;
    }

    /* ===== NAVBAR ===== */
    .navbar {
        background: #ffffff; padding: 0 30px;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 3px solid #f59e0b;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 0;
    }
    .navbar-brand {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.35rem; font-weight: 900;
        color: #0a2240 !important; padding: 14px 0; letter-spacing: -0.5px;
    }
    .navbar-brand span { color: #f59e0b !important; }
    .navbar-menu a {
        color: #374151 !important; text-decoration: none;
        font-family: 'Montserrat', sans-serif; font-weight: 700;
        font-size: 0.75rem; letter-spacing: 0.5px; text-transform: uppercase;
        padding: 18px 14px; display: inline-block;
        border-bottom: 3px solid transparent; margin-bottom: -3px;
        transition: all 0.2s;
    }
    .navbar-menu a:hover { color: #f59e0b !important; border-bottom-color: #f59e0b; }
    .admin-badge-nav {
        background: #f59e0b; color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif; font-weight: 800;
        font-size: 0.68rem; padding: 6px 14px; border-radius: 50px;
        letter-spacing: 0.8px; text-transform: uppercase; display: inline-block;
    }

    /* ===== HERO ===== */
    .hero-wrap {
        background: linear-gradient(135deg, #0a2240 0%, #0e3a6e 60%, #0a2240 100%);
        padding: 80px 60px 100px;
        text-align: center; position: relative; overflow: hidden;
    }
    .hero-wrap::before {
        content: "NGADA"; position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Montserrat', sans-serif;
        font-size: 14rem; font-weight: 900;
        color: rgba(255,255,255,0.025); white-space: nowrap;
        pointer-events: none; letter-spacing: 20px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(245,158,11,0.18); border: 1px solid rgba(245,158,11,0.5);
        color: #f59e0b !important; font-family: 'Montserrat', sans-serif;
        font-size: 0.67rem; font-weight: 700; letter-spacing: 3px;
        text-transform: uppercase; padding: 5px 18px; border-radius: 50px;
        margin-bottom: 18px;
    }
    .hero-wrap h1 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 3rem !important; font-weight: 900 !important;
        color: #ffffff !important; line-height: 1.15 !important;
        margin-bottom: 16px !important;
    }
    .hero-wrap p {
        color: #93b4cc !important; font-size: 1.05rem !important;
        max-width: 560px; margin: 0 auto 35px !important; line-height: 1.75;
    }

    /* ===== CTA BUTTON (Streamlit) ===== */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: #f59e0b !important; color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif !important; font-weight: 800 !important;
        font-size: 0.82rem !important; letter-spacing: 1.5px !important;
        text-transform: uppercase !important; border: none !important;
        border-radius: 50px !important; padding: 14px 36px !important;
        box-shadow: 0 8px 25px rgba(245,158,11,0.4) !important;
    }

    /* ===== 4 MENU CARDS ===== */
    .cards-grid {
        display: grid; grid-template-columns: repeat(4, 1fr);
        background: #fefaf3; border-radius: 20px;
        box-shadow: 0 14px 50px rgba(0,0,0,0.13);
        margin: -30px 10px 35px; position: relative; z-index: 20;
        overflow: hidden; border: 1px solid #e8e2d6;
    }
    .menu-card {
        padding: 38px 22px 30px; text-align: center;
        border-right: 1px solid #ede8df;
        transition: all 0.25s ease;
        position: relative; cursor: pointer;
    }
    .menu-card:last-child { border-right: none; }
    .menu-card:hover { background: #fff8e8; }
    .menu-icon { font-size: 3rem; margin-bottom: 14px; display: block; }
    .menu-card h4 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.82rem !important; font-weight: 800 !important;
        color: #0a2240 !important; text-transform: uppercase;
        letter-spacing: 0.8px; margin-bottom: 8px !important;
    }
    .menu-card p {
        font-size: 0.77rem !important; color: #6b7280 !important;
        line-height: 1.55; margin-bottom: 18px !important;
    }
    .btn-menu {
        display: inline-block; background: #f59e0b; color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 0.68rem;
        letter-spacing: 1px; text-transform: uppercase; padding: 9px 22px;
        border-radius: 50px; text-decoration: none;
        box-shadow: 0 4px 12px rgba(245,158,11,0.3);
    }

    /* Tombol Streamlit transparan menutupi card */
    .stColumn div[data-testid="stButton"] > button {
        opacity: 0 !important; position: absolute !important;
        inset: 0 !important; width: 100% !important; height: 100% !important;
        cursor: pointer !important; z-index: 50 !important;
        border-radius: 0 !important; padding: 0 !important;
    }

    /* ===== PAGE HEADER ===== */
    .page-header {
        padding: 20px 0 12px; border-bottom: 3px solid #f59e0b;
        margin-bottom: 25px; display: flex; align-items: center; gap: 14px;
    }
    .page-header-icon { font-size: 2rem; }
    .page-header-title {
        font-family: 'Montserrat', sans-serif; font-size: 1.5rem;
        font-weight: 900; color: #0a2240 !important;
    }
    .page-header-sub { font-size: 0.8rem; color: #6b7280 !important; margin-top: 3px; }

    /* ===== DATA CARDS ===== */
    .group-header {
        background: linear-gradient(90deg, #0a2240, #163d6e) !important;
        padding: 10px 18px; border-radius: 10px;
        margin-top: 20px; margin-bottom: 8px;
        font-family: 'Montserrat', sans-serif; font-weight: 800;
        font-size: 0.8rem; color: #ffffff !important;
        text-transform: uppercase; letter-spacing: 0.8px;
    }
    .card-container {
        background: white !important; padding: 16px 20px;
        border-radius: 12px; border: 1px solid #e8edf2;
        margin-bottom: 9px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .card-container:hover { box-shadow: 0 5px 18px rgba(0,0,0,0.08); }
    .price-main { font-size: 1.35rem; font-weight: 800; font-family: 'Montserrat', sans-serif; }
    .price-sub { font-size: 0.92rem; font-weight: 700; font-family: 'Montserrat', sans-serif; color: #374151 !important; }
    .price-label-top { font-size: 0.68rem; color: #6b7280 !important; margin-bottom: 3px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .price-box { text-align: right; border-left: 1px solid #f0f4f8; padding-left: 16px; min-width: 138px; }

    /* ===== INFO BOX ===== */
    .info-box {
        background: linear-gradient(135deg, #0a2240, #163d6e);
        padding: 18px; border-radius: 12px; border-left: 4px solid #f59e0b;
        font-size: 0.81rem; line-height: 1.7;
    }
    .info-box, .info-box * { color: #c8daea !important; }
    .info-box b { color: #f59e0b !important; }

    /* ===== SEARCH ===== */
    .stTextInput input {
        border-radius: 50px !important; border: 2px solid #e2e8f0 !important;
        padding: 10px 20px !important;
    }
    .stTextInput input:focus { border-color: #f59e0b !important; box-shadow: 0 0 0 3px rgba(245,158,11,0.12) !important; }

    /* ===== TOMBOL KEMBALI ===== */
    button[data-testid="stBaseButton-secondary"] {
        background: #0a2240 !important; color: white !important;
        border: none !important; border-radius: 50px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important; font-size: 0.75rem !important;
        opacity: 1 !important; position: relative !important;
        width: auto !important; height: auto !important;
        padding: 8px 20px !important;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center; padding: 28px;
        color: #9ca3af !important; font-size: 0.75rem;
        border-top: 1px solid #e5e7eb; margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. IMAGE HELPER ---
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 5. MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1)
        df_h = df_h.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        df_h = df_h.dropna(subset=['KOMODITAS'])

        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# ============================================================
# 6. TOPBAR + NAVBAR
# ============================================================
img_l = get_img_as_base64("logo_ngada.png")
logo_html = f'<img src="data:image/png;base64,{img_l}" height="30" style="vertical-align:middle; margin-right:8px;">' if img_l else "🏛️"
admin_link = "<a href='?'>🔒 Keluar Admin</a>" if is_admin else "<a href='?status=set'>⚙️ Admin</a>"

st.markdown(f"""
<div class="topbar">
    <span>📍 Jl. Soekarno-Hatta, Bajawa, Kabupaten Ngada, NTT</span>
    <div class="topbar-links">
        <a href="#">Facebook</a><a href="#">Twitter</a><a href="#">Instagram</a>
        {admin_link}
    </div>
</div>
<div class="navbar">
    <div class="navbar-brand">{logo_html}NGADA <span>DIGITAL</span></div>
    <div class="navbar-menu">
        <a href="?">🏠 Beranda</a>
        <a href="#">📊 Data Harga</a>
        <a href="#">📰 Berita</a>
        <a href="#">📥 Unduhan</a>
        <a href="#">ℹ️ Tentang</a>
    </div>
    {"<div class='admin-badge-nav'>🔓 Mode Editor</div>" if is_admin else ""}
</div>
""", unsafe_allow_html=True)


# ============================================================
# 7. FUNGSI TIAP HALAMAN
# ============================================================

def render_harga():
    col_back, _ = st.columns([1.2, 6])
    with col_back:
        if st.button("← Kembali", key="back_harga"):
            st.session_state.halaman = None; st.rerun()

    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">🛒</span>
        <div>
            <div class="page-header-title">Data Harga Komoditas</div>
            <div class="page-header-sub">Perbandingan harga hari ini vs kemarin di pasar-pasar Kabupaten Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_admin:
        with st.expander("🛠️ PANEL ADMIN: EDIT HERO"):
            global_settings["hero_title"] = st.text_input("Judul Hero:", value=global_settings["hero_title"])
            global_settings["hero_subtitle"] = st.text_area("Sub-judul:", value=global_settings["hero_subtitle"])
            if st.button("💾 Simpan"): st.rerun()

    col_foto, col_data = st.columns([1, 2.5])
    with col_foto:
        file_foto_pasar = "IMG_20251125_111048.jpg"
        if os.path.exists(file_foto_pasar):
            st.image(file_foto_pasar, use_container_width=True, caption="📸 Dokumentasi Pemantauan Pasar")
        else:
            st.info("💡 Foto belum diunggah.")
        st.markdown("""
            <div class="info-box" style="margin-top:14px;">
                <b>ℹ️ Informasi:</b><br>
                Data diperbarui setiap hari kerja berdasarkan pantauan langsung di pasar-pasar utama Kabupaten Ngada.
            </div>
        """, unsafe_allow_html=True)

    with col_data:
        search = st.text_input("🔍 Cari komoditas...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

        for _, row in df_show.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            try:
                k_ini  = int(pd.to_numeric(row['KECIL_INI'],  errors='coerce') or 0)
                k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                b_ini  = int(pd.to_numeric(row['BESAR_INI'],  errors='coerce') or 0)
                sel = k_ini - k_kmrn
                if sel > 0:   warna, ikon, status = "#DC2626", "🔺", f"NAIK Rp {abs(sel):,}"
                elif sel < 0: warna, ikon, status = "#059669", "🔻", f"TURUN Rp {abs(sel):,}"
                else:         warna, ikon, status = "#94A3B8", "➖", "STABIL"
                st.markdown(f"""
                <div class="card-container" style="border-left:5px solid {warna};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="flex:2;">
                            <b style="font-size:1.02rem; font-family:'Montserrat',sans-serif; color:#0a2240 !important;">{row["KOMODITAS"]}</b><br>
                            <small style="color:#6b7280 !important;">Satuan: {row["SATUAN"]}</small>
                        </div>
                        <div class="price-box">
                            <div class="price-label-top">Pedagang Besar</div>
                            <span class="price-sub">Rp {b_ini:,}</span>
                        </div>
                        <div class="price-box">
                            <div class="price-label-top" style="color:{warna};">Pedagang Kecil</div>
                            <div style="color:{warna}; font-size:0.7rem; font-weight:800; font-family:'Montserrat',sans-serif;">{ikon} {status}</div>
                            <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                            <small style="color:#94a3b8 !important; font-size:0.73rem;">Kemarin: Rp {k_kmrn:,}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except: continue


def render_tren():
    col_back, _ = st.columns([1.2, 6])
    with col_back:
        if st.button("← Kembali", key="back_tren"):
            st.session_state.halaman = None; st.rerun()

    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">💰</span>
        <div>
            <div class="page-header-title">Tren & Analisis Harga</div>
            <div class="page-header-sub">Grafik perbandingan harga komoditas strategis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_v = df_harga.dropna(subset=['SATUAN'])
    if is_admin:
        pilihan_baru = st.multiselect(
            "Pilih komoditas untuk dipublikasikan:",
            options=df_v['KOMODITAS'].unique(),
            default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()]
        )
        if st.button("🚀 Publikasikan"):
            global_settings["pilihan_admin"] = pilihan_baru; st.rerun()

    if global_settings["pilihan_admin"]:
        df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
        df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
        fig = px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group",
                     color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#f59e0b'})
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Montserrat')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Belum ada komoditas yang dipublikasikan." + (" Pilih di atas." if is_admin else " Tunggu pembaruan admin."))


def render_berita():
    col_back, _ = st.columns([1.2, 6])
    with col_back:
        if st.button("← Kembali", key="back_berita"):
            st.session_state.halaman = None; st.rerun()

    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">📊</span>
        <div>
            <div class="page-header-title">Media & Berita</div>
            <div class="page-header-sub">Kegiatan terbaru Bagian Perekonomian Setda Kab. Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for _, row in df_berita.iloc[::-1].iterrows():
        st.markdown(f"""
        <div class="card-container" style="border-left:5px solid #f59e0b;">
            <h3 style="font-family:'Montserrat',sans-serif; font-size:1rem; color:#0a2240 !important;">{row["Kegiatan"]}</h3>
            <p style="color:#6b7280 !important; font-size:0.8rem; margin:0;">📅 {row["Tanggal"]}</p>
        </div>
        """, unsafe_allow_html=True)
        link = str(row['Link'])
        if link.startswith("http"):
            if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']):
                st.image(link, use_container_width=True)
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; color:#0a2240 !important; font-weight:800; padding:9px 20px; background:#f59e0b; border-radius:50px; font-size:0.75rem; font-family:Montserrat,sans-serif; display:inline-block; margin:8px 0 16px;">📂 Lihat Detail</a>', unsafe_allow_html=True)


def render_tentang():
    col_back, _ = st.columns([1.2, 6])
    with col_back:
        if st.button("← Kembali", key="back_tentang"):
            st.session_state.halaman = None; st.rerun()

    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">🏛️</span>
        <div>
            <div class="page-header-title">Resmi & Terpercaya</div>
            <div class="page-header-sub">Komitmen Smart ASN Bagian Perekonomian Setda Kab. Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.6, 1])
    with col1:
        st.markdown(f"""
        <div class="card-container" style="border-left:5px solid #f59e0b;">
            <h3 style="font-family:'Montserrat',sans-serif; color:#0a2240 !important; margin-bottom:10px;">📜 Visi & Misi</h3>
            <p style="color:#374151 !important; line-height:1.85;">{global_settings["about_text"]}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="card-container" style="border-left:5px solid #0a2240; margin-top:12px;"><h3 style="font-family:Montserrat,sans-serif; color:#0a2240 !important;">📥 Pusat Unduhan</h3></div>', unsafe_allow_html=True)
        dl1, dl2 = st.columns(2)
        with dl1: st.download_button("⬇️ CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with dl2: st.download_button("⬇️ CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Media_Ngada.csv", "text/csv", use_container_width=True)
    with col2:
        img_b = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
        if img_b:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_b}" style="width:100%; border-radius:16px; box-shadow:0 8px 25px rgba(0,0,0,0.15);">', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#0a2240; padding:15px; border-radius:12px; margin-top:12px; border-left:4px solid #f59e0b;">
            <div style="color:#f59e0b !important; font-family:'Montserrat',sans-serif; font-weight:800; font-size:0.78rem; margin-bottom:5px;">BAGIAN PEREKONOMIAN & SDA</div>
            <div style="color:#c8daea !important; font-size:0.77rem; line-height:1.65;">Sekretariat Daerah<br>Kabupaten Ngada<br>Nusa Tenggara Timur</div>
        </div>
        """, unsafe_allow_html=True)

    if is_admin:
        with st.expander("🛠️ PANEL ADMIN: EDIT KOMITMEN"):
            global_settings["about_text"] = st.text_area("Isi Komitmen:", value=global_settings["about_text"])
            if st.button("💾 Simpan"): st.success("Diperbarui!"); st.rerun()


# ============================================================
# 8. ROUTER UTAMA
# ============================================================

if st.session_state.halaman is None:
    # ===== BERANDA: Hero + 4 Card Menu =====
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-badge">📍 Kabupaten Ngada, Nusa Tenggara Timur</div>
        <h1>{global_settings["hero_title"]}</h1>
        <p>{global_settings["hero_subtitle"]}</p>
    </div>
    """, unsafe_allow_html=True)

    # Tombol CTA tepat di bawah hero
    sp1, sp2, sp3 = st.columns([2.2, 1.2, 2.2])
    with sp2:
        if st.button("📊 LIHAT DATA HARGA", key="cta_hero", use_container_width=True):
            st.session_state.halaman = "harga"; st.rerun()

    # ===== 4 CARD NAVIGASI =====
    menus = [
        ("🛒", "Data Real-Time",     "Harga diperbarui setiap hari kerja langsung dari pasar", "harga"),
        ("💰", "Harga Transparan",   "Pantau selisih harga pedagang besar dan kecil",           "tren"),
        ("📊", "Analisis Tren",      "Grafik perubahan harga komoditas strategis",              "berita"),
        ("🏛️", "Resmi & Terpercaya", "Dikelola Bagian Perekonomian Setda Kab. Ngada",          "tentang"),
    ]

    st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (icon, title, desc, target) in enumerate(menus):
        with cols[i]:
            st.markdown(f"""
            <div class="menu-card">
                <span class="menu-icon">{icon}</span>
                <h4>{title}</h4>
                <p>{desc}</p>
                <span class="btn-menu">SELENGKAPNYA</span>
            </div>
            """, unsafe_allow_html=True)
            # Tombol transparan — menutupi seluruh card
            if st.button("​", key=f"nav_{target}", use_container_width=True):
                st.session_state.halaman = target; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.halaman == "harga":
    render_harga() if not df_harga.empty else st.error("❌ Data harga tidak tersedia.")

elif st.session_state.halaman == "tren":
    render_tren() if not df_harga.empty else st.error("❌ Data tidak tersedia.")

elif st.session_state.halaman == "berita":
    render_berita()

elif st.session_state.halaman == "tentang":
    render_tentang()

# ===== FOOTER =====
st.markdown("""
<div class="footer">
    © 2025 Portal Ekonomi Digital Ngada &nbsp;·&nbsp;
    Bagian Perekonomian & SDA Setda Kab. Ngada, NTT
</div>
""", unsafe_allow_html=True)
