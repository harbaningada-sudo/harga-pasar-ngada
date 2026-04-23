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
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat."
    }

global_settings = get_global_settings()
is_admin = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM (UNTUK KARTU MENU DI TENGAH) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }

    /* Hero Section */
    .hero-section {
        background: #059669;
        padding: 50px 20px;
        border-radius: 20px;
        margin-bottom: 40px;
        text-align: center;
        color: white !important;
    }
    .hero-section h1 { color: white !important; font-weight: 800; font-size: 3rem; margin-bottom: 10px; }
    .hero-section p { color: white !important; font-size: 1.2rem; }

    /* Container Menu */
    .menu-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        transition: all 0.3s ease;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    .menu-card:hover {
        border-color: #059669;
        background: #F0FDF4;
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .menu-icon { font-size: 3rem; margin-bottom: 15px; }
    .menu-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 5px; }
    .menu-desc { font-size: 0.9rem; color: #64748B !important; }

    /* Style Data Komoditas */
    .group-header {
        background: #F1F5F9 !important; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; font-weight: 800; border-left: 10px solid #059669;
    }
    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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

# --- 6. NAVIGASI LOGIC ---
# Kita gunakan session_state agar klik tombol di tengah bisa mengubah halaman
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Beranda"

# --- 7. SIDEBAR ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    st.markdown(f'<img src="data:image/jpeg;base64,{img_p}" style="width:100%; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)

    if is_admin: st.success("🔓 MODE EDITOR AKTIF")
    
    # Sinkronisasi radio button dengan session_state
    pilihan = st.radio("Navigasi:", 
                      ["🏠 Beranda", "🛍️ Harga Komoditas", "📈 Tren Harga", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen ASN"],
                      index=["🏠 Beranda", "🛍️ Harga Komoditas", "📈 Tren Harga", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen ASN"].index(st.session_state.page),
                      key="sidebar_nav")
    st.session_state.page = pilihan

# --- 8. TAMPILAN UTAMA ---

# --- HALAMAN BERANDA (DENGAN MENU DI TENGAH) ---
if st.session_state.page == "🏠 Beranda":
    st.markdown(f"""
        <div class="hero-section">
            <h1>{global_settings["hero_title"]}</h1>
            <p>{global_settings["hero_subtitle"]}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Menu Layanan Digital")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="menu-card">
                <div class="menu-icon">🛍️</div>
                <div class="menu-title">Harga Komoditas</div>
                <div class="menu-desc">Pantau harga harian pasar secara real-time.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Buka Harga", use_container_width=True, key="btn_harga"):
            st.session_state.page = "🛍️ Harga Komoditas"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="menu-card">
                <div class="menu-icon">📈</div>
                <div class="menu-title">Tren Ekonomi</div>
                <div class="menu-desc">Grafik perkembangan dan fluktuasi harga.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Buka Tren", use_container_width=True, key="btn_tren"):
            st.session_state.page = "📈 Tren Harga"
            st.rerun()

    with col3:
        st.markdown("""
            <div class="menu-card">
                <div class="menu-icon">📰</div>
                <div class="menu-title">Media & Berita</div>
                <div class="menu-desc">Kegiatan Pemerintah dan info ekonomi terkini.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Buka Berita", use_container_width=True, key="btn_berita"):
            st.session_state.page = "📰 Media & Berita"
            st.rerun()

# --- HALAMAN HARGA KOMODITAS (BUNGKUS DATA DI SINI) ---
elif st.session_state.page == "🛍️ Harga Komoditas":
    st.title("🛍️ Pantauan Harga Komoditas")
    
    col_foto, col_data = st.columns([1, 2.3])
    
    with col_foto:
        file_foto_pasar = "IMG_20251125_111048.jpg"
        if os.path.exists(file_foto_pasar):
            st.image(file_foto_pasar, use_container_width=True, caption="Dokumentasi Pasar")
        st.info("Data diperbarui setiap hari kerja oleh tim teknis lapangan.")

    with col_data:
        search = st.text_input("🔍 Cari komoditas...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
        
        for _, row in df_show.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            
            # (Logika tampilan kartu harga tetap sama seperti sebelumnya)
            st.markdown(f"""
                <div class="card-container">
                    <b>{row['KOMODITAS']}</b> ({row['SATUAN']}) <br>
                    <small>Harga: Rp {pd.to_numeric(row['KECIL_INI'], errors='coerce'):,}</small>
                </div>
            """, unsafe_allow_html=True)

# (Sisa halaman lainnya tetap sama)
elif st.session_state.page == "📈 Tren Harga":
    st.title("📈 Tren Harga")
    # ... isi tren harga ...

elif st.session_state.page == "📰 Media & Berita":
    st.title("📰 Media & Berita")
    # ... isi berita ...

elif st.session_state.page == "📥 Pusat Unduhan":
    st.title("📥 Pusat Unduhan")
    st.download_button("Download CSV Harga", df_harga.to_csv().encode('utf-8'), "harga.csv")

elif st.session_state.page == "ℹ️ Komitmen ASN":
    st.title("ℹ️ Komitmen ASN")
    st.write(global_settings["about_text"])
