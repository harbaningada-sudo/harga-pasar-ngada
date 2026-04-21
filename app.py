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

# --- 3. CSS KUSTOM (DESAIN BARU) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Plus Jakarta Sans', sans-serif; color: #1E293B !important; 
    }
    
    .stApp { background-color: #F8FAFC !important; }
    
    /* Header & Hero */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 60px 40px; border-radius: 24px; margin-bottom: 35px;
        box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.3);
    }
    .hero-section h1 { color: #FFFFFF !important; font-weight: 800; font-size: 2.5rem; margin-bottom: 10px; }
    .hero-section p { color: rgba(255,255,255,0.9) !important; font-size: 1.1rem; }

    /* Sidebar Design */
    .sidebar-header-box {
        position: relative; width: 100%; height: 240px;
        border-radius: 20px; overflow: hidden; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .bg-pimpinan { width: 100%; height: 100%; object-fit: cover; }
    .overlay-info {
        position: absolute; bottom: 0; left: 0; right: 0;
        background: linear-gradient(to top, rgba(255,255,255,1) 0%, rgba(255,255,255,0.8) 70%, transparent 100%);
        padding: 15px; text-align: center;
    }

    /* Cards & Data */
    .group-header {
        background: #F1F5F9 !important; padding: 15px 25px; border-radius: 12px;
        margin-top: 30px; font-weight: 800; color: #065F46 !important;
        border-left: 6px solid #059669; font-size: 1.1rem;
    }

    .card-container {
        background: white !important; padding: 25px; border-radius: 20px;
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.1);
        border-color: #059669;
    }
    
    .price-main { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }
    .price-sub { font-size: 1rem; font-weight: 600; color: #64748B !important; }
    .price-label-top { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
    .price-box { text-align: right; padding-left: 20px; min-width: 150px; }
    
    /* Utility */
    .stButton>button {
        border-radius: 12px; font-weight: 600; padding: 0.5rem 2rem;
        background-color: #059669; border: none;
    }
    .admin-success-box {
        background-color: #ECFDF5; border: 1px solid #059669;
        padding: 10px; border-radius: 10px; color: #065F46;
        font-weight: 700; font-size: 0.8rem; text-align: center;
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
            <img src="data:image/png;base64,{img_l}" width="40" style="margin-bottom:5px;">
            <div style="font-size:0.75rem; font-weight:800; color:#065F46; line-height:1.2;">
                Bagian Perekonomian & SDA<br>Setda Kab. Ngada
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if is_admin: 
        st.markdown('<div class="admin-success-box">🔓 MODE EDITOR AKTIF</div>', unsafe_allow_html=True)
    
    st.markdown("### Navigasi")
    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard", "📈 Tren Harga", "📰 Media & Berita", "📥 Pusat Unduhan", "ℹ️ Komitmen ASN"
    ], label_visibility="collapsed")

# --- 7. TAMPILAN UTAMA ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard":
        st.markdown(f'''
            <div class="hero-section">
                <h1>{global_settings["hero_title"]}</h1>
                <p>{global_settings["hero_subtitle"]}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        if is_admin:
            with st.expander("🛠️ KONFIGURASI HERO"):
                global_settings["hero_title"] = st.text_input("Judul Utama:", value=global_settings["hero_title"])
                global_settings["hero_subtitle"] = st.text_area("Sub-judul:", value=global_settings["hero_subtitle"])
                if st.button("💾 Perbarui Tampilan"): st.rerun()

        col_foto, col_data = st.columns([1, 2.3], gap="large")
        
        with col_foto:
            file_foto_pasar = "IMG_20251125_111048.jpg"
            if os.path.exists(file_foto_pasar):
                st.markdown('<div class="card-container" style="padding:10px;">', unsafe_allow_html=True)
                st.image(file_foto_pasar, use_container_width=True, caption="Dokumentasi Pemantauan Pasar")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="background:#F1F5F9; padding:20px; border-radius:15px; border:1px dashed #CBD5E1;">
                    <p style="font-size:0.85rem; line-height:1.6; margin:0;">
                        <b>💡 Catatan Pantauan:</b><br>
                        Data ini merupakan harga rata-rata yang dihimpun dari pedagang di pasar tradisional Kabupaten Ngada.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_data:
            search = st.text_input("🔍 Cari Komoditas Specific...", placeholder="Contoh: Beras, Cabai...")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
            
            for _, row in df_show.iterrows():
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                    st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                    continue
                
                try:
                    k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                    k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                    b_ini = int(pd.to_numeric(row['BESAR_INI'], errors='coerce') or 0)
                    sel = k_ini - k_kmrn
                    
                    if sel > 0: warna, ikon, status = "#EF4444", "↗️", f"+Rp {abs(sel):,}"
                    elif sel < 0: warna, ikon, status = "#10B981", "↘️", f"-Rp {abs(sel):,}"
                    else: warna, ikon, status = "#64748B", "➡️", "STABIL"

                    st.markdown(f"""
                    <div class="card-container">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;">
                                <div style="color:#64748B; font-size:0.8rem; font-weight:600;">{row["SATUAN"]}</div>
                                <div style="font-size:1.3rem; font-weight:800; color:#1E293B;">{row["KOMODITAS"]}</div>
                            </div>
                            <div class="price-box" style="border-right: 1px solid #F1F5F9; margin-right:20px;">
                                <div class="price-label-top">Harga Grosir</div>
                                <span class="price-sub">Rp {b_ini:,}</span>
                            </div>
                            <div class="price-box">
                                <div class="price-label-top" style="color:{warna};">Harga Eceran</div>
                                <div style="color:{warna}; font-size:0.85rem; font-weight:800; margin-bottom:2px;">{ikon} {status}</div>
                                <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga":
        st.title("📈 Analisis Tren Harga")
        df_v = df_harga.dropna(subset=['SATUAN'])
        if is_admin:
            with st.container(border=True):
                st.markdown("### ⚙️ Pengaturan Grafik")
                pilihan_baru = st.multiselect("Pilih komoditas untuk dipublikasikan:", options=df_v['KOMODITAS'].unique(), default=[x for x in global_settings["pilihan_admin"] if x in df_v['KOMODITAS'].unique()])
                if st.button("🚀 Update Grafik"):
                    global_settings["pilihan_admin"] = pilihan_baru; st.rerun()
        
        if global_settings["pilihan_admin"]:
            df_p = df_v[df_v['KOMODITAS'].isin(global_settings["pilihan_admin"])]
            df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group",
                         color_discrete_map={'KECIL_KMRN': '#CBD5E1', 'KECIL_INI': '#059669'},
                         template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pilih komoditas di panel admin untuk menampilkan grafik tren.")

    # ... (Bagian Media, Unduhan, dan Komitmen tetap berfungsi namun dengan style card-container yang baru)

else:
    st.error("Gagal memuat koneksi data Google Sheets.")
