import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (Satu Tempat untuk Semua Data) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menyediakan data akurat untuk stabilitas ekonomi daerah.",
        "potensi_text": "Kabupaten Ngada memiliki potensi besar di sektor Kopi, Pariwisata, dan Pertanian.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (Header Tetap & Tombol Navigasi) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC !important; }
    
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 20px; border-radius: 15px; text-align: center; color: white !important; 
        margin-bottom: 10px; 
    }
    
    .nav-btn-container {
        display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;
    }
    
    .price-card {
        background: white; border-radius: 10px; padding: 15px;
        border-left: 5px solid #059669; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER (SOLUSI VALUEERROR) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        # Mencegah ValueError: Ubah teks harga jadi angka, jika gagal jadi 0
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
            
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 5. HEADER & NAVIGASI UTAMA (Pengganti Sidebar agar tidak hilang) ---
with st.container():
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=80)
    with col_r:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2><p style='color:green;'>Portal Ekonomi & SDA Setda Ngada</p>", unsafe_allow_html=True)
    
    # Menu Navigasi Horizontal
    n1, n2, n3, n4 = st.columns(4)
    if n1.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if n2.button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if n3.button("📈 Tren", use_container_width=True): navigasi("Tren")
    if n4.button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
    
    if is_admin:
        if st.button("🛠️ PANEL ADMIN", type="primary", use_container_width=True): navigasi("Admin")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 📢 Informasi Terbaru")
        st.write(store["about_text"])
    with c2:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"):
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", use_container_width=True)

# B. HARGA (Besar vs Kecil)
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Pantauan Harga Komoditas")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0: 
            st.subheader(f"📂 {r['KOMODITAS']}")
            continue
            
        with st.container():
            st.markdown(f"""
            <div class="price-card">
                <table style="width:100%">
                    <tr>
                        <td style="width:40%"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></td>
                        <td><b>Pedagang Besar</b><br>Rp {r['B_INI']:,}</td>
                        <td><b>Pedagang Kecil</b><br>Rp {r['K_INI']:,}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

# C. TREN (Warna Berdasarkan Status)
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Tren Pergerakan Harga")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        def hitung_status(row):
            if row['K_INI'] > row['K_KMRN']: return 'Naik'
            if row['K_INI'] < row['K_KMRN']: return 'Turun'
            return 'Stabil'
        
        df_p['Status'] = df_p.apply(hitung_status, axis=1)
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status", 
                     color_discrete_map={'Naik': 'red', 'Turun': 'green', 'Stabil': 'orange'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada data tren yang dipilih oleh Admin.")

# D. POTENSI
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Daerah")
    st.success(store["potensi_text"])

# E. ADMIN (Full Control)
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Kontrol Panel Admin")
    
    with st.expander("📝 Edit Teks Beranda & Potensi", expanded=True):
        store["hero_title"] = st.text_input("Judul Hero:", store["hero_title"])
        store["hero_subtitle"] = st.text_input("Sub-judul Hero:", store["hero_subtitle"])
        store["about_text"] = st.text_area("Informasi Beranda:", store["about_text"])
        store["potensi_text"] = st.text_area("Teks Potensi Daerah:", store["potensi_text"])
    
    with st.expander("📊 Pilih Komoditas untuk Tren"):
        store["tren_publikasi"] = st.multiselect("Pilih:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
        
    if st.button("SIMPAN SEMUA PERUBAHAN", type="primary"):
        st.success("Data berhasil diperbarui!")
