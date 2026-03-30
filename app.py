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
    initial_sidebar_state="auto"
)

# --- 2. LOGIKA MEMORI PUBLIK ---
@st.cache_resource
def get_global_settings():
    return {
        "pilihan_admin": [],
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat."
    }

global_settings = get_global_settings()
jalur_rahasia = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px;
    }
    .hero-section h1, .hero-section p { color: #FFFFFF !important; }
    .group-header {
        background: #F1F5F9 !important; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; font-weight: 800; border-left: 10px solid #059669;
    }
    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px;
    }
    .sidebar-header-box {
        position: relative; width: 100%; height: 220px;
        border-radius: 15px; overflow: hidden; margin-bottom: 20px;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; z-index: 1; }
    .overlay-info {
        position: absolute; bottom: 10px; left: 10px; z-index: 2;
        background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 4. MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # GANTI LINK DI BAWAH INI DENGAN LINK CSV HASIL PUBLISH TO WEB TERBARU
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=1673392597&single=true&output=csv"
        
        # Baca data, loncati 6 baris header awal
        df_raw = pd.read_csv(url_h, skiprows=6) 
        
        # Ambil kolom A, C, D, E, F, G saja sesuai struktur baru
        df_h = df_raw.iloc[:, [0, 2, 3, 4, 5, 6]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KEMARIN', 'BESAR_HARI_INI', 'KECIL_KEMARIN', 'KECIL_HARI_INI']
        df_h = df_h.dropna(subset=['KOMODITAS'])
        
        # Logika Kategori
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories

        # Data Berita (gunakan link CSV yang sudah benar untuk berita juga jika perlu)
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except Exception as e:
        st.error(f"Detail Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 5. SIDEBAR ---
with st.sidebar:
    img_pimpinan = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_logo = get_img_as_base64("logo_ngada.png")
    st.markdown(f"""
    <div class="sidebar-header-box">
        <img src="data:image/jpeg;base64,{img_pimpinan}" class="bg-pimpinan">
        <div class="overlay-info">
            <img src="data:image/png;base64,{img_logo}" width="35">
            <div style="font-size:0.65rem; font-weight:800; color:#059669;">Bagian Perekonomian dan SDA<br>Setda Kab. Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    pilihan = st.radio("Menu:", ["🏠 Dashboard", "📈 Tren Harga", "📰 Media", "📥 Unduhan", "ℹ️ Komitmen"])
    is_admin = False
    if jalur_rahasia:
        pass_input = st.text_input("🔑 Pass", type="password")
        if pass_input == "ngada2026": is_admin = True

# --- 6. TAMPILAN ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        col_foto, col_data = st.columns([1, 2])
        with col_foto:
            if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)
        with col_data:
            search = st.text_input("🔍 Cari...", "")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]
            for _, row in df_show.iterrows():
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                    st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="card-container"><b>{row['KOMODITAS']}</b> ({row['SATUAN']})<br>
                    <small>Pedagang Besar: <b>Rp {row['BESAR_HARI_INI']}</b> | Pedagang Kecil: <b>Rp {row['KECIL_HARI_INI']}</b></small></div>""", unsafe_allow_html=True)
    
    elif pilihan == "📈 Tren Harga":
        st.title("📈 Tren Harga")
        df_valid = df_harga[df_harga['SATUAN'].notna()]
        if is_admin:
            list_k = df_valid['KOMODITAS'].unique().tolist()
            global_settings["pilihan_admin"] = st.multiselect("Pilih Tren:", list_k, default=[x for x in global_settings["pilihan_admin"] if x in list_k])
        
        if global_settings["pilihan_admin"]:
            df_p = df_valid[df_valid['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KEMARIN', 'KECIL_HARI_INI'], var_name='Waktu', value_name='Harga')
            st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group"))
else:
    st.warning("Data masih kosong atau link salah.")
