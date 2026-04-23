import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_content": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (ZERO SCROLL & CLEAN TABLE) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC !important; }
    
    /* Membuat font lebih compact agar tidak banyak scroll */
    html, body, [class*="css"] { font-size: 14px; }
    
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 20px; border-radius: 15px; text-align: center; color: white !important; 
        margin-bottom: 15px; 
    }
    
    .menu-card { 
        background: white; border: 1px solid #E2E8F0; padding: 10px; 
        border-radius: 12px; text-align: center; transition: 0.3s;
        height: 100px;
    }
    .menu-card h4 { margin: 5px 0; font-size: 14px; }

    /* Style Tabel Harga Modern */
    .price-container {
        background: white; border-radius: 10px; padding: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px;
    }
    .grid-harga {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 10px;
        align-items: center;
        border-bottom: 1px solid #F1F5F9;
        padding: 8px 0;
    }
    .header-harga { font-weight: bold; color: #64748B; font-size: 12px; text-transform: uppercase; }
    .val-now { font-weight: bold; color: #0F172A; }
    .val-old { font-size: 11px; color: #94A3B8; text-decoration: line-through; }
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

# --- 5. HEADER COMPACT ---
with st.container():
    c_logo, c_bupati, c_nav = st.columns([0.6, 1.5, 3])
    with c_logo:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=80)
    with c_bupati:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"): st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", width=220)
    with c_nav:
        st.markdown("<h3 style='margin:0;'>KABUPATEN NGADA</h3><p style='margin:0; color:green;'>Bagian Perekonomian & SDA</p>", unsafe_allow_html=True)
        btn1, btn2, btn3 = st.columns(3)
        with btn1: 
            if st.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
        with btn2:
            if st.button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
        with btn3:
            if is_admin:
                if st.button("🛠️ Admin", use_container_width=True): navigasi("Admin")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA (Compact Mode)
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h2 style="margin:0;">{store["hero_title"]}</h2><p style="margin:0;">{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    # Menu Grid 2 Baris agar hemat tempat
    cols = st.columns(3)
    menu_items = [
        ("🛍️", "Harga Pasar", "Harga"),
        ("📈", "Tren Harga", "Tren"),
        ("📰", "Berita", "Berita"),
        ("📥", "Unduhan", "Unduhan"),
        ("ℹ️", "Tentang", "Tentang"),
        ("🏛️", "Potensi", "Potensi")
    ]
    
    for i, (icon, label, target) in enumerate(menu_items):
        with cols[i % 3]:
            st.markdown(f'<div class="menu-card"><h3>{icon}</h3><h4>{label}</h4></div>', unsafe_allow_html=True)
            if st.button(f"Buka {label}", key=f"btn_{target}", use_container_width=True): navigasi(target)

# B. HARGA (Tampilan Perbandingan Besar & Kecil)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas")
    st.markdown("""
        <div class="grid-harga" style="background:#F1F5F9; padding:10px; border-radius:5px;">
            <div class="header-harga">Nama Komoditas</div>
            <div class="header-harga">Pedagang Besar (Rp)</div>
            <div class="header-harga">Pedagang Kecil (Rp)</div>
        </div>
    """, unsafe_allow_html=True)

    for _, r in df_harga.iterrows():
        if pd.isna(r['SATUAN']):
            st.markdown(f"<div style='background:#E2E8F0; padding:5px 10px; margin-top:10px; font-weight:bold;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
        
        # Logika warna/indikator (Opsional: bisa tambah panah jika naik/turun)
        st.markdown(f"""
            <div class="grid-harga">
                <div><b>{r['KOMODITAS']}</b> <br><small>{r['SATUAN']}</small></div>
                <div>
                    <span class="val-now">{r['B_INI']}</span> <br>
                    <span class="val-old">Kmrn: {r['B_KMRN']}</span>
                </div>
                <div>
                    <span class="val-now">{r['K_INI']}</span> <br>
                    <span class="val-old">Kmrn: {r['K_KMRN']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("⬅️ Kembali ke Beranda"): navigasi("Beranda")

# C. POTENSI DAERAH (Sudah diisi)
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Ekonomi & SDA Ngada")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("☕ Pertanian & Perkebunan")
            st.write("Kopi Arabika Jawawa, Cengkeh, dan Bambu merupakan komoditas unggulan yang menembus pasar internasional.")
    with col2:
        with st.container(border=True):
            st.subheader("🌋 Pariwisata & Energi")
            st.write("Kampung Adat Bena, Taman Laut Riung 17 Pulau, dan potensi energi panas bumi (Geothermal) Mataloko.")
    if st.button("⬅️ Kembali"): navigasi("Beranda")

# Halaman lainnya tetap sama fungsinya...
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Fluktuasi")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])]
        fig = px.line(df_p, x="KOMODITAS", y=["K_INI"], title="Grafik Harga Terkini")
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Pilih data di panel admin.")
    if st.button("⬅️ Kembali"): navigasi("Beranda")

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Kontrol Admin")
    t1, t2 = st.tabs(["Update Tren", "Edit Teks Beranda"])
    with t1:
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas Tampil:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
        if st.button("Simpan Pengaturan Tren"): st.success("Data Tren Diperbarui!")
    if st.button("⬅️ Kembali ke Beranda"): navigasi("Beranda")
