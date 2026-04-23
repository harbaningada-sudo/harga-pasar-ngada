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
    initial_sidebar_state="expanded"
)

# --- 2. LOGIKA NAVIGASI (Sangat Penting) ---
if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

# Fungsi ganti halaman
def ganti_ke(nama_halaman):
    st.session_state.halaman_aktif = nama_halaman

# Data dummy/settings sederhana
hero_title = "Smart Economy Ngada 👋"
hero_subtitle = "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada."

# --- 3. CSS KUSTOM (WARNA HIJAU & HARGA RINCI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Background Full Hijau */
    .stApp { background-color: #F0FDF4 !important; }
    
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #15803D 100%);
        padding: 40px; border-radius: 20px; text-align: center; color: white !important;
        margin-bottom: 30px;
    }
    .hero-section h1 { color: white !important; font-weight: 800; }
    .hero-section p { color: white !important; }

    /* Menu Card di Tengah */
    .menu-card-box {
        background: white; border: 1px solid #DCFCE7;
        padding: 25px; border-radius: 20px; text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Kartu Harga Rinci */
    .price-card {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-group { text-align: center; flex: 1; }
    .price-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
    .price-value { font-size: 1.3rem; font-weight: 800; color: #059669; }
    
    .group-header {
        background: #059669 !important; color: white !important; 
        padding: 10px 20px; border-radius: 10px; margin: 20px 0 10px 0; font-weight: 700;
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
        return df_h.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 6. SIDEBAR (Logo + Foto Pimpinan) ---
with st.sidebar:
    # Logo Kabupaten Ngada
    logo_ngada = get_img_as_base64("logo-ngada.png")
    if logo_ngada:
        st.markdown(f'<center><img src="data:image/png;base64,{logo_ngada}" width="80"></center>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>KABUPATEN NGADA</h3>", unsafe_allow_html=True)

    # Foto Pimpinan
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if img_p:
        st.image(f"data:image/jpeg;base64,{img_p}", use_container_width=True)
    
    st.info("Bagian Perekonomian & SDA Setda Ngada")
    
    # Navigasi Cadangan di Sidebar
    st.divider()
    if st.button("🏠 Beranda Utama", use_container_width=True): ganti_ke("Beranda")

# --- 7. TAMPILAN HALAMAN (LOGIKA UTAMA) ---

# HALAMAN BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-section"><h1>{hero_title}</h1><p>{hero_subtitle}</p></div>', unsafe_allow_html=True)
    
    # Foto Operasi Pasar
    file_foto_pasar = "IMG_20251125_111048.jpg"
    if os.path.exists(file_foto_pasar):
        st.image(file_foto_pasar, use_container_width=True, caption="Kegiatan Operasi Pasar Kabupaten Ngada")
    
    st.divider()
    st.markdown("<h3 style='text-align:center;'>🎯 Menu Layanan Digital</h3>", unsafe_allow_html=True)
    
    # Grid Menu di Tengah
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="menu-card-box"><h2>🛍️</h2><h4>Harga Komoditas</h4><p>Pedagang Besar & Kecil</p></div>', unsafe_allow_html=True)
        if st.button("Buka Harga Pasar", key="nav_h", use_container_width=True):
            ganti_ke("Harga")
            st.rerun()
    with col2:
        st.markdown('<div class="menu-card-box"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Grafik fluktuasi harga</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren Harga", key="nav_t", use_container_width=True):
            ganti_ke("Tren")
            st.rerun()
    with col3:
        st.markdown('<div class="menu-card-box"><h2>📰</h2><h4>Media Berita</h4><p>Kegiatan Perekonomian</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", key="nav_b", use_container_width=True):
            ganti_ke("Berita")
            st.rerun()

# HALAMAN HARGA (Rinci Besar vs Kecil)
elif st.session_state.halaman_aktif == "Harga":
    st.markdown("## 🛍️ Rincian Harga Komoditas")
    if st.button("⬅️ Kembali ke Menu Utama"):
        ganti_ke("Beranda")
        st.rerun()
    
    search = st.text_input("🔍 Cari komoditas...")
    df_show = df_harga.copy()
    if search:
        df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

    for _, row in df_show.iterrows():
        # Kategori/Grup
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            continue
        
        # Ambil Angka
        b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
        k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
        k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
        selisih = k_ini - k_kmrn
        warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#64748B"
        ikon = "▲" if selisih > 0 else "▼" if selisih < 0 else "—"

        # Tampilan HTML Kartu Rinci (Besar vs Kecil)
        st.markdown(f"""
        <div class="price-card" style="border-left: 8px solid {warna};">
            <div style="flex: 1.5;">
                <b style="font-size: 1.1rem;">{row['KOMODITAS']}</b><br>
                <small>Satuan: {row['SATUAN']}</small>
            </div>
            <div class="price-group">
                <div class="price-label">Pedagang Besar</div>
                <div class="price-value" style="color: #1E293B;">Rp {b_ini:,}</div>
            </div>
            <div class="price-group" style="border-left: 2px solid #F1F5F9;">
                <div class="price-label">Pedagang Kecil</div>
                <div class="price-value" style="color: {warna};">Rp {k_ini:,}</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: {warna};">
                    {ikon} {abs(selisih):,}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# HALAMAN TREN/BERITA (Placeholder)
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Fluktuasi Harga")
    if st.button("⬅️ Kembali"): ganti_ke("Beranda"); st.rerun()
    st.info("Halaman Tren sedang memuat data grafik...")

elif st.session_state.halaman_aktif == "Berita":
    st.header("📰 Media & Berita Terkini")
    if st.button("⬅️ Kembali"): ganti_ke("Beranda"); st.rerun()
    st.info("Daftar berita kegiatan sedang diperbarui...")
