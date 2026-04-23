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

# Inisialisasi navigasi
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
    
    /* Sidebar Header */
    .sidebar-header-box {
        position: relative; width: 100%; height: 200px;
        border-radius: 15px; overflow: hidden; margin-bottom: 20px;
        border: 2px solid #059669;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; }

    /* Hero & Menu Cards */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px; text-align: center;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    .menu-card-box {
        background: #F8FAFC; border: 1px solid #E2E8F0;
        padding: 25px; border-radius: 20px; text-align: center;
        transition: 0.3s;
    }
    .menu-card-box:hover { border-color: #059669; background: #F0FDF4; transform: translateY(-5px); }

    /* Data Cards */
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

# --- 6. SIDEBAR (Foto Bupati Tetap di Sini) ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if img_p:
        st.markdown(f'<div class="sidebar-header-box"><img src="data:image/jpeg;base64,{img_p}" class="bg-pimpinan"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🏛️ Menu Navigasi")
    if st.button("🏠 Beranda Utama", use_container_width=True): pindah_halaman("Beranda")
    
    if is_admin:
        st.divider()
        st.success("🔓 MODE EDITOR")
        if st.button("🛠️ Edit Konten Beranda", use_container_width=True): pindah_halaman("Admin")

# --- 7. LOGIKA HALAMAN ---

# A. HALAMAN BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    # Foto Operasi Pasar di Beranda
    col_img, col_txt = st.columns([1.5, 1])
    with col_img:
        file_foto_pasar = "IMG_20251125_111048.jpg"
        if os.path.exists(file_foto_pasar):
            st.image(file_foto_pasar, use_container_width=True, caption="Kegiatan Operasi Pasar Kabupaten Ngada")
    with col_txt:
        st.markdown("### Selamat Datang")
        st.write("Silakan pilih menu layanan di bawah ini untuk mengakses informasi harga komoditas dan berita terkini secara transparan.")

    st.divider()
    
    # Grid Navigasi Utama di Tengah
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="menu-card-box"><h2>🛍️</h2><h4>Harga Komoditas</h4><p>Pantau harga harian</p></div>', unsafe_allow_html=True)
        if st.button("Buka Data Harga", use_container_width=True): pindah_halaman("Harga")
    with c2:
        st.markdown('<div class="menu-card-box"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Grafik fluktuasi harga</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren Harga", use_container_width=True): pindah_halaman("Tren")
    with c3:
        st.markdown('<div class="menu-card-box"><h2>📰</h2><h4>Media & Berita</h4><p>Info kegiatan terbaru</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", use_container_width=True): pindah_halaman("Berita")

# B. HALAMAN HARGA (Logika kartu lengkap seperti sebelumnya)
elif st.session_state.halaman_aktif == "Harga":
    st.markdown("### 🛍️ Daftar Harga Komoditas Terkini")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    
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
            warna = "#DC2626" if sel > 0 else "#059669" if sel < 0 else "#94A3B8"
            ikon = "🔺" if sel > 0 else "🔻" if sel < 0 else "➖"
            status = f"NAIK Rp {abs(sel):,}" if sel > 0 else f"TURUN Rp {abs(sel):,}" if sel < 0 else "STABIL"

            st.markdown(f"""
            <div class="card-container" style="border-left: 10px solid {warna};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 2;">
                        <b style="font-size:1.15rem;">{row["KOMODITAS"]}</b><br>
                        <small>Satuan: {row["SATUAN"]}</small>
                    </div>
                    <div class="price-box">
                        <div style="font-size:0.75rem; color:#64748B;">Pedagang Besar</div>
                        <span style="font-weight:600;">Rp {b_ini:,}</span>
                    </div>
                    <div class="price-box">
                        <div style="color:{warna}; font-size:0.75rem; font-weight:800;">{ikon} {status}</div>
                        <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                        <small style="color: #64748B;">Kemarin: Rp {k_kmrn:,}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except: continue

# C. HALAMAN TREN
elif st.session_state.halaman_aktif == "Tren":
    st.markdown("### 📈 Tren Harga")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    
    df_v = df_harga.dropna(subset=['SATUAN'])
    pilih = st.multiselect("Pilih Komoditas:", options=df_v['KOMODITAS'].unique(), default=df_v['KOMODITAS'].unique()[:3])
    if pilih:
        df_p = df_v[df_v['KOMODITAS'].isin(pilih)]
        df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
        st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group"), use_container_width=True)

# D. HALAMAN BERITA
elif st.session_state.halaman_aktif == "Berita":
    st.markdown("### 📰 Media & Berita")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    for _, row in df_berita.iloc[::-1].iterrows():
        st.markdown(f'<div class="card-container"><h4>{row["Kegiatan"]}</h4><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)

# E. HALAMAN ADMIN
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Editor Beranda")
    global_settings["hero_title"] = st.text_input("Judul Hero:", global_settings["hero_title"])
    global_settings["hero_subtitle"] = st.text_area("Sub-judul:", global_settings["hero_subtitle"])
    if st.button("💾 Simpan Perubahan"): pindah_halaman("Beranda")
