import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (ADMIN & KONTEN) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_content": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menyediakan data akurat untuk menjaga stabilitas ekonomi daerah.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (FULLSCREEN & CLEAN) ---
st.markdown("""
    <style>
    /* Menghilangkan Sidebar secara paksa */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    
    .stApp { background-color: #F0FDF4 !important; }
    
    /* Container Header */
    .header-container {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
        text-align: center; border: 1px solid #DCFCE7;
    }
    
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 40px; border-radius: 20px; text-align: center; color: white !important; 
        margin-bottom: 25px; 
    }
    
    .menu-card { 
        background: white; border: 1px solid #DCFCE7; padding: 20px; 
        border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .menu-card:hover { transform: translateY(-5px); border-color: #059669; }

    .price-card { 
        background: white; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; 
        margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. IMAGE HELPER ---
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# --- 5. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h.dropna(subset=['KOMODITAS']), df_b.dropna(subset=['Kegiatan'])
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 6. HEADER UTAMA (PENGGANTI SIDEBAR) ---
with st.container():
    col_logo, col_info, col_bupati = st.columns([1, 3, 2])
    
    with col_logo:
        logo_data = get_img_as_base64("logo-ngada.png")
        if logo_data:
            st.markdown(f'<img src="data:image/png;base64,{logo_data}" style="width:100px; display:block; margin:auto;">', unsafe_allow_html=True)
    
    with col_info:
        st.markdown("<h1 style='text-align:center; margin-bottom:0;'>KABUPATEN NGADA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#059669; font-weight:bold;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
        # Tombol Home Navigasi Horizontal
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Beranda Utama", use_container_width=True): navigasi("Beranda")
        with c2:
            if is_admin:
                if st.button("🛠️ Admin Panel", use_container_width=True): navigasi("Admin")
    
    with col_bupati:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"):
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", use_container_width=True)

st.divider()

# --- 7. LOGIKA HALAMAN ---

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    # Hero Section
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    # Foto Operasi Pasar Utama
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Kegiatan Operasi Pasar Kabupaten Ngada")
    
    st.markdown("<h3 style='text-align:center; margin-top:30px;'>🎯 Menu Layanan Digital</h3>", unsafe_allow_html=True)
    
    # Grid Menu Utama (6 Menu)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="menu-card"><h2>🛍️</h2><h4>Harga Komoditas</h4></div>', unsafe_allow_html=True)
        if st.button("Lihat Harga", key="m1", use_container_width=True): navigasi("Harga")
    with c2:
        st.markdown('<div class="menu-card"><h2>📈</h2><h4>Tren Ekonomi</h4></div>', unsafe_allow_html=True)
        if st.button("Lihat Tren", key="m2", use_container_width=True): navigasi("Tren")
    with c3:
        st.markdown('<div class="menu-card"><h2>📰</h2><h4>Media & Berita</h4></div>', unsafe_allow_html=True)
        if st.button("Lihat Berita", key="m3", use_container_width=True): navigasi("Berita")

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="menu-card"><h2>📥</h2><h4>Pusat Unduhan</h4></div>', unsafe_allow_html=True)
        if st.button("Buka Unduhan", key="m4", use_container_width=True): navigasi("Unduhan")
    with c5:
        st.markdown('<div class="menu-card"><h2>ℹ️</h2><h4>Tentang Kita</h4></div>', unsafe_allow_html=True)
        if st.button("Buka Profil", key="m5", use_container_width=True): navigasi("Tentang")
    with col6 if 'col6' in locals() else c6: # Fix reference
        st.markdown('<div class="menu-card"><h2>🏛️</h2><h4>Potensi Daerah</h4></div>', unsafe_allow_html=True)
        if st.button("Buka Potensi", key="m6", use_container_width=True): navigasi("Potensi")

# B. HARGA
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Harga Harian Komoditas")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    for _, r in df_harga.iterrows():
        if pd.isna(r['SATUAN']): st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f'<div class="price-card"><b>{r["KOMODITAS"]} ({r["SATUAN"]})</b> <span>Besar: Rp {r["B_INI"]} | Kecil: Rp {r["K_INI"]}</span></div>', unsafe_allow_html=True)

# Logika elif lainnya (Tren, Berita, dll) tetap sama seperti sebelumnya
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Fluktuasi Harga")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])]
        fig = px.bar(df_p, x="KOMODITAS", y=["K_KMRN", "K_INI"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Belum ada data tren yang dipublikasikan.")

elif st.session_state.halaman_aktif == "Berita":
    st.header("📰 Media & Berita Terkini")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    for _, r in df_berita.iterrows():
        with st.container(border=True):
            st.subheader(r['Kegiatan'])
            st.caption(f"📅 {r['Tanggal']}")
            if str(r['Link']).startswith("http"): st.link_button("Lihat Selengkapnya", r['Link'])

elif st.session_state.halaman_aktif == "Unduhan":
    st.header("📥 Pusat Unduhan")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    st.download_button("Unduh CSV Harga", df_harga.to_csv().encode('utf-8'), "Harga_Ngada.csv")

elif st.session_state.halaman_aktif == "Tentang":
    st.header("ℹ️ Tentang Kita")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    st.write(store["about_content"])

elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Ekonomi")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    st.write("Informasi potensi SDA Ngada.")

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    t1, t2, t3 = st.tabs(["Tren", "Beranda", "Tentang"])
    with t1:
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas Grafik:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    with t2:
        store["hero_title"] = st.text_input("Judul:", store["hero_title"])
        store["hero_subtitle"] = st.text_area("Sub-judul:", store["hero_subtitle"])
    with t3:
        store["about_content"] = st.text_area("Konten Tentang:", store["about_content"])
    if st.button("Simpan Perubahan"): st.success("Data diperbarui!")
