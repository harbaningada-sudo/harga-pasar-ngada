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
    initial_sidebar_state="auto"
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

# --- 3. CSS KUSTOM (Lombok Transport Style) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Open+Sans:wght@400;600&display=swap');

    /* ===== RESET & BASE ===== */
    html, body, [class*="css"], .stMarkdown, p, span, div, label {
        font-family: 'Open Sans', sans-serif;
        color: #1a1a2e !important;
    }
    .stApp { background-color: #f4f6f9 !important; }

    /* ===== HIDE DEFAULT STREAMLIT HEADER ===== */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px;
    }

    /* ===== TOP NAVBAR (Mirip Lombok Transport) ===== */
    .navbar-top {
        background: #0a2240;
        padding: 8px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        color: #cdd5e0 !important;
    }
    .navbar-top a { color: #f59e0b !important; margin-left: 14px; text-decoration: none; font-weight: 600; }
    .navbar-main {
        background: #ffffff;
        padding: 0 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-bottom: 3px solid #f59e0b;
    }
    .navbar-brand {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.5rem;
        font-weight: 900;
        color: #0a2240 !important;
        padding: 14px 0;
        letter-spacing: -0.5px;
    }
    .navbar-brand span { color: #f59e0b !important; }
    .navbar-links { display: flex; gap: 0; }
    .navbar-links a {
        color: #0a2240 !important;
        text-decoration: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        padding: 20px 18px;
        display: block;
        transition: all 0.2s;
        border-bottom: 3px solid transparent;
        margin-bottom: -3px;
        text-transform: uppercase;
    }
    .navbar-links a:hover, .navbar-links a.active {
        color: #f59e0b !important;
        border-bottom: 3px solid #f59e0b;
    }

    /* ===== HERO SECTION ===== */
    .hero-section {
        background: linear-gradient(135deg, #0a2240 0%, #1a4a7a 50%, #0d3560 100%);
        padding: 90px 60px 80px;
        border-radius: 0 0 30px 30px;
        margin-bottom: 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: "EKONOMI DIGITAL";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Montserrat', sans-serif;
        font-size: 8rem;
        font-weight: 900;
        color: rgba(255,255,255,0.04);
        white-space: nowrap;
        letter-spacing: 10px;
        pointer-events: none;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(245, 158, 11, 0.2);
        border: 1px solid #f59e0b;
        color: #f59e0b !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 6px 20px;
        border-radius: 50px;
        margin-bottom: 20px;
    }
    .hero-section h1 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        color: #FFFFFF !important;
        line-height: 1.15 !important;
        margin-bottom: 18px !important;
        position: relative;
    }
    .hero-section p {
        color: #b0c4de !important;
        font-size: 1.1rem !important;
        max-width: 600px;
        margin: 0 auto 30px !important;
        line-height: 1.7;
    }
    .hero-cta {
        display: inline-block;
        background: #f59e0b;
        color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 14px 36px;
        border-radius: 50px;
        text-decoration: none;
        box-shadow: 0 8px 25px rgba(245,158,11,0.4);
        transition: transform 0.2s;
    }
    .hero-cta:hover { transform: translateY(-2px); }

    /* ===== FEATURE CARDS (Mirip 4 card di Lombok Transport) ===== */
    .features-section {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: -20px 20px 30px;
        overflow: hidden;
        position: relative;
        z-index: 10;
    }
    .feature-card {
        padding: 35px 25px;
        text-align: center;
        border-right: 1px solid #f0f0f0;
        transition: all 0.3s;
    }
    .feature-card:last-child { border-right: none; }
    .feature-card:hover { background: #fff8ec; }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
        display: block;
    }
    .feature-card h4 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #0a2240 !important;
        margin-bottom: 8px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .feature-card p {
        font-size: 0.78rem !important;
        color: #6b7280 !important;
        margin: 0 0 15px !important;
        line-height: 1.5;
    }
    .btn-learn-more {
        display: inline-block;
        background: #f59e0b;
        color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.7rem;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        padding: 8px 20px;
        border-radius: 50px;
        text-decoration: none;
    }

    /* ===== SECTION TITLE ===== */
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.6rem;
        font-weight: 900;
        color: #0a2240 !important;
        margin-bottom: 5px;
    }
    .section-subtitle {
        font-size: 0.85rem;
        color: #6b7280 !important;
        margin-bottom: 20px;
    }
    .section-divider {
        width: 50px; height: 4px;
        background: #f59e0b;
        border-radius: 2px;
        margin-bottom: 25px;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: #0a2240 !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 0;
    }
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        color: #f59e0b !important;
    }

    .sidebar-header-box {
        position: relative; width: 100%; height: 200px;
        border-radius: 12px; overflow: hidden; margin-bottom: 20px;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; z-index: 1; }
    .overlay-info {
        position: absolute; bottom: 10px; left: 10px; z-index: 2;
        background: rgba(10, 34, 64, 0.92); padding: 8px 12px; border-radius: 8px;
        border-left: 3px solid #f59e0b;
    }
    .overlay-info div { color: #e2e8f0 !important; font-size: 0.65rem; font-weight: 600; }

    .sidebar-brand {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1rem;
        font-weight: 900;
        color: #ffffff !important;
        text-align: center;
        padding: 10px 0 5px;
        letter-spacing: 1px;
    }
    .sidebar-brand span { color: #f59e0b !important; }
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin: 15px 0;
    }

    /* ===== DATA CARDS ===== */
    .group-header {
        background: linear-gradient(90deg, #0a2240, #1a4a7a) !important;
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 25px;
        font-weight: 800;
        font-family: 'Montserrat', sans-serif;
        color: #ffffff !important;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
        text-transform: uppercase;
    }

    .card-container {
        background: white !important;
        padding: 18px 22px;
        border-radius: 12px;
        border: 1px solid #e8edf2;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .card-container:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.08); }

    .price-main { font-size: 1.4rem; font-weight: 800; font-family: 'Montserrat', sans-serif; }
    .price-sub { font-size: 0.95rem; font-weight: 700; color: #475569 !important; font-family: 'Montserrat', sans-serif; }
    .price-label-top { font-size: 0.7rem; color: #64748B !important; margin-bottom: 3px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .price-box { text-align: right; border-left: 1px solid #f0f4f8; padding-left: 18px; min-width: 140px; }

    /* ===== SEARCH BOX ===== */
    .stTextInput input {
        border-radius: 50px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 10px 20px !important;
        font-family: 'Open Sans', sans-serif !important;
    }
    .stTextInput input:focus { border-color: #f59e0b !important; box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important; }

    /* ===== INFO BOX ===== */
    .info-box {
        background: linear-gradient(135deg, #0a2240, #1a4a7a);
        padding: 20px;
        border-radius: 12px;
        color: #e2e8f0 !important;
        font-size: 0.82rem;
        line-height: 1.7;
        border-left: 4px solid #f59e0b;
    }
    .info-box b { color: #f59e0b !important; }

    /* ===== ADMIN BADGE ===== */
    .admin-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #0a2240 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 8px 16px;
        border-radius: 50px;
        text-align: center;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 15px;
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

# --- 6. SIDEBAR ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_l = get_img_as_base64("logo_ngada.png")
    st.markdown(f"""
    <div class="sidebar-brand">NGADA <span>DIGITAL</span></div>
    <hr class="sidebar-divider">
    <div class="sidebar-header-box">
        <img src="data:image/jpeg;base64,{img_p}" class="bg-pimpinan">
        <div class="overlay-info">
            <img src="data:image/png;base64,{img_l}" width="30" style="margin-bottom:4px;">
            <div>Bagian Perekonomian & SDA<br>Setda Kab. Ngada</div>
        </div>
    </div>
    <hr class="sidebar-divider">
    """, unsafe_allow_html=True)

    if is_admin:
        st.markdown('<div class="admin-badge">🔓 Mode Editor Aktif</div>', unsafe_allow_html=True)

    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard", "📈 Tren Harga", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen ASN"
    ])

# --- 7. TAMPILAN UTAMA ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard":

        # ===== HERO SECTION =====
        st.markdown(f"""
        <div class="hero-section">
            <div class="hero-badge">📍 Kabupaten Ngada, Nusa Tenggara Timur</div>
            <h1>{global_settings["hero_title"]}</h1>
            <p>{global_settings["hero_subtitle"]}</p>
            <a class="hero-cta" href="#">📊 Lihat Data Harga</a>
        </div>
        """, unsafe_allow_html=True)

        # ===== 4 FEATURE CARDS (mirip Lombok Transport) =====
        st.markdown("""
        <div class="features-section">
            <div class="feature-card">
                <span class="feature-icon">🛒</span>
                <h4>Data Real-Time</h4>
                <p>Harga diperbarui setiap hari kerja langsung dari pasar</p>
                <a class="btn-learn-more" href="#">Selengkapnya</a>
            </div>
            <div class="feature-card">
                <span class="feature-icon">💰</span>
                <h4>Harga Transparan</h4>
                <p>Pantau selisih harga pedagang besar dan kecil</p>
                <a class="btn-learn-more" href="#">Selengkapnya</a>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <h4>Analisis Tren</h4>
                <p>Grafik perubahan harga komoditas strategis</p>
                <a class="btn-learn-more" href="#">Selengkapnya</a>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🏛️</span>
                <h4>Resmi & Terpercaya</h4>
                <p>Dikelola Bagian Perekonomian Setda Kab. Ngada</p>
                <a class="btn-learn-more" href="#">Selengkapnya</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Admin Editor
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT DASHBOARD"):
                global_settings["hero_title"] = st.text_input("Judul:", value=global_settings["hero_title"])
                global_settings["hero_subtitle"] = st.text_area("Sub-judul:", value=global_settings["hero_subtitle"])
                if st.button("💾 Simpan Perubahan"): st.rerun()

        # Layout Utama: 2 Kolom (Kiri: Foto, Kanan: Data)
        col_foto, col_data = st.columns([1, 2.3])

        with col_foto:
            file_foto_pasar = "IMG_20251125_111048.jpg"
            if os.path.exists(file_foto_pasar):
                st.image(file_foto_pasar, use_container_width=True, caption="📸 Dokumentasi Pemantauan Pasar")
            else:
                st.info("💡 Foto dokumentasi belum diunggah.")

            st.divider()
            st.markdown("""
                <div class="info-box">
                    <b>ℹ️ Informasi:</b><br>
                    Data diperbarui setiap hari kerja berdasarkan pantauan langsung di pasar-pasar utama Kabupaten Ngada.
                </div>
            """, unsafe_allow_html=True)

        with col_data:
            # Section Title
            st.markdown("""
                <div class="section-title">📋 Data Harga Komoditas</div>
                <div class="section-subtitle">Perbandingan harga hari ini vs kemarin</div>
                <div class="section-divider"></div>
            """, unsafe_allow_html=True)

            search = st.text_input("🔍 Cari komoditas...", "")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

            for _, row in df_show.iterrows():
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                    st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                    continue

                try:
                    k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                    k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                    b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
                    sel = k_ini - k_kmrn

                    if sel > 0:
                        warna, ikon, status = "#DC2626", "🔺", f"NAIK Rp {abs(sel):,}"
                    elif sel < 0:
                        warna, ikon, status = "#059669", "🔻", f"TURUN Rp {abs(sel):,}"
                    else:
                        warna, ikon, status = "#94A3B8", "➖", "STABIL"

                    st.markdown(f"""
                    <div class="card-container" style="border-left: 5px solid {warna};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;">
                                <b style="font-size:1.05rem; font-family:'Montserrat',sans-serif; color:#0a2240 !important;">{row["KOMODITAS"]}</b><br>
                                <small style="color:#6b7280 !important;">Satuan: {row["SATUAN"]}</small>
                            </div>
                            <div class="price-box">
                                <div class="price-label-top">Pedagang Besar</div>
                                <span class="price-sub">Rp {b_ini:,}</span>
                            </div>
                            <div class="price-box">
                                <div class="price-label-top" style="color:{warna};">Pedagang Kecil</div>
                                <div style="color:{warna}; font-size:0.72rem; font-weight:800; font-family:'Montserrat',sans-serif;">{ikon} {status}</div>
                                <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                                <small style="color: #94a3b8 !important; font-size:0.75rem;">Kemarin: Rp {k_kmrn:,}</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga":
        st.markdown('<div class="section-title">📈 Tren Harga Komoditas</div><div class="section-divider"></div>', unsafe_allow_html=True)
        df_v = df_harga.dropna(subset=['SATUAN'])
        if is_admin:
            pilihan_baru = st.multiselect("Pilih komoditas publik:", options=df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
            if st.button("🚀 Publikasikan"):
                global_settings["pilihan_admin"] = pilihan_baru; st.rerun()

        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group",
                         color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#f59e0b'})
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📰 Media & Berita":
        st.markdown('<div class="section-title">📰 Media & Berita</div><div class="section-divider"></div>', unsafe_allow_html=True)
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="card-container" style="border-left: 5px solid #f59e0b;">
                <h3 style="font-family:'Montserrat',sans-serif; font-size:1.05rem; color:#0a2240 !important;">{row["Kegiatan"]}</h3>
                <p style="color:#6b7280 !important; font-size:0.82rem;">📅 {row["Tanggal"]}</p>
            </div>
            """, unsafe_allow_html=True)
            link = str(row['Link'])
            if link.startswith("http"):
                if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): st.image(link, use_container_width=True)
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; color:#0a2240 !important; font-weight:bold; padding:10px 20px; background:#f59e0b; border-radius:50px; font-size:0.8rem; font-family:Montserrat,sans-serif; display:inline-block; margin-bottom:15px;">📂 Lihat Detail</a>', unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.markdown('<div class="section-title">📥 Pusat Unduhan</div><div class="section-divider"></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1: st.download_button("⬇️ Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2: st.download_button("⬇️ Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Media_Ngada.csv", "text/csv", use_container_width=True)

    elif pilihan == "ℹ️ Komitmen ASN":
        st.markdown('<div class="section-title">ℹ️ Komitmen Smart ASN</div><div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-container" style="border-left: 5px solid #f59e0b;">
            <h3 style="font-family:'Montserrat',sans-serif; color:#0a2240 !important;">Visi & Misi</h3>
            <p style="color:#374151 !important; line-height:1.8;">{global_settings["about_text"]}</p>
        </div>
        """, unsafe_allow_html=True)
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT KOMITMEN"):
                global_settings["about_text"] = st.text_area("Isi:", value=global_settings["about_text"])
                if st.button("💾 Simpan"): st.success("Diperbarui!"); st.rerun()
else:
    st.error("❌ Gagal memuat data. Periksa koneksi internet atau URL Google Sheets.")
