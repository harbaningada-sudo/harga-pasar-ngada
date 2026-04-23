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
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas ekonomi daerah.",
        "potensi_text": "Kabupaten Ngada memiliki potensi unggulan di sektor Kopi Arabika, Pariwisata, dan Bambu.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (OPTIMASI TAMPILAN) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC !important; }
    
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 25px; border-radius: 15px; text-align: center; color: white !important; 
        margin-bottom: 15px; 
    }
    
    .price-card {
        background: white; border-radius: 10px; padding: 12px;
        border-left: 5px solid #059669; margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER (ANTI-ERROR & NUMERIK) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
            
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 5. HEADER & 6 NAVIGASI UTAMA (TIDAK AKAN HILANG) ---
with st.container():
    c1, c2, c3 = st.columns([0.8, 2, 1.2])
    with c1:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=90)
    with c2:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2><p style='color:green; margin:0;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
    with c3:
        if is_admin:
            if st.button("🛠️ PANEL ADMIN", type="primary", use_container_width=True): navigasi("Admin")

    # Baris Navigasi 6 Menu
    n1, n2, n3, n4, n5, n6 = st.columns(6)
    if n1.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if n2.button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if n3.button("📈 Tren", use_container_width=True): navigasi("Tren")
    if n4.button("ℹ️ Tentang", use_container_width=True): navigasi("Tentang")
    if n5.button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if n6.button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA (EDITABLE)
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.info("### Selamat Datang")
        st.write(store["about_text"])
    with col_b:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"):
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", use_container_width=True)

# B. HARGA KOMODITAS
elif st.session_state.halaman_aktif == "Harga":
    st.header("🛍️ Harga Komoditas Hari Ini")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"<div style='background:#E2E8F0; padding:8px; border-radius:5px; font-weight:bold; margin-top:10px;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
        st.markdown(f"""
        <div class="price-card">
            <table style="width:100%">
                <tr>
                    <td style="width:35%"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></td>
                    <td><small>Besar:</small><br><b>Rp {r['B_INI']:,}</b></td>
                    <td><small>Kecil:</small><br><b>Rp {r['K_INI']:,}</b></td>
                </tr>
            </table>
        </div>""", unsafe_allow_html=True)

# C. TREN HARGA (BESAR & KECIL - WARNA DINAMIS)
elif st.session_state.halaman_aktif == "Tren":
    st.header("📈 Analisis Tren Harga")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        # Logika Status
        def get_status(ini, kmrn):
            if ini > kmrn: return 'Naik'
            if ini < kmrn: return 'Turun'
            return 'Stabil'
        
        df_p['Status Besar'] = df_p.apply(lambda x: get_status(x['B_INI'], x['B_KMRN']), axis=1)
        df_p['Status Kecil'] = df_p.apply(lambda x: get_status(x['K_INI'], x['K_KMRN']), axis=1)
        
        tab_b, tab_k = st.tabs(["Pedagang Besar", "Pedagang Kecil"])
        with tab_b:
            fig_b = px.bar(df_p, x="KOMODITAS", y="B_INI", color="Status Besar", 
                           color_discrete_map={'Naik': '#EF4444', 'Turun': '#10B981', 'Stabil': '#FBBF24'},
                           title="Tren Harga Pedagang Besar")
            st.plotly_chart(fig_b, use_container_width=True)
        with tab_k:
            fig_k = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status Kecil",
                           color_discrete_map={'Naik': '#EF4444', 'Turun': '#10B981', 'Stabil': '#FBBF24'},
                           title="Tren Harga Pedagang Kecil")
            st.plotly_chart(fig_k, use_container_width=True)
    else: st.warning("Pilih komoditas di Panel Admin.")

# D. TENTANG KITA
elif st.session_state.halaman_aktif == "Tentang":
    st.header("ℹ️ Profil Instansi")
    st.write(store["about_text"])

# E. PUSAT UNDUHAN
elif st.session_state.halaman_aktif == "Unduhan":
    st.header("📥 Pusat Unduhan Data")
    st.download_button("Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_ngada.csv", "text/csv")

# F. POTENSI DAERAH
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Daerah Ngada")
    st.success(store["potensi_text"])

# G. ADMIN PANEL (EDIT SEMUA)
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Kendali Admin")
    with st.expander("📝 Edit Konten Beranda & Profil", expanded=True):
        store["hero_title"] = st.text_input("Judul Banner:", store["hero_title"])
        store["hero_subtitle"] = st.text_input("Sub-judul Banner:", store["hero_subtitle"])
        store["about_text"] = st.text_area("Teks Profil/Tentang:", store["about_text"])
        store["potensi_text"] = st.text_area("Teks Potensi Daerah:", store["potensi_text"])
    
    with st.expander("📊 Pengaturan Grafik Tren"):
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas Tampil:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    
    if st.button("SIMPAN PERUBAHAN", type="primary"):
        st.success("Konten Berhasil Diperbarui!")
