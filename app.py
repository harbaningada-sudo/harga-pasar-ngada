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

# --- 3. CSS KUSTOM (WARNA HIJAU & DETAIL HARGA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Background Web Jadi Hijau Muda */
    .stApp { background-color: #F0FDF4 !important; }
    
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 2px solid #DCFCE7; }
    
    .sidebar-logo { width: 80px; display: block; margin: 0 auto 10px; }
    .sidebar-pimpinan { width: 100%; border-radius: 15px; border: 2px solid #059669; margin-bottom: 15px; }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #15803D 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px; text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }

    /* Menu Card di Tengah */
    .menu-card-box {
        background: white; border: 1px solid #DCFCE7;
        padding: 20px; border-radius: 20px; text-align: center;
        transition: 0.3s; min-height: 180px; display: flex; flex-direction: column; justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .menu-card-box:hover { border-color: #059669; transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

    /* Data Card Detail Harga */
    .price-card {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .price-group { text-align: center; flex: 1; border-left: 1px solid #F1F5F9; }
    .price-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px; }
    .price-value { font-size: 1.25rem; font-weight: 800; }
    .group-header {
        background: #059669 !important; color: white !important; padding: 10px 20px; 
        border-radius: 10px; margin: 25px 0 15px 0; font-weight: 700;
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

# --- 6. SIDEBAR (Logo + Foto Pimpinan) ---
with st.sidebar:
    # Tampilkan Logo Ngada (Pastikan file logo-ngada.png ada di folder yang sama)
    logo_ngada = get_img_as_base64("logo-ngada.png") # Ganti nama file sesuai file kamu
    if logo_ngada:
        st.markdown(f'<img src="data:image/png;base64,{logo_ngada}" class="sidebar-logo">', unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;'>🏛️</h2>", unsafe_allow_html=True)
        
    st.markdown("<h4 style='text-align:center; margin-bottom:20px;'>KABUPATEN NGADA</h4>", unsafe_allow_html=True)

    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if img_p:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_p}" class="sidebar-pimpinan">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#F0FDF4; border-radius:10px; border: 1px solid #DCFCE7;">
            <small><b>Bagian Perekonomian & SDA</b><br>Setda Kabupaten Ngada</small>
        </div>
    """, unsafe_allow_html=True)
    
    if is_admin:
        st.divider()
        st.success("🔓 MODE EDITOR")
        if st.button("🛠️ Panel Admin", use_container_width=True): pindah_halaman("Admin")
        if st.button("🏠 Menu Beranda", use_container_width=True): pindah_halaman("Beranda")

# --- 7. LOGIKA HALAMAN ---

# A. BERANDA
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
        st.markdown('<div class="menu-card-box"><h2>🛍️</h2><h4>Harga Komoditas</h4><p>Pedagang Besar & Kecil</p></div>', unsafe_allow_html=True)
        if st.button("Buka Harga", key="nav1", use_container_width=True): pindah_halaman("Harga")
    with row1_c2:
        st.markdown('<div class="menu-card-box"><h2>📈</h2><h4>Tren Ekonomi</h4><p>Grafik fluktuasi</p></div>', unsafe_allow_html=True)
        if st.button("Buka Tren", key="nav2", use_container_width=True): pindah_halaman("Tren")
    with row1_c3:
        st.markdown('<div class="menu-card-box"><h2>📰</h2><h4>Media & Berita</h4><p>Info terkini</p></div>', unsafe_allow_html=True)
        if st.button("Buka Berita", key="nav3", use_container_width=True): pindah_halaman("Berita")

    row2_c1, row2_c2, row2_c3 = st.columns(3)
    with row2_c1:
        st.markdown('<div class="menu-card-box"><h2>📥</h2><h4>Pusat Unduhan</h4><p>Data CSV</p></div>', unsafe_allow_html=True)
        if st.button("Buka Unduhan", key="nav4", use_container_width=True): pindah_halaman("Unduhan")
    with row2_c2:
        st.markdown('<div class="menu-card-box"><h2>ℹ️</h2><h4>Tentang Kita</h4><p>Profil Setda</p></div>', unsafe_allow_html=True)
        if st.button("Buka Info", key="nav5", use_container_width=True): pindah_halaman("Tentang")
    with row2_c3:
        st.markdown('<div class="menu-card-box"><h2>📞</h2><h4>Kontak</h4><p>Layanan Pengaduan</p></div>', unsafe_allow_html=True)
        st.button("Hubungi Kami", key="nav6", use_container_width=True, disabled=True)

# B. HARGA (DETAIL BESAR VS KECIL)
elif st.session_state.halaman_aktif == "Harga":
    st.markdown("<h2 style='text-align:center;'>🛍️ Rincian Harga Komoditas</h2>", unsafe_allow_html=True)
    if st.button("⬅️ Kembali ke Menu Utama"): pindah_halaman("Beranda")
    
    search = st.text_input("🔍 Cari barang (contoh: Beras, Telur)...")
    df_show = df_harga.copy()
    if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
    
    for _, row in df_show.iterrows():
        # Judul Grup/Kategori
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            continue
        
        # Konversi Angka
        b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
        b_kmrn = int(pd.to_numeric(row['BESAR_KMRN'], errors='coerce') or 0)
        k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
        k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
        
        # Logika Perubahan Harga (Pedagang Kecil sebagai acuan status)
        selisih = k_ini - k_kmrn
        warna_status = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#64748B"
        ikon = "🔺" if selisih > 0 else "🔻" if selisih < 0 else "➖"

        # Tampilan Kartu Rinci
        st.markdown(f"""
        <div class="price-card" style="border-left: 8px solid {warna_status};">
            <div style="flex: 1.5;">
                <b style="font-size: 1.2rem;">{row['KOMODITAS']}</b><br>
                <span style="color: #64748B;">Satuan: {row['SATUAN']}</span>
            </div>
            
            <div class="price-group">
                <div class="price-label">Pedagang Besar</div>
                <div class="price-value" style="color: #1E293B;">Rp {b_ini:,}</div>
                <small style="color: #94A3B8;">Kemarin: Rp {b_kmrn:,}</small>
            </div>
            
            <div class="price-group" style="border-left: 2px solid #F1F5F9;">
                <div class="price-label">Pedagang Kecil</div>
                <div class="price-value" style="color: {warna_status};">Rp {k_ini:,}</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: {warna_status};">
                    {ikon} {abs(selisih):,}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# (Bagian Halaman Lain seperti Tren, Berita, dll tetap sama dengan kode sebelumnya)
# ... [Sisa kode Tren, Berita, Admin tetap dipertahankan] ...
