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
    initial_sidebar_state="collapsed" # Kita sembunyikan sidebar agar lebih bersih
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

# Inisialisasi menu aktif jika belum ada
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "🏠 Dashboard"

def set_menu(nama_menu):
    st.session_state.menu_aktif = nama_menu

# --- 3. CSS KUSTOM (MODIFIKASI CARD MENU) ---
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
        padding: 60px 40px; border-radius: 30px; margin-bottom: 40px; text-align: center;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.2);
    }
    .hero-section h1 { color: #FFFFFF !important; font-size: 3rem !important; font-weight: 800; }
    .hero-section p { color: #ECFDF5 !important; font-size: 1.2rem; }

    /* Card Menu Utama */
    .menu-card {
        background: white; padding: 30px; border-radius: 20px; text-align: center;
        border: 1px solid #E2E8F0; transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .menu-card:hover { transform: translateY(-5px); border-color: #059669; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .menu-icon { font-size: 3.5rem; margin-bottom: 15px; display: block; }
    .menu-title { font-weight: 800; font-size: 1.1rem; margin-bottom: 10px; color: #059669 !important; }

    /* Card Data Harga */
    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 12px;
    }
    .group-header {
        background: #059669 !important; color: white !important; padding: 10px 20px; 
        border-radius: 10px; margin-top: 25px; font-weight: 700;
    }
    .price-main { font-size: 1.4rem; font-weight: 800; }
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

# --- 6. TAMPILAN UTAMA ---
if not df_harga.empty:
    
    # HEADER LOGO & ADMIN STATUS
    t1, t2 = st.columns([1, 5])
    with t1:
        img_l = get_img_as_base64("logo_ngada.png")
        if img_l: st.markdown(f'<img src="data:image/png;base64,{img_l}" width="80">', unsafe_allow_html=True)
    with t2:
        if is_admin: st.warning("🔓 MODE EDITOR AKTIF")

    # --- HALAMAN BERANDA (DASHBOARD) ---
    if st.session_state.menu_aktif == "🏠 Dashboard":
        # Hero Section
        st.markdown(f'''
            <div class="hero-section">
                <h1>{global_settings["hero_title"]}</h1>
                <p>{global_settings["hero_subtitle"]}</p>
            </div>
        ''', unsafe_allow_html=True)
        
        # GRID MENU (MIRIP GAMBAR REFERENSI)
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown('<div class="menu-card"><span class="menu-icon">📈</span><div class="menu-title">TREN HARGA</div><small>Pantau grafik fluktuasi</small></div>', unsafe_allow_html=True)
            if st.button("Buka Tren", use_container_width=True): set_menu("📈 Tren Harga"); st.rerun()

        with m2:
            st.markdown('<div class="menu-card"><span class="menu-icon">📰</span><div class="menu-title">BERITA & MEDIA</div><small>Update kegiatan terbaru</small></div>', unsafe_allow_html=True)
            if st.button("Baca Berita", use_container_width=True): set_menu("📰 Media & Berita"); st.rerun()

        with m3:
            st.markdown('<div class="menu-card"><span class="menu-icon">📥</span><div class="menu-title">DOWNLOAD</div><small>Unduh data CSV/Excel</small></div>', unsafe_allow_html=True)
            if st.button("Unduh Data", use_container_width=True): set_menu("📥 Pusat Unduhan"); st.rerun()

        with m4:
            st.markdown('<div class="menu-card"><span class="menu-icon">🏛️</span><div class="menu-title">KOMITMEN</div><small>Visi Misi Perekonomian</small></div>', unsafe_allow_html=True)
            if st.button("Lihat Visi", use_container_width=True): set_menu("ℹ️ Komitmen ASN"); st.rerun()

        st.markdown("<br><h2 style='text-align:center;'>📊 Monitoring Harga Pasar Hari Ini</h2>", unsafe_allow_html=True)

        # Layout Data: Foto vs Tabel Harga
        col_foto, col_data = st.columns([1, 2.3])
        
        with col_foto:
            file_foto_pasar = "IMG_20251125_111048.jpg"
            if os.path.exists(file_foto_pasar):
                st.image(file_foto_pasar, use_container_width=True, caption="Dokumentasi Pasar")
            
            # Info Tambahan
            st.info("💡 Data diperbarui setiap hari kerja berdasarkan pantauan langsung di pasar Kabupaten Ngada.")
            
            # Admin Editor
            if is_admin:
                with st.expander("🛠️ EDIT HERO SECTION"):
                    global_settings["hero_title"] = st.text_input("Judul Hero:", value=global_settings["hero_title"])
                    global_settings["hero_subtitle"] = st.text_area("Sub-judul Hero:", value=global_settings["hero_subtitle"])
                    if st.button("💾 Simpan"): st.rerun()

        with col_data:
            search = st.text_input("🔍 Cari nama bahan pokok...", "")
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
                    
                    warna = "#DC2626" if sel > 0 else ("#059669" if sel < 0 else "#94A3B8")
                    ikon = "🔺" if sel > 0 else ("🔻" if sel < 0 else "➖")
                    status = f"{'NAIK' if sel > 0 else 'TURUN'} Rp {abs(sel):,}" if sel != 0 else "STABIL"

                    st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid {warna};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 2;">
                                <b style="font-size:1.2rem;">{row["KOMODITAS"]}</b><br>
                                <span style="color:#64748B;">Satuan: {row["SATUAN"]}</span>
                            </div>
                            <div style="text-align: right; min-width: 150px;">
                                <div style="font-size:0.7rem; font-weight:700; color:{warna};">{ikon} {status}</div>
                                <div class="price-main" style="color:{warna};">Rp {k_ini:,}</div>
                                <small style="color: #64748B;">Grosir: Rp {b_ini:,}</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except: continue

    # --- HALAMAN LAIN (NAVIGASI BALIK) ---
    else:
        if st.button("⬅️ Kembali ke Beranda"):
            set_menu("🏠 Dashboard")
            st.rerun()
        
        st.divider()

        if st.session_state.menu_aktif == "📈 Tren Harga":
            st.title("📈 Analisis Tren Harga")
            df_v = df_harga.dropna(subset=['SATUAN'])
            pilihan_komo = st.multiselect("Pilih Komoditas:", options=df_v['KOMODITAS'].unique())
            if pilihan_komo:
                df_p = df_v[df_v['KOMODITAS'].isin(pilihan_komo)]
                df_m = df_p.melt(id_vars=['KOMODITAS'], value_vars=['KECIL_KMRN', 'KECIL_INI'], var_name='Waktu', value_name='Harga')
                st.plotly_chart(px.bar(df_m, x="KOMODITAS", y="Harga", color="Waktu", barmode="group"), use_container_width=True)

        elif st.session_state.menu_aktif == "📰 Media & Berita":
            st.title("📰 Media & Berita Ekonomi")
            for _, row in df_berita.iloc[::-1].iterrows():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
                link = str(row['Link'])
                if link.startswith("http"):
                    if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): st.image(link, use_container_width=True)
                    st.link_button("Lihat Detail", link)

        elif st.session_state.menu_aktif == "📥 Pusat Unduhan":
            st.title("📥 Download Data")
            st.info("Silakan unduh data dalam format CSV untuk kebutuhan analisis lebih lanjut.")
            st.download_button("Download Data Harga (.csv)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv")

        elif st.session_state.menu_aktif == "ℹ️ Komitmen ASN":
            st.title("🏛️ Visi & Misi Smart Economy")
            st.markdown(f'<div class="card-container" style="font-size:1.2rem; line-height:1.6;">{global_settings["about_text"]}</div>', unsafe_allow_html=True)

else:
    st.error("Data tidak ditemukan atau gagal dimuat.")
