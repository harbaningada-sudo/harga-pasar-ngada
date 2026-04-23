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
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_content": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas ekonomi daerah.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (OPTIMASI ZERO SCROLL) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC !important; }
    
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 15px; border-radius: 12px; text-align: center; color: white !important; 
        margin-bottom: 10px; 
    }
    
    .menu-card { 
        background: white; border: 1px solid #E2E8F0; padding: 10px; 
        border-radius: 10px; text-align: center; height: 90px;
    }

    .grid-harga {
        display: grid; grid-template-columns: 2fr 1.2fr 1.2fr;
        gap: 10px; align-items: center; border-bottom: 1px solid #F1F5F9;
        padding: 6px 0; font-size: 13px;
    }
    .header-harga { font-weight: bold; color: #64748B; font-size: 11px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER (DENGAN FIX ERROR NUMERIC) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        # Mencegah Error ValueError pada data kosong
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 5. HEADER TETAP (LOGO & FOTO PIMPINAN) ---
with st.container():
    c_logo, c_bupati, c_nav = st.columns([0.5, 1.2, 3])
    with c_logo:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=70)
    with c_bupati:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"): 
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", width=200) #
    with c_nav:
        st.markdown("<h3 style='margin:0;'>KABUPATEN NGADA</h3><p style='margin:0; font-size:12px; color:green;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
        n1, n2, n3 = st.columns(3)
        with n1: 
            if st.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
        with n2: 
            if st.button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
        with n3:
            if is_admin:
                if st.button("🛠️ Admin", use_container_width=True): navigasi("Admin")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h2 style="margin:0;">{store["hero_title"]}</h2><p style="margin:0; font-size:14px;">{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    menu = [("🛍️", "Harga", "Harga"), ("📈", "Tren", "Tren"), ("ℹ️", "Tentang", "Tentang")] #
    for i, (icon, label, target) in enumerate(menu):
        with cols[i]:
            st.markdown(f'<div class="menu-card"><h3>{icon}</h3><h4>{label}</h4></div>', unsafe_allow_html=True)
            if st.button(f"Buka {label}", key=f"m_{target}", use_container_width=True): navigasi(target)

# B. HARGA (PEDAGANG BESAR & KECIL)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Pantauan Harga Harian")
    st.markdown("""<div class="grid-harga" style="background:#F1F5F9; padding:8px; border-radius:5px;">
        <div class="header-harga">Komoditas / Satuan</div>
        <div class="header-harga">Besar (Rp)</div>
        <div class="header-harga">Kecil (Rp)</div>
    </div>""", unsafe_allow_html=True)

    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"<div style='background:#E2E8F0; padding:5px; margin-top:5px; font-weight:bold; font-size:12px;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
        
        st.markdown(f"""
            <div class="grid-harga">
                <div><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                <div><b>{r['B_INI']:,}</b><br><span style='color:gray; font-size:10px;'>Kmrn: {r['B_KMRN']:,}</span></div>
                <div><b>{r['K_INI']:,}</b><br><span style='color:gray; font-size:10px;'>Kmrn: {r['K_KMRN']:,}</span></div>
            </div>""", unsafe_allow_html=True) #

# C. TREN (LOGIKA WARNA OTOMATIS)
elif st.session_state.halaman_aktif == "Tren":
    st.subheader("📈 Tren Fluktuasi")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        # Logika Warna
        def set_color(row):
            if row['K_INI'] > row['K_KMRN']: return 'Naik (Merah)'
            elif row['K_INI'] < row['K_KMRN']: return 'Turun (Hijau)'
            return 'Stabil (Kuning)'
        
        df_p['Status'] = df_p.apply(set_color, axis=1)
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status",
                     color_discrete_map={'Naik (Merah)': '#EF4444', 'Turun (Hijau)': '#10B981', 'Stabil (Kuning)': '#FBBF24'})
        st.plotly_chart(fig, use_container_width=True) #
    else: st.info("Pilih komoditas di Admin.")

# D. POTENSI & TENTANG
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Ekonomi")
    st.write("Kopi Jawawa, Bambu, dan Pariwisata adalah pilar utama ekonomi Ngada.")

elif st.session_state.halaman_aktif == "Tentang":
    st.header("ℹ️ Tentang Kami")
    st.write(store["about_content"])

# E. ADMIN (EDIT SEMUA KONTEN)
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin Konten")
    t1, t2, t3 = st.tabs(["Update Tren", "Edit Beranda", "Edit Tentang"])
    
    with t1:
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas Grafik:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    with t2:
        store["hero_title"] = st.text_input("Judul Utama:", store["hero_title"])
        store["hero_subtitle"] = st.text_area("Sub-Judul:", store["hero_subtitle"])
    with t3:
        store["about_content"] = st.text_area("Konten Tentang Kami:", store["about_content"], height=200)
    
    if st.button("Simpan Semua Perubahan"):
        st.success("Konten berhasil diperbarui!")
