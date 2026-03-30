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

# --- 3. CSS KUSTOM (WARNA DINAMIS & LAYOUT) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    header { background-color: #059669 !important; }
    
    .sidebar-header-box {
        position: relative; width: 100%; height: 220px;
        border-radius: 15px; overflow: hidden; margin-bottom: 20px;
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
        border: 1px solid #E2E8F0; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .price-main { font-size: 1.4rem; font-weight: 800; }
    .price-sub { font-size: 1rem; font-weight: 600; color: #475569 !important; }
    .status-label { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; }
    .price-box { text-align: right; border-left: 1px solid #EEE; padding-left: 15px; min-width: 150px; }
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

    if is_admin: st.success("🔓 MODE EDITOR AKTIF")
    pilihan = st.radio("Navigasi Menu:", ["🏠 Dashboard", "📈 Tren Harga", "ℹ️ Komitmen ASN"])

# --- 7. TAMPILAN DASHBOARD ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT DASHBOARD"):
                global_settings["hero_title"] = st.text_input("Judul:", value=global_settings["hero_title"])
                global_settings["hero_subtitle"] = st.text_area("Sub-judul:", value=global_settings["hero_subtitle"])
                if st.button("💾 Simpan Perubahan"): st.rerun()

        search = st.text_input("🔍 Cari komoditas...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
        
        for _, row in df_show.iterrows():
            # Header Kategori
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            
            # Logika Harga & Warna (Fokus Pedagang Kecil)
            try:
                k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
                sel = k_ini - k_kmrn
                
                # Penentuan Warna & Label
                if sel > 0:
                    warna, ikon, status = "#DC2626", "🔺", f"NAIK Rp {abs(sel):,}"
                elif sel < 0:
                    warna, ikon, status = "#059669", "🔻", f"TURUN Rp {abs(sel):,}"
                else:
                    warna, ikon, status = "#94A3B8", "➖", "STABIL"

                st.markdown(f"""
                <div class="card-container" style="border-left: 10px solid {warna};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 2;">
                            <b style="font-size:1.2rem;">{row["KOMODITAS"]}</b><br>
                            <small>Satuan: {row["SATUAN"]}</small>
                        </div>
                        <div class="price-box">
                            <small style="color: #64748B;">Pedagang Besar</small><br>
                            <span class="price-sub">Rp {b_ini:,}</span>
                        </div>
                        <div class="price-box">
                            <div style="color:{warna};" class="status-label">{ikon} {status}</div>
                            <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                            <small style="color: #64748B;">Kemarin: Rp {k_kmrn:,}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except: continue

    elif pilihan == "📈 Tren Harga":
        st.title("📈 Tren Harga Komoditas")
        df_v = df_harga.dropna(subset=['SATUAN'])
        if is_admin:
            pilihan_baru = st.multiselect("Pilih komoditas publik:", options=df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
            if st.button("🚀 Publikasikan Tren"):
                global_settings["pilihan_admin"] = pilihan_baru
                st.success("Tren diperbarui!"); st.rerun()
        
        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
            st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group", color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#059669'}), use_container_width=True)
        else:
            st.info("💡 Belum ada data tren yang dipilih oleh Admin.")

    elif pilihan == "ℹ️ Komitmen ASN":
        st.title("ℹ️ Komitmen Smart ASN")
        st.markdown(f'<div class="card-container"><h3>Visi & Misi</h3><p>{global_settings["about_text"]}</p></div>', unsafe_allow_html=True)
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT TENTANG KAMI"):
                global_settings["about_text"] = st.text_area("Isi Komitmen:", value=global_settings["about_text"])
                if st.button("💾 Simpan Perubahan Komitmen"): st.success("Diperbarui!"); st.rerun()
else:
    st.error("Gagal memuat data.")
