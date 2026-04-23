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
    initial_sidebar_state="collapsed" # Kita sembunyikan sidebar saat awal agar fokus ke tengah
)

# --- 2. LOGIKA MEMORI & NAVIGASI ---
@st.cache_resource
def get_global_settings():
    return {
        "pilihan_admin": [],
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat."
    }

global_settings = get_global_settings()
is_admin = st.query_params.get("status") == "set"

# Inisialisasi halaman aktif jika belum ada
if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

# Fungsi untuk pindah halaman
def pindah_halaman(nama_halaman):
    st.session_state.halaman_aktif = nama_halaman
    st.rerun()

# --- 3. CSS KUSTOM (TAMPILAN MENU TENGAH) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }
    
    /* Tombol Navigasi agar terlihat seperti kartu */
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        height: 60px;
        border: 1px solid #E2E8F0;
        background-color: white;
        transition: all 0.3s ease;
        font-weight: 700;
    }
    .stButton > button:hover {
        border-color: #059669;
        color: #059669 !important;
        background-color: #F0FDF4;
        transform: translateY(-3px);
    }

    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 60px 40px; border-radius: 25px; margin-bottom: 40px; text-align: center;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    .menu-box {
        background: #F8FAFC;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1)
        df_h = df_h.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        return df_h.dropna(subset=['KOMODITAS']), pd.DataFrame() # Berita disederhanakan dulu
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, _ = load_all_data()

# --- 5. LOGIKA TAMPILAN ---

# A. HEADER TOMBOL KEMBALI (Hanya muncul jika tidak di Beranda)
if st.session_state.halaman_aktif != "Beranda":
    if st.button("⬅️ Kembali ke Menu Utama"):
        pindah_halaman("Beranda")
    st.divider()

# B. KONTEN HALAMAN BERANDA (PUSAT NAVIGASI)
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f"""
        <div class="hero-section">
            <h1>{global_settings["hero_title"]}</h1>
            <p>{global_settings["hero_subtitle"]}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center;'>Pilih Layanan Masyarakat:</h3>", unsafe_allow_html=True)
    
    # Grid Menu Navigasi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="menu-box"><h2>🛍️</h2><h4>Harga Pasar</h4><p>Cek harga komoditas hari ini</p></div>', unsafe_allow_html=True)
        if st.button("Lihat Harga ↗️", key="nav_harga"):
            pindah_halaman("Harga")

    with col2:
        st.markdown('<div class="menu-box"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Statistik fluktuasi harga</p></div>', unsafe_allow_html=True)
        if st.button("Lihat Tren ↗️", key="nav_tren"):
            pindah_halaman("Tren")

    with col3:
        st.markdown('<div class="menu-box"><h2>📰</h2><h4>Info Berita</h4><p>Kegiatan & pengumuman</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita ↗️", key="nav_berita"):
            pindah_halaman("Berita")

# C. HALAMAN HARGA KOMODITAS
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Pantauan Harga Komoditas Harian")
    search = st.text_input("🔍 Cari barang (contoh: Beras, Cabe)...")
    
    # Filter dan Tampilkan Data (Gunakan logika card kamu yang lama di sini)
    df_show = df_harga.copy()
    if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
    
    for _, row in df_show.iterrows():
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f"### 📂 {row['KOMODITAS']}")
        else:
            st.info(f"**{row['KOMODITAS']}** ({row['SATUAN']}) - Rp {row['KECIL_INI']}")

# D. HALAMAN TREN
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Fluktuasi Harga")
    st.write("Grafik perbandingan harga kemarin dan hari ini.")
    # Masukkan kode Plotly kamu di sini

# E. MODE ADMIN (Floating atau Sidebar)
if is_admin:
    with st.sidebar:
        st.write("### 🛠️ Panel Admin")
        if st.button("Edit Konten Beranda"):
            pindah_halaman("Admin")

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Pengaturan Portal")
    global_settings["hero_title"] = st.text_input("Judul Hero", global_settings["hero_title"])
    if st.button("Simpan & Kembali"):
        pindah_halaman("Beranda")
