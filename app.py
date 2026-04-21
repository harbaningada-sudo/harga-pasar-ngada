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

# --- 2. LOGIKA MEMORI & NAVIGASI ---
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

# Inisialisasi state menu
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "🏠 Dashboard"

def set_menu(nama_menu):
    st.session_state.menu_aktif = nama_menu

# --- 3. CSS KUSTOM (UI MODERN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }
    .stApp { background-color: #F8FAFC !important; }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 50px 30px; border-radius: 25px; margin-bottom: 30px; text-align: center;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.15);
    }
    .hero-section h1 { color: #FFFFFF !important; font-size: 2.5rem !important; font-weight: 800; margin-bottom: 10px; }
    .hero-section p { color: #ECFDF5 !important; font-size: 1.1rem; opacity: 0.9; }

    /* Card Menu di Beranda */
    .menu-card {
        background: white; padding: 20px; border-radius: 18px; text-align: center;
        border: 1px solid #E2E8F0; transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        height: 180px; display: flex; flex-direction: column; justify-content: center;
        margin-bottom: 10px;
    }
    .menu-card:hover { transform: translateY(-5px); border-color: #059669; box-shadow: 0 12px 20px rgba(0,0,0,0.1); }
    .menu-icon { font-size: 2.8rem; margin-bottom: 8px; }
    .menu-title { font-weight: 800; font-size: 0.9rem; color: #059669 !important; letter-spacing: 0.5px; }

    /* Card Item Harga */
    .price-card {
        background: white !important; padding: 18px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .group-label {
        background: #059669 !important; color: white !important; padding: 8px 15px; 
        border-radius: 8px; margin-top: 20px; font-weight: 700; font-size: 0.9rem;
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
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1)
        df_h = df_h.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        df_h = df_h.dropna(subset=['KOMODITAS'])

        # Data Berita
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 6. RENDER HALAMAN ---
if not df_harga.empty:
    
    # Logo Header
    img_l = get_img_as_base64("logo_ngada.png")
    if img_l: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_l}" width="60"></div>', unsafe_allow_html=True)

    # A. HALAMAN BERANDA
    if st.session_state.menu_aktif == "🏠 Dashboard":
        st.markdown(f'''
            <div class="hero-section">
                <h1>{global_settings["hero_title"]}</h1>
                <p>{global_settings["hero_subtitle"]}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Grid 5 Kolom
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
                if st.button(f"Buka {m['title']}", key=f"btn_{i}", use_container_width=True):
                    set_menu(m["target"])
                    st.rerun()

    # B. HALAMAN DETAIL (Sub-Menu)
    else:
        if st.button("⬅️ Kembali ke Menu Utama"):
            set_menu("🏠 Dashboard")
            st.rerun()
        
        st.divider()

        # 1. Menu Harga Pasar (Konten yang dipindahkan)
        if st.session_state.menu_aktif == "🛒 Harga Pasar":
            st.subheader("🛒 Monitoring Harga Pasar Hari Ini")
            
            col_img, col_list = st.columns([1, 2.3])
            with col_img:
                file_foto = "IMG_20251125_111048.jpg"
                if os.path.exists(file_foto):
                    st.image(file_foto, use_container_width=True, caption="Pantauan Pasar Ngada")
                st.info("Data diperbarui setiap hari kerja berdasarkan pantauan lapangan.")
                
            with col_list:
                search = st.text_input("🔍 Cari komoditas...", "")
                df_f = df_harga.copy()
                if search: df_f = df_f[df_f['KOMODITAS'].str.contains(search, case=False, na=False)]
                
                for _, row in df_f.iterrows():
                    # Header Kategori
                    if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                        st.markdown(f'<div class="group-label">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                        continue
                    
                    try:
                        k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                        k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                        sel = k_ini - k_kmrn
                        warna = "#DC2626" if sel > 0 else ("#059669" if sel < 0 else "#94A3B8")
                        ikon = "🔺" if sel > 0 else ("🔻" if sel < 0 else "➖")

                        st.markdown(f'''
                            <div class="price-card" style="border-left: 6px solid {warna};">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <b style="font-size:1rem;">{row["KOMODITAS"]}</b><br>
                                        <small style="color:#64748B;">Satuan: {row["SATUAN"]}</small>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color:{warna}; font-weight:800; font-size:1.1rem;">Rp {k_ini:,}</div>
                                        <small style="color:#94A3B8;">{ikon} Selisih: Rp {abs(sel):,}</small>
                                    </div>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                    except: continue

        # 2. Menu Tren Harga
        elif st.session_state.menu_aktif == "📈 Tren Harga":
            st.subheader("📈 Analisis Tren Harga")
            df_v = df_harga.dropna(subset=['SATUAN'])
            items = st.multiselect("Pilih Komoditas:", options=df_v['KOMODITAS'].unique())
            if items:
                df_p = df_v[df_v['KOMODITAS'].isin(items)]
                df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Periode', value_name='Harga')
                fig = px.bar(df_m, x="KOMODITAS", y="Harga", color="Periode", barmode="group", color_discrete_map={'KECIL_KMRN': '#94A3B8', 'KECIL_INI': '#059669'})
                st.plotly_chart(fig, use_container_width=True)

        # 3. Menu Berita
        elif st.session_state.menu_aktif == "📰 Media & Berita":
            st.subheader("📰 Update Berita Ekonomi")
            for _, row in df_berita.iloc[::-1].iterrows():
                st.markdown(f'<div class="price-card"><b>{row["Kegiatan"]}</b><br><small>📅 {row["Tanggal"]}</small></div>', unsafe_allow_html=True)
                if str(row['Link']).startswith("http"):
                    st.link_button("Lihat Publikasi", str(row['Link']))

        # 4. Menu Download
        elif st.session_state.menu_aktif == "📥 Pusat Unduhan":
            st.subheader("📥 Download Data")
            st.write("Silakan unduh database harga terbaru.")
            st.download_button("Download CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

        # 5. Menu Komitmen
        elif st.session_state.menu_aktif == "ℹ️ Komitmen ASN":
            st.subheader("🏛️ Visi & Misi")
            st.markdown(f'<div class="price-card" style="line-height:1.7;">{global_settings["about_text"]}</div>', unsafe_allow_html=True)
            if is_admin:
                new_text = st.text_area("Edit Teks:", value=global_settings["about_text"])
                if st.button("Simpan Perubahan"):
                    global_settings["about_text"] = new_text
                    st.success("Teks diperbarui!")
                    st.rerun()
else:
    st.error("Koneksi ke data Google Sheets bermasalah.")
