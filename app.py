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
    initial_sidebar_state="collapsed"
)

# --- 2. LOGIKA PRIVASI ADMIN (URL: ?admin=rahasia) ---
query_params = st.query_params
is_admin = query_params.get("admin") == "rahasia"

# Menggunakan session_state agar perubahan teks tersimpan sementara selama sesi aktif
if "hero_title" not in st.session_state:
    st.session_state.hero_title = "Smart Economy Ngada 👋"
if "hero_subtitle" not in st.session_state:
    st.session_state.hero_subtitle = "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada."
if "about_text" not in st.session_state:
    st.session_state.about_text = "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat melalui pemantauan rutin di pasar-pasar lokal Kabupaten Ngada."

# Navigasi Menu
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "🏠 Dashboard"

def set_menu(nama_menu):
    st.session_state.menu_aktif = nama_menu

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }
    .stApp { background-color: #F8FAFC !important; }
    
    /* Pimpinan Header */
    .pimpinan-container {
        display: flex; align-items: center; background: white; 
        padding: 20px; border-radius: 20px; margin-bottom: 20px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .pimpinan-img { width: 110px; height: 110px; object-fit: cover; border-radius: 15px; border: 3px solid #059669; }
    .pimpinan-text { margin-left: 20px; }

    /* Hero */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 45px; border-radius: 25px; margin-bottom: 30px; text-align: center;
    }
    .hero-section h1 { color: #FFFFFF !important; font-size: 2.6rem !important; font-weight: 800; margin-bottom: 10px; }
    .hero-section p { color: #ECFDF5 !important; font-size: 1.1rem; opacity: 0.9; }

    /* Menu Cards */
    .menu-card {
        background: white; padding: 25px; border-radius: 20px; text-align: center;
        border: 1px solid #E2E8F0; transition: all 0.3s ease; height: 170px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .menu-card:hover { transform: translateY(-5px); border-color: #059669; box-shadow: 0 10px 20px rgba(0,0,0,0.08); }
    .menu-icon { font-size: 2.8rem; margin-bottom: 10px; }
    .menu-title { font-weight: 800; font-size: 0.9rem; color: #059669 !important; letter-spacing: 0.5px; }

    /* Admin Bar */
    .admin-bar {
        background: #DC2626; color: white; padding: 12px; 
        text-align: center; font-weight: bold; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI GAMBAR ---
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 5. DATA LOADING ---
@st.cache_data(ttl=60)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url, skiprows=1)
        df = df.iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        return df.dropna(subset=['KOMODITAS'])
    except: return pd.DataFrame()

df_harga = load_data()

# --- 6. RENDER HALAMAN ---

# Tampilkan Bar Admin Jika Aktif
if is_admin:
    st.markdown('<div class="admin-bar">🔓 MODE EDITOR AKTIF (URL RAHASIA)</div>', unsafe_allow_html=True)

if not df_harga.empty:
    
    # --- BERANDA (DASHBOARD) ---
    if st.session_state.menu_aktif == "🏠 Dashboard":
        # Header Foto Bupati
        img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
        img_l = get_img_as_base64("logo_ngada.png")
        st.markdown(f"""
            <div class="pimpinan-container">
                <img src="data:image/jpeg;base64,{img_p}" class="pimpinan-img">
                <div class="pimpinan-text">
                    <img src="data:image/png;base64,{img_l}" width="35">
                    <h3 style="margin:0; color:#059669;">Pemerintah Kabupaten Ngada</h3>
                    <p style="margin:0; font-size:0.9rem; opacity:0.7;">Bagian Perekonomian & SDA - Setda Ngada</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Hero Section
        st.markdown(f'''
            <div class="hero-section">
                <h1>{st.session_state.hero_title}</h1>
                <p>{st.session_state.hero_subtitle}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Grid 5 Kolom Menu Utama
        c1, c2, c3, c4, c5 = st.columns(5)
        menu_items = [
            {"icon": "🛒", "title": "HARGA PASAR", "target": "🛒 Harga Pasar"},
            {"icon": "📈", "title": "TREN HARGA", "target": "📈 Tren Harga"},
            {"icon": "📰", "title": "MEDIA BERITA", "target": "📰 Media & Berita"},
            {"icon": "📥", "title": "PUSAT DATA", "target": "📥 Pusat Unduhan"},
            {"icon": "🏛️", "title": "KOMITMEN", "target": "ℹ️ Komitmen ASN"}
        ]
        cols = [c1, c2, c3, c4, c5]
        for i, m in enumerate(menu_items):
            with cols[i]:
                st.markdown(f'''
                    <div class="menu-card">
                        <div class="menu-icon">{m["icon"]}</div>
                        <div class="menu-title">{m["title"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                if st.button(f"Klik {m['title']}", key=f"btn_{i}", use_container_width=True):
                    set_menu(m["target"])
                    st.rerun()

        # Tombol Edit Hero (Hanya Muncul untuk Admin)
        if is_admin:
            st.divider()
            with st.expander("🛠️ EDIT HERO (KHUSUS ADMIN)"):
                st.session_state.hero_title = st.text_input("Ganti Judul Hero:", st.session_state.hero_title)
                st.session_state.hero_subtitle = st.text_area("Ganti Sub-judul Hero:", st.session_state.hero_subtitle)
                st.info("Perubahan akan terlihat di halaman depan.")

    # --- HALAMAN DETAIL ---
    else:
        col_back, col_title = st.columns([1, 5])
        with col_back:
            if st.button("⬅️ Beranda"):
                set_menu("🏠 Dashboard")
                st.rerun()
        with col_title:
            st.markdown(f"### {st.session_state.menu_aktif}")
        
        st.divider()

        # 1. Harga Pasar
        if st.session_state.menu_aktif == "🛒 Harga Pasar":
            st.dataframe(df_harga, use_container_width=True)

        # 2. Tren Harga (Ada Fitur Edit Admin)
        elif st.session_state.menu_aktif == "📈 Tren Harga":
            if is_admin:
                st.warning("Mode Admin: Anda dapat memfilter tampilan default di bawah ini.")
            
            df_v = df_harga.dropna(subset=['SATUAN'])
            pilihan = st.multiselect("Pilih Komoditas untuk Grafik:", options=df_v['KOMODITAS'].unique())
            if pilihan:
                df_p = df_v[df_v['KOMODITAS'].isin(pilihan)]
                fig = px.bar(df_p, x="KOMODITAS", y="KECIL_INI", title="Perbandingan Harga Pasar", color_discrete_sequence=['#10B981'])
                st.plotly_chart(fig, use_container_width=True)

        # 3. Komitmen ASN (Ada Fitur Edit Admin)
        elif st.session_state.menu_aktif == "ℹ️ Komitmen ASN":
            st.markdown(f'''
                <div style="background:white; padding:30px; border-radius:15px; border-left:8px solid #059669; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    <p style="font-size:1.1rem; line-height:1.8;">{st.session_state.about_text}</p>
                </div>
            ''', unsafe_allow_html=True)
            
            if is_admin:
                st.divider()
                with st.expander("📝 EDIT TEKS KOMITMEN (KHUSUS ADMIN)"):
                    st.session_state.about_text = st.text_area("Update Visi/Misi:", value=st.session_state.about_text, height=200)
                    if st.button("Simpan Teks"):
                        st.success("Teks berhasil diperbarui!")

else:
    st.error("Koneksi ke database bermasalah. Pastikan link Google Sheets benar.")
