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
    /* Menghilangkan Sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    .stApp { background-color: #F0FDF4 !important; }
    
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

# --- 4. DATA LOADER ---
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

# --- 5. HEADER FULLSCREEN (LOGO DISAMPING FOTO) ---
with st.container():
    # Membuat 3 kolom: 1 untuk Logo, 1 untuk Foto Bupati, 1 untuk Info/Navigasi
    col_img1, col_img2, col_text = st.columns([0.8, 2, 3])
    
    with col_img1:
        # Menampilkan Logo Kabupaten Ngada yang baru dikirim
        if os.path.exists("logo-ngada.png"):
            st.image("logo-ngada.png", width=110)
            
    with col_img2:
        # Menampilkan Foto Bupati & Wakil Bupati tepat disampingnya
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"):
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", use_container_width=True)
            
    with col_text:
        st.markdown("<h2 style='margin-bottom:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#059669; font-weight:bold; margin-top:0;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
        
        # Tombol Navigasi Cepat
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
        with nav_col2:
            if is_admin:
                if st.button("🛠️ Admin", use_container_width=True): navigasi("Admin")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Operasi Pasar")
    
    st.markdown("<h3 style='text-align:center; margin-top:30px;'>🎯 Menu Layanan Digital</h3>", unsafe_allow_html=True)
    
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
    with c6:
        st.markdown('<div class="menu-card"><h2>🏛️</h2><h4>Potensi Daerah</h4></div>', unsafe_allow_html=True)
        if st.button("Buka Potensi", key="m6", use_container_width=True): navigasi("Potensi")

# B. HARGA (Logika List Harga)
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Harga Harian Komoditas")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    for _, r in df_harga.iterrows():
        if pd.isna(r['SATUAN']): st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f'<div class="price-card"><b>{r["KOMODITAS"]} ({r["SATUAN"]})</b> <span>Besar: Rp {r["B_INI"]} | Kecil: Rp {r["K_INI"]}</span></div>', unsafe_allow_html=True)

# ... (Halaman Tren, Berita, Admin tetap sama)
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Fluktuasi")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])]
        fig = px.bar(df_p, x="KOMODITAS", y=["K_KMRN", "K_INI"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Pilih data di panel admin untuk melihat tren.")

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin Konten")
    if st.button("⬅️ Kembali"): navigasi("Beranda")
    t1, t2 = st.tabs(["Publikasi Tren", "Edit Teks"])
    with t1:
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    with t2:
        store["hero_title"] = st.text_input("Judul Hero", store["hero_title"])
        if st.button("Simpan"): st.success("Tersimpan!")
