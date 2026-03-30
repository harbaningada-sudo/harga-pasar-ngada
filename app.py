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

# --- 3. CSS KUSTOM (FIX TEKS HITAM & UI ANALISIS) ---
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
    .status-badge {
        padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 4. MUAT DATA DENGAN LOGIKA ANALISIS ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Link CSV terbaru Bapak
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=1673392597&single=true&output=csv"
        
        df_raw = pd.read_csv(url_h, skiprows=6) 
        df_h = df_raw.iloc[:, [0, 2, 3, 4, 5, 6]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KEMARIN', 'BESAR_HARI_INI', 'KECIL_KEMARIN', 'KECIL_HARI_INI']
        df_h = df_h.dropna(subset=['KOMODITAS'])

        # Bersihkan Karakter Non-Angka (seperti titik atau spasi) agar bisa dihitung
        for col in ['BESAR_KEMARIN', 'BESAR_HARI_INI', 'KECIL_KEMARIN', 'KECIL_HARI_INI']:
            df_h[col] = pd.to_numeric(df_h[col].astype(str).str.replace('.', '').str.replace(',', '').str.replace('-', '0'), errors='coerce').fillna(0)

        # LOGIKA PERHITUNGAN (Fokus ke Pedagang Kecil)
        df_h['SELISIH'] = df_h['KECIL_HARI_INI'] - df_h['KECIL_KEMARIN']
        
        # Logika Kategori
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "" or str(row['SATUAN']).strip() == "0":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories

        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except Exception as e:
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
    pilihan = st.radio("Menu:", ["🏠 Dashboard", "📈 Tren Harga", "📰 Media", "ℹ️ Komitmen"])
    is_admin = jalur_rahasia

# --- 6. TAMPILAN DASHBOARD DENGAN ANALISIS ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        
        search = st.text_input("🔍 Cari Komoditas...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]
        
        for _, row in df_show.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "0" or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
            else:
                # Logika Ikon & Warna Berdasarkan Selisih
                selisih = row['SELISIH']
                if selisih > 0:
                    status_html = f'<span class="status-badge" style="background:#FEE2E2; color:#DC2626;">🔺 NAIK Rp {selisih:,.0f}</span>'
                    border_color = "#DC2626"
                elif selisih < 0:
                    status_html = f'<span class="status-badge" style="background:#D1FAE5; color:#059669;">🔻 TURUN Rp {abs(selisih):,.0f}</span>'
                    border_color = "#059669"
                else:
                    status_html = f'<span class="status-badge" style="background:#F1F5F9; color:#64748B;">➖ STABIL</span>'
                    border_color = "#E2E8F0"

                st.markdown(f"""
                <div class="card-container" style="border-left: 10px solid {border_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b style="font-size:1.1rem;">{row['KOMODITAS']}</b><br>
                            <small>Satuan: {row['SATUAN']}</small>
                        </div>
                        <div style="text-align: right;">
                            {status_html}<br>
                            <span style="font-size:1.2rem; font-weight:800;">Rp {row['KECIL_HARI_INI']:,.0f}</span><br>
                            <small style="color:gray;">Besar: Rp {row['BESAR_HARI_INI']:,.0f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    elif pilihan == "📈 Tren Harga":
        st.title("📈 Tren Harga")
        df_v = df_harga[df_harga['SATUAN'] != "0"]
        if is_admin:
            global_settings["pilihan_admin"] = st.multiselect("Pilih Komoditas:", df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
        
        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            fig = px.bar(df_p, x="KOMODITAS", y=["KECIL_KEMARIN", "KECIL_HARI_INI"], barmode="group", title="Perbandingan Harga (Eceran/Kecil)")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Gagal memuat data. Pastikan Spreadsheet sudah di-Publish to Web sebagai CSV.")
