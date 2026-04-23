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

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def pindah_halaman(nama_halaman):
    st.session_state.halaman_aktif = nama_halaman
    st.rerun()

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    
    /* Sidebar Photo Only */
    .sidebar-header-box {
        position: relative; width: 100%; height: 180px;
        border-radius: 15px; overflow: hidden; margin-bottom: 10px;
        border: 2px solid #059669;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px; text-align: center;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    /* Menu Card di Tengah */
    .menu-card-box {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        padding: 20px; border-radius: 20px; text-align: center;
        transition: 0.3s; min-height: 180px; display: flex; flex-direction: column; justify-content: center;
    }
    .menu-card-box:hover { border-color: #059669; background: #F0FDF4; transform: translateY(-5px); }

    /* Data Cards */
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
        
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h.dropna(subset=['KOMODITAS']), df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 6. SIDEBAR (Hanya Foto Pimpinan & Info Singkat) ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if img_p:
        st.markdown(f'<div class="sidebar-header-box"><img src="data:image/jpeg;base64,{img_p}" class="bg-pimpinan"></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#F0FDF4; border-radius:10px;">
            <small><b>Bagian Perekonomian & SDA</b><br>Setda Kabupaten Ngada</small>
        </div>
    """, unsafe_allow_html=True)
    
    if is_admin:
        st.divider()
        st.success("🔓 MODE EDITOR")
        if st.button("🛠️ Panel Admin Beranda", use_container_width=True): pindah_halaman("Admin")
        if st.button("🏠 Kembali Ke Beranda", use_container_width=True): pindah_halaman("Beranda")

# --- 7. LOGIKA HALAMAN ---

# A. BERANDA (PUSAT NAVIGASI SATU-SATUNYA)
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    col_img, col_txt = st.columns([1.5, 1])
    with col_img:
        file_foto_pasar = "IMG_20251125_111048.jpg"
        if os.path.exists(file_foto_pasar):
            st.image(file_foto_pasar, use_container_width=True, caption="Dokumentasi Operasi Pasar")
    with col_txt:
        st.markdown("### Visi & Misi")
        st.write(global_settings["about_text"])

    st.divider()
    st.markdown("<h3 style='text-align:center;'>🎯 Menu Layanan Utama</h3>", unsafe_allow_html=True)
    
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    with row1_c1:
        st.markdown('<div class="menu-card-box"><h2>🛍️</h2><h4>Harga Komoditas</h4><p>Cek harga pasar harian</p></div>', unsafe_allow_html=True)
        if st.button("Buka Harga", key="nav1", use_container_width=True): pindah_halaman("Harga")
    with row1_c2:
        st.markdown('<div class="menu-card-box"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Grafik harga terbaru</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren", key="nav2", use_container_width=True): pindah_halaman("Tren")
    with row1_c3:
        st.markdown('<div class="menu-card-box"><h2>📰</h2><h4>Media & Berita</h4><p>Info kegiatan terkini</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", key="nav3", use_container_width=True): pindah_halaman("Berita")

    row2_c1, row2_c2, row2_c3 = st.columns(3)
    with row2_c1:
        st.markdown('<div class="menu-card-box"><h2>📥</h2><h4>Pusat Unduhan</h4><p>Ambil data CSV</p></div>', unsafe_allow_html=True)
        if st.button("Buka Unduhan", key="nav4", use_container_width=True): pindah_halaman("Unduhan")
    with row2_c2:
        st.markdown('<div class="menu-card-box"><h2>ℹ️</h2><h4>Tentang Kita</h4><p>Komitmen Smart ASN</p></div>', unsafe_allow_html=True)
        if st.button("Buka Info", key="nav5", use_container_width=True): pindah_halaman("Tentang")
    with row2_c3:
        st.markdown('<div class="menu-card-box"><h2>📞</h2><h4>Kontak</h4><p>Hubungi Setda Ngada</p></div>', unsafe_allow_html=True)
        st.button("Hubungi Kami", key="nav6", use_container_width=True, disabled=True)

# B. HARGA
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Pantauan Harga Komoditas")
    if st.button("⬅️ Kembali ke Menu Utama"): pindah_halaman("Beranda")
    search = st.text_input("🔍 Cari komoditas...")
    df_show = df_harga.copy()
    if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
    for _, row in df_show.iterrows():
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f'<div style="background:#F1F5F9; padding:10px; border-radius:10px; margin-top:20px; font-weight:800; border-left:8px solid #059669;">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            continue
        st.markdown(f'<div class="card-container"><b>{row["KOMODITAS"]}</b> ({row["SATUAN"]}) <br> <span style="color:#059669; font-size:1.2rem; font-weight:800;">Rp {pd.to_numeric(row["KECIL_INI"], errors="coerce"):,}</span></div>', unsafe_allow_html=True)

# C. TREN
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Grafik Harga")
    if st.button("⬅️ Kembali ke Menu Utama"): pindah_halaman("Beranda")
    df_v = df_harga.dropna(subset=['SATUAN'])
    if is_admin:
        with st.expander("🛠️ PANEL ADMIN: PUBLIKASIKAN TREN"):
            pilihan_baru = st.multiselect("Pilih komoditas:", options=df_v['KOMODITAS'].unique(), default=global_settings["pilihan_admin"])
            if st.button("🚀 Publikasikan"):
                global_settings["pilihan_admin"] = pilihan_baru; st.rerun()
    if global_settings["pilihan_admin"]:
        df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
        df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
        st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group", color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#059669'}), use_container_width=True)

# D. BERITA
elif st.session_state.halaman_aktif == "Berita":
    st.header("📰 Media & Berita Terkini")
    if st.button("⬅️ Kembali ke Menu Utama"): pindah_halaman("Beranda")
    for _, row in df_berita.iloc[::-1].iterrows():
        st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
        link = str(row['Link'])
        if link.startswith("http"):
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; background:#059669; color:white; padding:8px 15px; border-radius:8px; font-weight:bold;">🔗 Lihat Selengkapnya</a>', unsafe_allow_html=True)
        st.divider()

# E. UNDUHAN & TENTANG (Logika Minimalis)
elif st.session_state.halaman_aktif == "Unduhan":
    st.header("📥 Pusat Unduhan")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    st.download_button("Download Data Harga", df_harga.to_csv(index=False).encode('utf-8'), "Data_Harga_Ngada.csv")

elif st.session_state.halaman_aktif == "Tentang":
    st.header("ℹ️ Tentang Kami")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    st.info(global_settings["about_text"])

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    global_settings["hero_title"] = st.text_input("Judul Hero", global_settings["hero_title"])
    global_settings["hero_subtitle"] = st.text_area("Sub-judul", global_settings["hero_subtitle"])
    if st.button("Simpan"): pindah_halaman("Beranda")
