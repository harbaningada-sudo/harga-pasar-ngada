import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Digital Ngada", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. LOGIKA KEAMANAN ADMIN (DOUBLE SECURITY) ---
# Mantra URL: ?role=admin
# Email: harbaningada-sudo@gmail.com
EMAIL_ADMIN = "harbaningada-sudo@gmail.com"

def check_admin():
    # Cek via URL mantra
    if st.query_params.get("role") == "admin":
        return True
    # Cek via Email login
    try:
        if st.user.email == EMAIL_ADMIN:
            return True
    except:
        pass
    return False

is_admin = check_admin()

# --- 3. MEMORI PUBLIK (GLOBAL CACHE) ---
@st.cache_resource
def get_global_settings():
    return {"pilihan_admin": []}

global_settings = get_global_settings()

# --- 4. CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B !important; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white !important;
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .group-header {
        background: #F1F5F9; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; margin-bottom: 15px; font-weight: 800;
        color: #0F172A; border-left: 10px solid #059669;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .card-container {
        background: white !important; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .price-main { font-size: 1.5rem; font-weight: 800; color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"): st.image("logo_ngada.png", use_container_width=True)
    st.divider()
    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard Beranda", 
        "📈 Tren Harga Komoditas", 
        "📰 Media & Berita", 
        "📥 Pusat Unduhan", 
        "ℹ️ Komitmen Smart ASN"
    ])
    
    # PANEL ADMIN (Hanya Muncul Jika Syarat Terpenuhi)
    mode_admin = False
    if is_admin:
        st.divider()
        st.markdown("### 🔐 Panel Kontrol Admin")
        mode_admin = st.checkbox("Aktifkan Kunci Tren")

# --- 7. LOGIKA TAMPILAN ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown('<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.</p></div>', unsafe_allow_html=True)
        col_foto, col_data = st.columns([1, 2])
        with col_foto:
            if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Pasar")
        with col_data:
            search = st.text_input("🔍 Cari komoditas...", "")
            df_show = df_harga.copy()
            if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
            last_header = ""
            for _, row in df_show.iterrows():
                if row['KATEGORI_INDUK'] != last_header:
                    st.markdown(f'<div class="group-header">📂 {row["KATEGORI_INDUK"]}</div>', unsafe_allow_html=True)
                    last_header = row['KATEGORI_INDUK']
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "": continue
                try:
                    h_ini = int(pd.to_numeric(row['HARGA HARI INI'], errors='coerce') or 0)
                    h_kmrn = int(pd.to_numeric(row['HARGA KEMARIN'], errors='coerce') or 0)
                    selisih = h_ini - h_kmrn
                    warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#94A3B8"
                    ikon = "🔺" if selisih > 0 else "🔻" if selisih < 0 else "➖"
                    st.markdown(f'<div class="card-container" style="border-left: 10px solid {warna};"><div style="display: flex; justify-content: space-between; align-items: center;"><div><b>{row["KOMODITAS"]}</b><br><small>Satuan: {row["SATUAN"]}</small></div><div style="text-align: right;"><span class="price-main">Rp {h_ini:,}</span><br><span style="color: {warna}; font-weight: 700;">{ikon} Rp {abs(selisih):,}</span><br><small style="color: gray;">Kemarin: Rp {h_kmrn:,}</small></div></div></div>', unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Tren Harga Terkini")
        df_valid = df_harga.dropna(subset=['SATUAN'])
        list_komoditas = df_valid['KOMODITAS'].unique().tolist()
        
        if mode_admin:
            st.warning("⚠️ MODE ADMIN: Pilihan Anda tampil di semua device.")
            pilihan_baru = st.multiselect("Pilih komoditas:", options=list_komoditas, default=global_settings["pilihan_admin"])
            if st.button("🚀 Publikasikan ke Semua Device"):
                global_settings["pilihan_admin"] = pilihan_baru
                st.success("Tren berhasil diperbarui!")
        
        pilihan_final = global_settings["pilihan_admin"]
        if pilihan_final:
            df_plot = df_valid[df_valid['KOMODITAS'].isin(pilihan_final)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga (Rp)')
            fig = px.bar(df_plot, x="KOMODITAS", y="Harga (Rp)", color="Waktu", barmode="group", text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Belum ada data tren yang dipublikasikan oleh Admin.")

    elif pilihan == "📰 Media & Berita":
        st.title("📰 Media & Berita")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
            link = str(row['Link'])
            if link.startswith("http"):
                if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): st.image(link, use_container_width=True)
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; color:#4F46E5; font-weight:bold; padding:10px; background:#EEF2FF; border-radius:8px;">📂 Lihat Detail</a>', unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Open Data Center")
        col1, col2 = st.columns(2)
        with col1: st.download_button("Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2: st.download_button("Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Media_Ngada.csv", "text/csv", use_container_width=True)

    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Komitmen Smart ASN")
        st.markdown('<div class="card-container"><h3>Transparansi Berbasis Teknologi</h3><p>Inovasi digital ini menjamin masyarakat mendapatkan akses informasi harga yang jujur dan akurat langsung dari sumbernya.</p></div>', unsafe_allow_html=True)

else:
    st.error("⚠️ Gagal memuat data.")
