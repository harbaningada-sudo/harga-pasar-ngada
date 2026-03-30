import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Digital Ngada", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. LOGIKA MEMORI PUBLIK ---
@st.cache_resource
def get_global_settings():
    return {
        "pilihan_admin": [],
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat langsung dari sumbernya."
    }

global_settings = get_global_settings()
jalur_rahasia = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM (LOGO DI ATAS FOTO PIMPINAN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    
    .stApp { background-color: #FFFFFF !important; }
    header { background-color: #059669 !important; }

    /* Container khusus Sidebar Header */
    .sidebar-header-container {
        position: relative;
        width: 100%;
        height: 250px;
        border-radius: 0 0 20px 20px;
        overflow: hidden;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 15px;
    }

    .bg-foto {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        object-fit: cover;
        z-index: 1;
        opacity: 0.8; /* Agar background tidak terlalu terang */
    }

    .overlay-content {
        position: relative;
        z-index: 2;
        background: rgba(255, 255, 255, 0.85); /* Kotak putih transparan di pojok */
        padding: 10px;
        border-radius: 10px;
        width: fit-content;
        border: 1px solid rgba(5, 150, 105, 0.3);
    }

    .sidebar-dept-text {
        font-size: 0.75rem;
        font-weight: 800;
        color: #059669 !important;
        line-height: 1.2;
        margin-top: 5px;
    }

    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    .group-header {
        background: #F1F5F9 !important; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; font-weight: 800; border-left: 10px solid #059669;
    }

    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .price-main { font-size: 1.4rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADING ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 5. SIDEBAR DENGAN BACKGROUND FOTO ---
with st.sidebar:
    # Header Sidebar: Foto Bupati sebagai background, Logo & Teks di pojok kiri bawah foto
    file_pimpinan = "Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"
    logo_file = "logo_ngada.png"
    
    # Logika HTML untuk Sidebar Header
    header_html = f"""
    <div class="sidebar-header-container">
        <img src="https://raw.githubusercontent.com/{os.environ.get('GITHUB_REPOSITORY', 'username/repo')}/main/{file_pimpinan}" class="bg-foto">
        <div class="overlay-content">
            <img src="https://raw.githubusercontent.com/{os.environ.get('GITHUB_REPOSITORY', 'username/repo')}/main/{logo_file}" width="50">
            <div class="sidebar-dept-text">
                Bagian Perekonomian dan SDA<br>Setda Kab. Ngada
            </div>
        </div>
    </div>
    """
    # Jika dijalankan lokal/tanpa env github, gunakan file lokal
    if os.path.exists(file_pimpinan) and os.path.exists(logo_file):
        import base64
        def get_base64(path):
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
        
        header_html = f"""
        <div class="sidebar-header-container">
            <img src="data:image/jpeg;base64,{get_base64(file_pimpinan)}" class="bg-foto">
            <div class="overlay-content">
                <img src="data:image/png;base64,{get_base64(logo_file)}" width="40">
                <div class="sidebar-dept-text">
                    Bagian Perekonomian dan SDA<br>Setda Kab. Ngada
                </div>
            </div>
        </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)

    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard Beranda", "📈 Tren Harga Komoditas", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen Smart ASN"
    ])
    
    is_admin = False
    if jalur_rahasia:
        pass_input = st.text_input("🔑 Petugas", type="password")
        if pass_input == "ngada2026":
            is_admin = True
            st.success("Admin Aktif")

# --- 6. KONTEN UTAMA ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        
        col_foto, col_data = st.columns([1, 2])
        with col_foto:
            if os.path.exists("IMG_20251125_111048.jpg"): 
                st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Pasar")
        
        with col_data:
            search = st.text_input("🔍 Cari komoditas...", "")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
            last_header = ""
            for _, row in df_show.iterrows():
                if row['KATEGORI_INDUK'] != last_header:
                    st.markdown(f'<div class="group-header">📂 {row["KATEGORI_INDUK"]}</div>', unsafe_allow_html=True)
                    last_header = row['KATEGORI_INDUK']
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "": continue
                try:
                    h_ini = int(pd.to_numeric(row['HARGA HARI INI'], errors='coerce') or 0)
                    h_kmrn = int(pd.to_numeric(row['HARGA KEMARIN'], errors='coerce') or 0)
                    selisih = h_ini - h_kmrn
                    warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#94A3B8"
                    ikon = "🔺" if selisih > 0 else "🔻" if selisih < 0 else "➖"
                    st.markdown(f'<div class="card-container" style="border-left: 10px solid {warna};"><div style="display: flex; justify-content: space-between; align-items: center;"><div><b>{row["KOMODITAS"]}</b><br><small>Satuan: {row["SATUAN"]}</small></div><div style="text-align: right;"><span class="price-main">Rp {h_ini:,}</span><br><span style="color: {warna}; font-weight: 700;">{ikon} Rp {abs(selisih):,}</span><br><small style="color: #000000;">Kemarin: Rp {h_kmrn:,}</small></div></div></div>', unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Tren Harga")
        # Logika tren tetap sama seperti sebelumnya...
        st.info("Pilih komoditas di panel admin untuk melihat tren.")

    # Menu lain tetap sama...
else:
    st.error("Gagal muat data.")
