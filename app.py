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

# --- 2. CEK STATUS ADMIN ---
# URL Umum: ...streamlit.app
# URL Admin: ...streamlit.app/?admin=rahasia
query_params = st.query_params
is_admin = query_params.get("admin") == "rahasia"

# --- 3. DATA DEFAULT (Yang akan tampil di URL Umum) ---
# Tip: Jika ingin permanen selamanya, teks ini yang harus kamu edit di kode
DEFAULT_HERO_TITLE = "Smart Economy Ngada 👋"
DEFAULT_HERO_SUBTITLE = "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada."
DEFAULT_ABOUT = "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat melalui pemantauan rutin di pasar-pasar lokal Kabupaten Ngada."

if "hero_title" not in st.session_state:
    st.session_state.hero_title = DEFAULT_HERO_TITLE
if "hero_subtitle" not in st.session_state:
    st.session_state.hero_subtitle = DEFAULT_HERO_SUBTITLE
if "about_text" not in st.session_state:
    st.session_state.about_text = DEFAULT_ABOUT

# Logika Navigasi
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "🏠 Dashboard"

def set_menu(nama_menu):
    st.session_state.menu_aktif = nama_menu

# --- 4. CSS KUSTOM (DISAMAKAN UNTUK SEMUA URL) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Dasar Layout */
    .stApp {{ background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }}
    
    /* Header Pimpinan */
    .pimpinan-container {{
        display: flex; align-items: center; background: white; 
        padding: 20px; border-radius: 20px; margin-bottom: 25px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .pimpinan-img {{ width: 110px; height: 110px; object-fit: cover; border-radius: 15px; border: 3px solid #059669; }}
    .pimpinan-text {{ margin-left: 20px; }}

    /* Hero Section */
    .hero-section {{
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 50px 20px; border-radius: 25px; margin-bottom: 35px; text-align: center;
        color: white !important;
    }}
    .hero-section h1 {{ font-size: 2.8rem !important; font-weight: 800; margin-bottom: 10px; color: white !important; }}
    .hero-section p {{ font-size: 1.2rem; opacity: 0.95; color: #ECFDF5 !important; }}

    /* Grid Menu Cards */
    .menu-card {{
        background: white; padding: 25px; border-radius: 22px; text-align: center;
        border: 1px solid #E2E8F0; transition: all 0.3s ease; height: 180px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}
    .menu-card:hover {{ transform: translateY(-8px); border-color: #059669; box-shadow: 0 12px 24px rgba(5, 150, 105, 0.15); }}
    .menu-icon {{ font-size: 3rem; margin-bottom: 12px; }}
    .menu-title {{ font-weight: 800; font-size: 0.95rem; color: #059669 !important; text-transform: uppercase; }}

    /* Badge Admin */
    .admin-indicator {{
        background: #EF4444; color: white; padding: 8px 20px; border-radius: 10px;
        text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 0.8rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. FUNGSI HELPER GAMBAR ---
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 6. LOAD DATA HARGA ---
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

# --- 7. RENDER ---

# Munculkan indikator hanya jika di URL Admin
if is_admin:
    st.markdown('<div class="admin-indicator">🔓 MODE EDITOR AKTIF - Perubahan bersifat sementara (Sesi ini)</div>', unsafe_allow_html=True)

if not df_harga.empty:
    
    # HALAMAN BERANDA (Tampilan Umum & Admin Sama)
    if st.session_state.menu_aktif == "🏠 Dashboard":
        
        # Header Foto Bupati & Wakil (Wajib ada di semua URL)
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

        # Hero Section (Teks diambil dari session agar bisa di-edit admin)
        st.markdown(f'''
            <div class="hero-section">
                <h1>{st.session_state.hero_title}</h1>
                <p>{st.session_state.hero_subtitle}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Grid 5 Kolom Menu
        cols = st.columns(5)
        menu_items = [
            {"icon": "🛒", "title": "HARGA PASAR", "target": "🛒 Harga Pasar"},
            {"icon": "📈", "title": "TREN HARGA", "target": "📈 Tren Harga"},
            {"icon": "📰", "title": "MEDIA BERITA", "target": "📰 Media & Berita"},
            {"icon": "📥", "title": "PUSAT DATA", "target": "📥 Pusat Unduhan"},
            {"icon": "🏛️", "title": "KOMITMEN", "target": "ℹ️ Komitmen ASN"}
        ]
        
        for i, m in enumerate(menu_items):
            with cols[i]:
                st.markdown(f'''
                    <div class="menu-card">
                        <div class="menu-icon">{m["icon"]}</div>
                        <div class="menu-title">{m["title"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                if st.button(f"Lihat {m['title']}", key=f"btn_{i}", use_container_width=True):
                    set_menu(m["target"])
                    st.rerun()

        # Fitur Edit Hero (HANYA MUNCUL DI URL ADMIN)
        if is_admin:
            st.write("---")
            with st.expander("🛠️ PANEL EDITOR HERO"):
                st.session_state.hero_title = st.text_input("Judul Utama:", st.session_state.hero_title)
                st.session_state.hero_subtitle = st.text_area("Sub-judul:", st.session_state.hero_subtitle)
                st.info("💡 Tips: Perubahan di sini hanya berlaku sementara. Untuk permanen, ubah nilai DEFAULT di kode Python.")

    # HALAMAN DETAIL
    else:
        if st.button("⬅️ Kembali ke Menu Utama"):
            set_menu("🏠 Dashboard")
            st.rerun()
        
        st.divider()
        st.subheader(f"Halaman {st.session_state.menu_aktif}")

        if st.session_state.menu_aktif == "🛒 Harga Pasar":
            st.dataframe(df_harga, use_container_width=True)

        elif st.session_state.menu_aktif == "ℹ️ Komitmen ASN":
            st.info(st.session_state.about_text)
            if is_admin:
                with st.expander("📝 Edit Teks Komitmen"):
                    st.session_state.about_text = st.text_area("Teks Baru:", st.session_state.about_text, height=150)
                    if st.button("Update"): st.rerun()

else:
    st.error("Gagal menarik data dari Google Sheets.")
