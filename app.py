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

# --- 2. LOGIKA MEMORI ---
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

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    
    .sidebar-header-box {
        position: relative; width: 100%; height: 220px;
        border-radius: 15px; overflow: hidden; margin-bottom: 20px;
        border: 2px solid #059669;
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; z-index: 1; }
    .overlay-info {
        position: absolute; bottom: 10px; left: 10px; z-index: 2;
        background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 8px;
        border: 1px solid #059669;
    }

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
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .price-main { font-size: 1.4rem; font-weight: 800; }
    .price-box { text-align: right; border-left: 1px solid #EEE; padding-left: 15px; min-width: 140px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. IMAGE HELPER ---
def get_img_as_base64(file):
    try:
        if os.path.exists(file):
            with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- 5. MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        
        # Data Berita (Gid 201409714 sesuai permintaanmu)
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h.dropna(subset=['KOMODITAS']), df_b.dropna(subset=['Kegiatan']).fillna("")
    except Exception as e:
        st.error(f"Koneksi Data Terputus: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 6. SIDEBAR ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_l = get_img_as_base64("logo_ngada.png")
    
    st.markdown(f"""
    <div class="sidebar-header-box">
        <img src="data:image/jpeg;base64,{img_p}" class="bg-pimpinan">
        <div class="overlay-info">
            <img src="data:image/png;base64,{img_l}" width="35">
            <div style="font-size:0.65rem; font-weight:800; color:#059669;">Bagian Perekonomian & SDA<br>Setda Kab. Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard", "📈 Tren Harga", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen ASN"
    ])
    
    if is_admin: st.success("🔓 MODE EDITOR AKTIF")

# --- 7. TAMPILAN UTAMA ---
if pilihan == "🏠 Dashboard":
    st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    
    col_foto, col_data = st.columns([1, 2.3])
    
    with col_foto:
        if os.path.exists("IMG_20251125_111048.jpg"):
            st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Pasar")
        st.info("Data diperbarui setiap hari kerja.")

    with col_data:
        search = st.text_input("🔍 Cari komoditas...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
        
        for _, row in df_show.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            
            k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
            k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
            sel = k_ini - k_kmrn
            warna = "#DC2626" if sel > 0 else ("#059669" if sel < 0 else "#94A3B8")
            
            st.markdown(f"""
            <div class="card-container" style="border-left: 10px solid {warna};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 2;">
                        <b style="font-size:1.1rem;">{row["KOMODITAS"]}</b><br>
                        <small>Satuan: {row["SATUAN"]}</small>
                    </div>
                    <div class="price-box">
                        <div style="font-size:0.7rem; color:#64748B;">Pedagang Kecil</div>
                        <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                        <small style="color:{warna}; font-weight:bold;">{"▲" if sel>0 else ("▼" if sel<0 else "—")} Rp {abs(sel):,}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif pilihan == "📰 Media & Berita":
    st.title("📰 Media & Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""
                <div class="card-container">
                    <small style="color:#059669; font-weight:bold;">{row['Tipe']}</small>
                    <h3 style="margin:5px 0;">{row['Kegiatan']}</h3>
                    <p style="font-size:0.85rem; color:gray;">📅 {row['Tanggal']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']):
                        st.image(link, use_container_width=True)
                    st.markdown(f'<a href="{link}" target="_blank" style="display:inline-block; background:#059669; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">🔗 Lihat Detail Berita</a>', unsafe_allow_html=True)
                st.divider()
    else:
        st.warning("Belum ada berita yang tersedia di Spreadsheet.")

elif pilihan == "📈 Tren Harga":
    st.title("📈 Analisis Tren Harga")
    # Logika Tren (Bisa disesuaikan lagi)
    st.info("Pilih komoditas di dashboard untuk melihat tren rincinya.")

elif pilihan == "📥 Pusat Unduhan":
    st.title("📥 Pusat Unduhan")
    st.download_button("📥 Unduh Data Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv")

elif pilihan == "ℹ️ Komitmen ASN":
    st.title("ℹ️ Komitmen Smart ASN")
    st.markdown(f'<div class="card-container"><h3>Visi & Misi</h3><p>{global_settings["about_text"]}</p></div>', unsafe_allow_html=True)
