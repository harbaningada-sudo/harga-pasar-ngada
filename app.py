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

# --- 3. CSS KUSTOM (WAJIB ADA AGAR TIDAK MUNCUL TEKS KODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Background Full Hijau */
    .stApp { background-color: #F0FDF4 !important; }
    
    /* Perbaikan Tampilan Kartu Harga */
    .price-card {
        background: white !important; 
        padding: 20px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 12px;
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .price-group { text-align: center; flex: 1; }
    .price-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 5px; }
    .price-value { font-size: 1.2rem; font-weight: 800; color: #1E293B; }
    
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #15803D 100%);
        padding: 40px; border-radius: 20px; text-align: center; color: white !important;
    }
    .menu-card-box {
        background: white; border: 1px solid #DCFCE7; padding: 20px; border-radius: 20px; text-align: center;
    }
    .group-header {
        background: #059669 !important; color: white !important; padding: 8px 15px; border-radius: 8px; margin: 20px 0 10px 0;
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
        return df_h.dropna(subset=['KOMODITAS']), pd.DataFrame()
    except: return pd.DataFrame(), pd.DataFrame()

df_harga, _ = load_all_data()

# --- 6. SIDEBAR ---
with st.sidebar:
    # Logo Kabupaten
    logo_ngada = get_img_as_base64("logo-ngada.png")
    if logo_ngada: st.markdown(f'<center><img src="data:image/png;base64,{logo_ngada}" width="80"></center>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>KABUPATEN NGADA</h3>", unsafe_allow_html=True)

    # Foto Pimpinan
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    if img_p: st.image(f"data:image/jpeg;base64,{img_p}", use_container_width=True)
    
    st.info("Bagian Perekonomian & SDA Setda Ngada")
    if is_admin:
        if st.button("🛠️ Admin"): pindah_halaman("Admin")
    if st.button("🏠 Beranda"): pindah_halaman("Beranda")

# --- 7. TAMPILAN HALAMAN ---

if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="menu-card-box"><h2>🛍️</h2><h4>Harga Komoditas</h4></div>', unsafe_allow_html=True)
        if st.button("Buka Harga", key="nav1", use_container_width=True): pindah_halaman("Harga")
    # ... (tambah kolom lain jika perlu)

elif st.session_state.halaman_aktif == "Harga":
    st.markdown("## 🛍️ Pantauan Harga Pasar")
    if st.button("⬅️ Kembali"): pindah_halaman("Beranda")
    
    search = st.text_input("🔍 Cari komoditas...")
    df_show = df_harga.copy()
    if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

    for _, row in df_show.iterrows():
        # Jika baris adalah Kategori (Satuan kosong)
        if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
            st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            continue
        
        # Logika angka
        try:
            b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
            k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
            k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
            selisih = k_ini - k_kmrn
            warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#64748B"
            ikon = "▲" if selisih > 0 else "▼" if selisih < 0 else "—"

            # INI KUNCINYA: Menggunakan st.markdown dengan unsafe_allow_html=True
            st.markdown(f"""
            <div class="price-card" style="border-left: 8px solid {warna};">
                <div style="flex: 1.5;">
                    <b style="font-size: 1.1rem;">{row['KOMODITAS']}</b><br>
                    <small>Satuan: {row['SATUAN']}</small>
                </div>
                <div class="price-group">
                    <div class="price-label">Pedagang Besar</div>
                    <div class="price-value">Rp {b_ini:,}</div>
                </div>
                <div class="price-group" style="border-left: 1px solid #EEE;">
                    <div class="price-label">Pedagang Kecil</div>
                    <div class="price-value" style="color: {warna};">Rp {k_ini:,}</div>
                    <small style="color: {warna}; font-weight: bold;">{ikon} {abs(selisih):,}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            continue
