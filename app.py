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

# --- 2. CSS KUSTOM (SMART ASN & UI BERSIH) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B !important; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white !important;
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    /* Gaya Header Kelompok/Kategori */
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
    .border-naik { border-left: 10px solid #DC2626 !important; }
    .border-turun { border-left: 10px solid #059669 !important; }
    .border-stabil { border-left: 10px solid #94A3B8 !important; }
    
    .price-main { font-size: 1.4rem; font-weight: 800; color: #1E293B !important; }
    .price-sub { font-size: 0.85rem; color: #64748B !important; font-weight: 500; }
    
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        
        # Logika Kategori Otomatis berdasarkan baris yang satuannya kosong
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories

        # Data Media
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"): 
        st.image("logo_ngada.png", use_container_width=True)
    st.divider()
    pilihan = st.radio("Menu Layanan Digital:", [
        "🏠 Dashboard Beranda", 
        "📈 Tren Harga Komoditas", 
        "📰 Media & Berita", 
        "📥 Pusat Unduhan", 
        "ℹ️ Komitmen Smart ASN"
    ])

# --- 5. LOGIKA TAMPILAN ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown("""
            <div class="hero-section">
                <h1>Smart Economy Ngada 👋</h1>
                <p>Implementasi <b>Orientasi Pelayanan</b> melalui transparansi harga pasar. Kami hadir memberikan kepastian data yang akurat bagi Bapak Mama masyarakat Ngada.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Kolom Foto dan Harga
        col_foto, col_data = st.columns([1, 2])

        with col_foto:
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True, caption="Dokumentasi Pemantauan Lapangan")
            st.info("**Indikator:** 🔴 Naik | 🟢 Turun | ⚪ Stabil")

        with col_data:
            search = st.text_input("🔍 Cari komoditas atau kelompok (Contoh: Beras, Ayam, Cabai)...", "")
            df_show = df_harga.copy()
            if search:
                mask = (df_show['KOMODITAS'].str.contains(search, case=False, na=False)) | \
                       (df_show['KATEGORI_INDUK'].str.contains(search, case=False, na=False))
                df_show = df_show[mask]

            last_header = ""
            for _, row in df_show.iterrows():
                # Tampilkan Header Kelompok
                if row['KATEGORI_INDUK'] != last_header:
                    st.markdown(f'<div class="group-header">📂 KELOMPOK: {row["KATEGORI_INDUK"]}</div>', unsafe_allow_html=True)
                    last_header = row['KATEGORI_INDUK']

                # Abaikan baris judul itu sendiri di daftar kartu
                if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                    continue

                try:
                    h_ini = int(pd.to_numeric(row['HARGA HARI INI'], errors='coerce') or 0)
                    h_kmrn = int(pd.to_numeric(row['HARGA KEMARIN'], errors='coerce') or 0)
                    selisih = h_ini - h_kmrn
                    
                    if selisih > 0: css, ikon, warna, ket = "border-naik", "🔺", "#DC2626", f"Naik Rp {abs(selisih):,}"
                    elif selisih < 0: css, ikon, warna, ket = "border-turun", "🔻", "#059669", f"Turun Rp {abs(selisih):,}"
                    else: css, ikon, warna, ket = "border-stabil", "➖", "#64748B", "Stabil"

                    st.markdown(f"""
                        <div class="card-container {css}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div><b>{row['KOMODITAS']}</b><br><small>Satuan: {row['SATUAN']}</small></div>
                                <div style="text-align: right;">
                                    <span class="price-main">Rp {h_ini:,}</span><br>
                                    <span style="color: {warna}; font-weight: 700; font-size: 0.95rem;">{ikon} {ket}</span><br>
                                    <span class="price-sub">Kemarin: Rp {h_kmrn:,}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                except: continue

    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Analisis Perbandingan Harga")
        df_chart = df_harga.dropna(subset=['SATUAN'])
        fig = px.bar(df_chart, x="KOMODITAS", y="HARGA HARI INI", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📰 Media & Berita":
        st.title("📰 Dokumentasi & Publikasi")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
            if str(row['Link']).startswith("http"):
                st.markdown(f'<a href="{row["Link"]}" target="_blank" style="text-decoration:none; color:#4F46E5; font-weight:bold;">📂 Lihat Detail</a>', unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Open Data Center")
        col1, col2 = st.columns(2)
        with col1: st.download_button("Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2: st.download_button("Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Media_Ngada.csv", "text/csv", use_container_width=True)

    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Komitmen Melayani")
        st.markdown('<div class="card-container"><h3>Hospitality & Integritas</h3><p>Sebagai Smart ASN, kami berkomitmen memberikan pelayanan prima melalui penguasaan teknologi informasi untuk transparansi harga komoditas bagi masyarakat Ngada.</p><hr><p style="font-size: 0.85rem; color: #94A3B8;">Proyek Aktualisasi Latsar CPNS Ngada 2026.</p></div>', unsafe_allow_html=True)

else:
    st.error("⚠️ Gagal memuat data.")
