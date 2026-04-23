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

# --- 2. LOGIKA NAVIGASI & MEMORI ---
if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def pindah_ke(nama):
    st.session_state.halaman_aktif = nama
    st.rerun()

# --- 3. CSS KUSTOM (HIJAU NGADA & ANTI-ERROR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #F0FDF4 !important; }
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }
    
    /* Hero & Card Styles */
    .hero-box {
        background: linear-gradient(135deg, #059669 0%, #15803D 100%);
        padding: 40px; border-radius: 20px; text-align: center; color: white !important; margin-bottom: 30px;
    }
    .hero-box h1 { color: white !important; font-weight: 800; margin-bottom: 10px; }
    .hero-box p { color: #DCFCE7 !important; }

    .menu-card {
        background: white; border: 1px solid #DCFCE7; padding: 25px; border-radius: 20px; 
        text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.03); min-height: 200px;
    }

    /* Price Card Detail */
    .price-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .price-col { text-align: center; flex: 1; }
    .label-mini { font-size: 0.7rem; color: #64748B; font-weight: 700; text-transform: uppercase; }
    .val-price { font-size: 1.25rem; font-weight: 800; color: #059669; }
    
    .cat-header {
        background: #059669; color: white; padding: 10px 20px; border-radius: 10px; 
        margin-top: 25px; font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. IMAGE HELPER ---
def get_img_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 5. DATA LOADER (DENGAN PROTEKSI ERROR) ---
@st.cache_data(ttl=60)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url, skiprows=1)
        df = df.iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_data()

# --- 6. SIDEBAR (LOGO & PIMPINAN) ---
with st.sidebar:
    logo = get_img_base64("logo-ngada.png")
    if logo: st.markdown(f'<center><img src="data:image/png;base64,{logo}" width="70"></center>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>KABUPATEN NGADA</h4>", unsafe_allow_html=True)
    
    foto = get_img_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if foto: st.image(f"data:image/jpeg;base64,{foto}", use_container_width=True)
    
    st.success("Bagian Perekonomian & SDA")
    st.divider()
    if st.button("🏠 Beranda Utama", use_container_width=True): pindah_ke("Beranda")

# --- 7. LOGIKA HALAMAN ---

# A. HALAMAN BERANDA (SEMUA NAVIGASI DI SINI)
if st.session_state.halaman_aktif == "Beranda":
    st.markdown("""
        <div class="hero-box">
            <h1>Smart Economy Ngada 👋</h1>
            <p>Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.</p>
        </div>
    """, unsafe_allow_html=True)

    # Grid 6 Menu Utama
    st.markdown("<h3 style='text-align:center;'>🎯 Menu Layanan Digital</h3>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="menu-card"><h2>🛍️</h2><h4>Harga Komoditas</h4><p>Pedagang Besar & Kecil</p></div>', unsafe_allow_html=True)
        if st.button("Buka Harga", key="btn1", use_container_width=True): pindah_ke("Harga")
    with m2:
        st.markdown('<div class="menu-card"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Statistik perkembangan</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren", key="btn2", use_container_width=True): pindah_ke("Tren")
    with m3:
        st.markdown('<div class="menu-card"><h2>📰</h2><h4>Media & Berita</h4><p>Info kegiatan terkini</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", key="btn3", use_container_width=True): pindah_ke("Berita")

    m4, m5, m6 = st.columns(3)
    with m4:
        st.markdown('<div class="menu-card"><h2>📥</h2><h4>Pusat Unduhan</h4><p>Data & Dokumen</p></div>', unsafe_allow_html=True)
        if st.button("Buka Unduhan", key="btn4", use_container_width=True): pindah_ke("Unduhan")
    with m5:
        st.markdown('<div class="menu-card"><h2>ℹ️</h2><h4>Tentang Kita</h4><p>Profil & Komitmen</p></div>', unsafe_allow_html=True)
        if st.button("Buka Info", key="btn5", use_container_width=True): pindah_ke("Tentang")
    with m6:
        st.markdown('<div class="menu-card"><h2>🏛️</h2><h4>SDA Ngada</h4><p>Potensi Daerah</p></div>', unsafe_allow_html=True)
        st.button("Segera Hadir", key="btn6", use_container_width=True, disabled=True)

# B. HALAMAN HARGA (DENGAN PROTEKSI VALUEERROR)
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Daftar Harga Komoditas")
    if st.button("⬅️ Kembali ke Menu"): pindah_ke("Beranda")
    
    search = st.text_input("🔍 Cari komoditas...")
    df_f = df_harga.copy()
    if search: df_f = df_f[df_f['KOMODITAS'].str.contains(search, case=False, na=False)]

    for _, row in df_f.iterrows():
        # Handle Kategori
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f'<div class="cat-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            continue
        
        # PROTEKSI DATA (Supaya tidak ValueError)
        def clean_val(val):
            try:
                v = pd.to_numeric(val, errors='coerce')
                return int(v) if not pd.isna(v) else 0
            except: return 0

        b_ini = clean_val(row['B_INI'])
        k_ini = clean_val(row['K_INI'])
        k_kmrn = clean_val(row['K_KMRN'])
        selisih = k_ini - k_kmrn
        
        warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#64748B"
        ikon = "▲" if selisih > 0 else "▼" if selisih < 0 else "—"

        st.markdown(f"""
        <div class="price-container" style="border-left: 8px solid {warna};">
            <div style="flex: 1.5;">
                <b style="font-size: 1.1rem;">{row['KOMODITAS']}</b><br>
                <small style="color: #64748B;">Satuan: {row['SATUAN']}</small>
            </div>
            <div class="price-col">
                <div class="label-mini">Pedagang Besar</div>
                <div class="val-price" style="color: #1E293B;">Rp {b_ini:,}</div>
            </div>
            <div class="price-col" style="border-left: 2px solid #F1F5F9;">
                <div class="label-mini">Pedagang Kecil</div>
                <div class="val-price" style="color: {warna};">Rp {k_ini:,}</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: {warna};">{ikon} {abs(selisih):,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Halaman lainnya (Placeholder agar tidak kosong)
elif st.session_state.halaman_aktif in ["Tren", "Berita", "Unduhan", "Tentang"]:
    st.header(f"📍 Halaman {st.session_state.halaman_aktif}")
    if st.button("⬅️ Kembali ke Menu"): pindah_ke("Beranda")
    st.info(f"Fitur {st.session_state.halaman_aktif} sedang dalam sinkronisasi data.")
