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

# DETEKSI JALUR RAHASIA
# Jika URL mengandung ?status=set, maka is_admin langsung TRUE
is_admin = st.query_params.get("status") == "set"

# --- 3. CSS KUSTOM ---
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
    .price-box { text-align: right; border-left: 1px solid #EEE; padding-left: 15px; }
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

        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
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
            <img src="data:image/png;base64,{img_l}" width="40">
            <div style="font-size:0.7rem; font-weight:800; color:#059669;">Bagian Perekonomian & SDA<br>Setda Kab. Ngada</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_admin:
        st.success("🔓 MODE EDITOR AKTIF")

    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard Beranda", "📈 Tren Harga Komoditas", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen Smart ASN"
    ])

# --- 7. TAMPILAN DASHBOARD ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown(f'<div class="hero-section"><h1>{global_settings["hero_title"]}</h1><p>{global_settings["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
        
        # FITUR EDIT UNTUK ADMIN
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT DASHBOARD"):
                new_title = st.text_input("Judul Dashboard:", value=global_settings["hero_title"])
                new_sub = st.text_area("Sub-judul Dashboard:", value=global_settings["hero_subtitle"])
                if st.button("💾 Simpan Perubahan Dashboard"):
                    global_settings["hero_title"] = new_title
                    global_settings["hero_subtitle"] = new_sub
                    st.success("Dashboard diperbarui!")
                    st.rerun()

        col_foto, col_data = st.columns([1, 2.5])
        with col_foto:
            if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)
        
        with col_data:
            search = st.text_input("🔍 Cari komoditas...", "")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
            
            for _, row in df_show.iterrows():
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                    st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                    continue
                try:
                    k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                    k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                    sel = k_ini - k_kmrn
                    warna = "#DC2626" if sel > 0 else "#059669" if sel < 0 else "#94A3B8"
                    ikon = "🔺" if sel > 0 else "🔻" if sel < 0 else "➖"
                    st.markdown(f"""
                    <div class="card-container">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;"><b>{row["KOMODITAS"]}</b><br><small>{row["SATUAN"]}</small></div>
                            <div class="price-box" style="flex: 1.5;"><small>Pedagang Besar</small><br><b>Rp {int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0):,}</b></div>
                            <div class="price-box" style="flex: 1.5;"><small>Pedagang Kecil</small><br><b style="color:{warna};">Rp {k_ini:,}</b><br><small style="color:{warna};">{ikon} {abs(sel):,}</small></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Tren Harga Komoditas")
        df_v = df_harga.dropna(subset=['SATUAN'])
        
        if is_admin:
            st.warning("⚙️ PANEL ADMIN: KUNCI TREN PUBLIK")
            pilihan_baru = st.multiselect("Pilih komoditas yang ingin ditampilkan ke publik:", options=df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
            if st.button("🚀 Publikasikan ke Semua Device"):
                global_settings["pilihan_admin"] = pilihan_baru
                st.success("Tren berhasil dikunci dan dipublikasikan!")
                st.rerun()
        
        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
            st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group", color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#059669'}), use_container_width=True)
        else:
            st.info("💡 Belum ada data tren yang dipilih oleh Admin.")

    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Komitmen Smart ASN")
        st.markdown(f'<div class="card-container"><h3>Visi & Misi</h3><p>{global_settings["about_text"]}</p></div>', unsafe_allow_html=True)
        if is_admin:
            with st.expander("🛠️ PANEL ADMIN: EDIT TENTANG KAMI"):
                new_about = st.text_area("Isi Komitmen:", value=global_settings["about_text"])
                if st.button("💾 Simpan Perubahan Komitmen"):
                    global_settings["about_text"] = new_about
                    st.success("Teks komitmen diperbarui!")
                    st.rerun()
else:
    st.error("Data gagal dimuat.")
