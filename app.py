import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide")

# --- 2. LOGIKA MEMORI ---
@st.cache_resource
def get_global_settings():
    return {
        "pilihan_admin": [],
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
    }

global_settings = get_global_settings()
jalur_rahasia = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM (TEKS HITAM PEKAT) ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, div, label { color: #000000 !important; font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FFFFFF !important; }
    .hero-section { background: linear-gradient(135deg, #059669 0%, #10B981 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; color: white !important; }
    .hero-section h1, .hero-section p { color: white !important; }
    .card-container { background: white !important; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 10px; border-left: 10px solid #059669; }
    .status-badge { padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 4. MUAT DATA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        # LINK CSV HASIL PUBLISH TO WEB
        URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=1673392597&single=true&output=csv"
        
        df = pd.read_csv(URL, skiprows=6)
        # Ambil kolom: A(0), C(2), D(3), E(4), F(5), G(6)
        df = df.iloc[:, [0, 2, 3, 4, 5, 6]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KEMARIN', 'B_HARI_INI', 'K_KEMARIN', 'K_HARI_INI']
        df = df.dropna(subset=['KOMODITAS'])

        # Bersihkan angka dari titik/karakter agar bisa dihitung
        for col in ['B_KEMARIN', 'B_HARI_INI', 'K_KEMARIN', 'K_HARI_INI']:
            df[col] = df[col].astype(str).str.replace('.', '').str.replace(',', '').str.replace('-', '0').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        return None

df = load_data()

# --- 5. SIDEBAR ---
with st.sidebar:
    img_pimpinan = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_logo = get_img_as_base64("logo_ngada.png")
    st.markdown(f"""
        <div style="position: relative; width: 100%; height: 180px; border-radius: 15px; overflow: hidden; margin-bottom: 15px;">
            <img src="data:image/jpeg;base64,{img_pimpinan}" style="width: 100%; height: 100%; object-fit: cover;">
            <div style="position: absolute; bottom: 5px; left: 5px; background: rgba(255,255,255,0.9); padding: 5px; border-radius: 5px;">
                <img src="data:image/png;base64,{img_logo}" width="30"><br>
                <b style="font-size: 0.6rem; color: #059669;">Bagian Perekonomian & SDA</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
    pilihan = st.radio("Navigasi:", ["🏠 Dashboard", "📈 Tren Harga"])
    is_admin = jalur_rahasia

# --- 6. TAMPILAN ---
if df is not None:
    if pilihan == "🏠 Dashboard":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            # Jika baris adalah Judul Kategori (Satuan kosong)
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "" or str(row['SATUAN']) == "0":
                st.markdown(f"<h3 style='border-bottom: 2px solid #059669; padding-top:20px;'>📂 {row['KOMODITAS']}</h3>", unsafe_allow_html=True)
            else:
                # Logika Selisih
                selisih = row['K_HARI_INI'] - row['K_KEMARIN']
                if selisih > 0:
                    status = f"<span class='status-badge' style='background:#FEE2E2; color:#DC2626;'>🔺 Naik Rp {selisih:,.0f}</span>"
                elif selisih < 0:
                    status = f"<span class='status-badge' style='background:#D1FAE5; color:#059669;'>🔻 Turun Rp {abs(selisih):,.0f}</span>"
                else:
                    status = f"<span class='status-badge' style='background:#F1F5F9; color:#64748B;'>➖ Stabil</span>"

                st.markdown(f"""
                <div class="card-container">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><b>{row['KOMODITAS']}</b><br><small>Satuan: {row['SATUAN']}</small></div>
                        <div style="text-align:right;">
                            {status}<br>
                            <span style="font-size:1.2rem; font-weight:800;">Rp {row['K_HARI_INI']:,.0f}</span><br>
                            <small>Besar: Rp {row['B_HARI_INI']:,.0f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    elif pilihan == "📈 Tren Harga":
        st.title("📈 Analisis Tren Harga")
        df_v = df[df['SATUAN'].notna()]
        if is_admin:
            global_settings["pilihan_admin"] = st.multiselect("Pilih Komoditas:", df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
        
        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            fig = px.bar(df_p, x="KOMODITAS", y=["K_KEMARIN", "K_HARI_INI"], barmode="group", color_discrete_map={"K_KEMARIN": "#94A3B8", "K_HARI_INI": "#059669"})
            st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ Data gagal dimuat. Cek kembali link CSV di kodingan.")
