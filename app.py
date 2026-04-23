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
# Tetap menggunakan query params agar URL tidak berubah
is_admin = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM (DIPERBARUI UNTUK MENU LAYANAN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 60px 40px; border-radius: 20px; margin-bottom: 30px; text-align: center;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    /* Card Menu Layanan di Beranda */
    .menu-card {
        background: #f8fafc; border: 2px solid #e2e8f0; padding: 25px;
        border-radius: 15px; text-align: center; transition: 0.3s;
        cursor: pointer; height: 100%;
    }
    .menu-card:hover { border-color: #059669; background: #f0fdf4; transform: translateY(-5px); }
    
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
    .price-main { font-size: 1.4rem; font-weight: 800; }
    .price-box { text-align: right; border-left: 1px solid #EEE; padding-left: 15px; min-width: 140px; }
    
    /* Sidebar Styling */
    .sidebar-header-box {
        position: relative; width: 100%; height: 180px;
        border-radius: 15px; overflow: hidden; margin-bottom: 20px;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; }
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
    <div class="sidebar-header-box">
        <img src="data:image/jpeg;base64,{img_p}" class="bg-pimpinan">
    </div>
    """, unsafe_allow_html=True)

    if is_admin: st.success("🔓 MODE EDITOR AKTIF")
    
    # Navigasi Utama
    pilihan = st.radio("Pilih Halaman:", [
        "🏠 Beranda", "🛍️ Layanan Harga Komoditas", "📈 Tren & Grafik", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Informasi"
    ])

# --- 7. TAMPILAN UTAMA ---

# HALAMAN 1: BERANDA (Tampilan Menu Layanan di Tengah)
if pilihan == "🏠 Beranda":
    st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    st.subheader("🎯 Menu Layanan Digital")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="menu-card"><h3>🛍️</h3><b>Harga Komoditas</b><p>Pantau harga harian pasar</p></div>', unsafe_allow_html=True)
        if st.button("Buka Harga", use_container_width=True):
            st.info("Pilih '🛍️ Layanan Harga Komoditas' di menu samping")
            
    with c2:
        st.markdown('<div class="menu-card"><h3>📈</h3><b>Tren Ekonomi</b><p>Grafik perkembangan harga</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren", use_container_width=True):
            st.info("Pilih '📈 Tren & Grafik' di menu samping")

    with c3:
        st.markdown('<div class="menu-card"><h3>📰</h3><b>Berita</b><p>Kegiatan & Info terkini</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", use_container_width=True):
            st.info("Pilih '📰 Media & Berita' di menu samping")

# HALAMAN 2: LAYANAN DATA KOMODITAS (Data dibungkus di sini)
elif pilihan == "🛍️ Layanan Harga Komoditas":
    st.title("🛍️ Data Harga Komoditas Harian")
    
    col_foto, col_data = st.columns([1, 2.5])
    
    with col_foto:
        file_foto_pasar = "IMG_20251125_111048.jpg"
        if os.path.exists(file_foto_pasar):
            st.image(file_foto_pasar, use_container_width=True, caption="Pantauan Pasar")
        st.info("Data ini diperbarui langsung oleh petugas pasar setiap hari kerja.")
        
    with col_data:
        search = st.text_input("🔍 Cari Nama Barang...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
        
        for _, row in df_show.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            
            try:
                k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                sel = k_ini - k_kmrn
                warna = "#DC2626" if sel > 0 else "#059669" if sel < 0 else "#94A3B8"
                ikon = "🔺" if sel > 0 else "🔻" if sel < 0 else "➖"

                st.markdown(f"""
                <div class="card-container" style="border-left: 10px solid {warna};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 2;">
                            <b style="font-size:1.1rem;">{row["KOMODITAS"]}</b><br>
                            <small>Satuan: {row["SATUAN"]}</small>
                        </div>
                        <div class="price-box">
                            <div style="color:{warna}; font-size:0.75rem; font-weight:800;">{ikon} Rp {abs(sel):,}</div>
                            <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except: continue

# HALAMAN 3: TREN HARGA
elif pilihan == "📈 Tren & Grafik":
    st.title("📈 Analisis Tren Harga")
    df_v = df_harga.dropna(subset=['SATUAN'])
    
    if is_admin:
        with st.expander("⚙️ Pengaturan Grafik Publik"):
            pilihan_baru = st.multiselect("Pilih komoditas yang ingin ditampilkan:", options=df_v['KOMODITAS'].unique(), default=global_settings["pilihan_admin"])
            if st.button("Simpan Tampilan"):
                global_settings["pilihan_admin"] = pilihan_baru
                st.rerun()

    if global_settings["pilihan_admin"]:
        df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
        df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
        fig = px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group", color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#059669'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada komoditas yang dipilih untuk ditampilkan grafiknya.")

# HALAMAN LAINNYA (MEDIA, DOWNLOAD, DLL) TETAP SAMA
elif pilihan == "📰 Media & Berita":
    st.title("📰 Media & Berita")
    for _, row in df_berita.iloc[::-1].iterrows():
        st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
        link = str(row['Link'])
        if link.startswith("http"):
            if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): st.image(link, use_container_width=True)
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; color:#059669; font-weight:bold;">🔗 Baca Selengkapnya</a>', unsafe_allow_html=True)

elif pilihan == "📥 Pusat Unduhan":
    st.title("📥 Pusat Unduhan Data")
    st.download_button("📥 Download Data Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv")

elif pilihan == "ℹ️ Informasi":
    st.title("ℹ️ Tentang Portal")
    st.info(global_settings["about_text"])
    if is_admin:
        new_about = st.text_area("Edit Info:", value=global_settings["about_text"])
        if st.button("Update"):
            global_settings["about_text"] = new_about
            st.rerun()
