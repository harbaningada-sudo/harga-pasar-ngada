import streamlit as st
import pandas as pd
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Digital Ngada", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LOGIKA PRIVASI ADMIN ---
# Cek apakah ada parameter ?admin=rahasia di URL
# Kamu bisa ganti kata "rahasia" dengan kata kunci lain agar lebih aman
query_params = st.query_params
is_admin = query_params.get("admin") == "rahasia"

@st.cache_resource
def get_global_settings():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat."
    }

global_settings = get_global_settings()

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
    
    .pimpinan-container {
        display: flex; align-items: center; background: white; 
        padding: 20px; border-radius: 20px; margin-bottom: 25px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .pimpinan-img { width: 120px; height: 120px; object-fit: cover; border-radius: 15px; border: 3px solid #059669; }
    .pimpinan-text { margin-left: 20px; }

    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 25px; margin-bottom: 30px; text-align: center;
    }
    .hero-section h1 { color: #FFFFFF !important; font-size: 2.2rem !important; font-weight: 800; }
    .hero-section p { color: #ECFDF5 !important; }

    .menu-card {
        background: white; padding: 20px; border-radius: 18px; text-align: center;
        border: 1px solid #E2E8F0; transition: all 0.3s ease;
        height: 160px; display: flex; flex-direction: column; justify-content: center;
    }
    .menu-card:hover { transform: translateY(-5px); border-color: #059669; box-shadow: 0 10px 15px rgba(0,0,0,0.1); }
    .menu-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .menu-title { font-weight: 800; font-size: 0.85rem; color: #059669 !important; }

    .admin-badge {
        background-color: #EF4444; color: white; padding: 5px 15px; 
        border-radius: 50px; font-weight: bold; font-size: 0.8rem;
        margin-bottom: 10px; display: inline-block;
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
        df_h = df_h.dropna(subset=['KOMODITAS'])
        return df_h
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 6. RENDER HALAMAN ---

# Tampilkan Badge Admin Jika Mode Aktif
if is_admin:
    st.markdown('<div class="admin-badge">🔓 MODE EDITOR AKTIF (PRIVATE URL)</div>', unsafe_allow_html=True)

if not df_harga.empty:
    
    # --- BERANDA ---
    if st.session_state.menu_aktif == "🏠 Dashboard":
        # Header Bupati
        img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
        img_l = get_img_as_base64("logo_ngada.png")
        
        st.markdown(f"""
            <div class="pimpinan-container">
                <img src="data:image/jpeg;base64,{img_p}" class="pimpinan-img">
                <div class="pimpinan-text">
                    <img src="data:image/png;base64,{img_l}" width="40">
                    <h3 style="margin:0; color:#059669;">Pemerintah Kabupaten Ngada</h3>
                    <p style="margin:0; font-size:0.9rem; opacity:0.8;">Bagian Perekonomian & SDA - Setda Ngada</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Hero (Dapat diubah oleh Admin)
        st.markdown(f'''
            <div class="hero-section">
                <h1>{global_settings["hero_title"]}</h1>
                <p>{global_settings["hero_subtitle"]}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Grid Menu
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
                st.markdown(f'<div class="menu-card"><div class="menu-icon">{m["icon"]}</div><div class="menu-title">{m["title"]}</div></div>', unsafe_allow_html=True)
                if st.button(f"Buka {m['title']}", key=f"btn_{i}", use_container_width=True):
                    set_menu(m["target"])
                    st.rerun()
        
        # FITUR EDIT KHUSUS ADMIN DI HALAMAN DEPAN
        if is_admin:
            st.divider()
            with st.expander("🛠️ PENGATURAN HERO (HANYA ADMIN)"):
                global_settings["hero_title"] = st.text_input("Ganti Judul Hero:", global_settings["hero_title"])
                global_settings["hero_subtitle"] = st.text_area("Ganti Sub-judul Hero:", global_settings["hero_subtitle"])
                if st.button("Simpan Perubahan Hero"):
                    st.success("Tampilan Hero diperbarui!")
                    st.rerun()

    # --- SUB-MENU ---
    else:
        if st.button("⬅️ Kembali ke Beranda"):
            set_menu("🏠 Dashboard")
            st.rerun()
        
        st.divider()

        # Contoh tampilan menu Harga Pasar
        if st.session_state.menu_aktif == "🛒 Harga Pasar":
            st.subheader("🛒 Monitoring Harga Pasar Hari Ini")
            st.dataframe(df_harga, use_container_width=True)
            
        # Menu Komitmen (Dapat diubah oleh Admin)
        elif st.session_state.menu_aktif == "ℹ️ Komitmen ASN":
            st.subheader("🏛️ Visi & Misi")
            st.info(global_settings["about_text"])
            
            if is_admin:
                st.divider()
                new_about = st.text_area("Edit Teks Komitmen (Hanya Admin):", global_settings["about_text"])
                if st.button("Simpan Teks Komitmen"):
                    global_settings["about_text"] = new_about
                    st.success("Teks Komitmen diperbarui!")
                    st.rerun()
else:
    st.error("Data tidak ditemukan.")
