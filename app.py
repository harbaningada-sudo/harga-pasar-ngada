import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="auto"
)

# --- 2. CSS KUSTOM (KUNCI TEKS HITAM & NAVIGASI UTUH) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Global Reset & Kunci Teks Hitam di Body */
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        color: #1E293B !important; 
    }
    .stApp { background-color: #F8FAFC; }
    
    /* Header Hijau Pemkab */
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    
    /* Hero Banner Beranda */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white !important;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .hero-section h1, .hero-section p { color: white !important; }

    /* Card Box - Kunci Latar Putih & Teks Hitam */
    .card-container {
        background: white !important; 
        padding: 25px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-container h2, .card-container h3, .card-container p, .card-container span, .card-container b {
        color: #1E293B !important; /* Warna Hitam Slate */
    }
    .card-harga { border-left: 8px solid #059669; }

    /* Desain Tombol Link Dokumentasi */
    .link-tombol {
        display: inline-block; padding: 10px 20px; background-color: #EEF2FF;
        color: #4F46E5 !important; border-radius: 10px; text-decoration: none;
        font-weight: 600; font-size: 0.9rem; border: 1px solid #C7D2FE;
        margin-top: 10px;
    }
    .link-tombol:hover { background-color: #E0E7FF; border-color: #4F46E5; }

    /* Optimasi Mobile */
    @media (max-width: 640px) {
        .hero-section { padding: 25px; }
        .hero-section h1 { font-size: 1.4rem; }
        .card-container h3 { font-size: 1.1rem !important; }
        .link-tombol { display: block; text-align: center; width: 100%; }
    }

    /* Jarak Aman Atas */
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    # Data Harga Komoditas
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
    df_h['SELISIH (Rp)'] = pd.to_numeric(df_h['SELISIH (Rp)'], errors='coerce').fillna(0)
    
    # Data Berita & Dokumentasi
    url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df_b = pd.read_csv(url_b, skiprows=2)
    df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    
    # Filter baris kosong
    df_b = df_b.dropna(subset=['Kegiatan'])
    df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
    
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_all_data()
    data_ok = True
except Exception as e:
    data_ok = False
    pesan_error = e

# --- 4. SIDEBAR NAVIGASI (SEMUA MENU KEMBALI UTUH) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669; margin-top: -10px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Pilih Menu Layanan:", [
        "🏠 Dashboard Beranda", 
        "📈 Tren & Analisis Harga", 
        "📰 Berita & Media", 
        "📥 Pusat Unduhan", 
        "ℹ️ Informasi Layanan"
    ])

# --- 5. LOGIKA TAMPILAN KONTEN ---
if data_ok:
    # --- MENU 1: BERANDA ---
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown('<div class="hero-section"><h1>Halo, Bapak Mama & Saudara Semua! 👋</h1><p>Pantau harga pangan hari ini agar belanja lebih tenang dan terencana.</p></div>', unsafe_allow_html=True)
        search = st.text_input("🔍 Cari bahan makanan hari ini...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            selisih = int(row['SELISIH (Rp)'])
            warna = "#DC2626" if selisih > 0 else ("#059669" if selisih < 0 else "#64748B")
            simbol = "🔺" if selisih > 0 else ("🔹" if selisih < 0 else "➖")
            st.markdown(f"""
                <div class="card-container card-harga">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div><b>{row['KOMODITAS']}</b><br><small>Satuan: {row['SATUAN']}</small></div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.2rem; font-weight: 800; color: #059669;">Rp {int(row['HARGA HARI INI']):,}.00</span><br>
                            <span style="color: {warna}; font-size: 0.85rem; font-weight: 600;">{simbol} Selisih: Rp {abs(selisih):,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- MENU 2: TREN HARGA ---
    elif pilihan == "📈 Tren & Analisis Harga":
        st.title("📈 Komparasi Harga Pangan")
        list_k = df_harga['KOMODITAS'].unique().tolist()
        pick = st.multiselect("Pilih Komoditas:", options=list_k, default=list_k[:5])
        if pick:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pick)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    # --- MENU 3: BERITA & MEDIA (KLIK LINK & TEKS HITAM) ---
    elif pilihan == "📰 Berita & Media":
        st.markdown('<h2 style="color: #1E293B; margin-bottom: 20px;">📰 Berita & Dokumentasi Terkini</h2>', unsafe_allow_html=True)
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="card-container">
                        <h3 style="margin-top:0;">{row["Kegiatan"]}</h3>
                        <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 10px;">📅 Publikasi: {row["Tanggal"]}</p>
                    </div>
                """, unsafe_allow_html=True)
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    st.markdown(f'<a href="{link}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi Lengkap</a>', unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)

    # --- MENU 4: UNDUH DATA ---
    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Akses Data Terbuka")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📊 Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2:
            st.download_button("📰 Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Berita_Ngada.csv", "text/csv", use_container_width=True)

    # --- MENU 5: INFORMASI LAYANAN (TEKS HITAM) ---
    elif pilihan == "ℹ️ Informasi Layanan":
        st.markdown('<h2 style="color: #1E293B; margin-bottom: 20px;">ℹ️ Dari Kami, Untuk Ngada</h2>', unsafe_allow_html=True)
        st.markdown("""
            <div class="card-container">
                <h3>Mengapa Aplikasi Ini Ada?</h3>
                <p style="font-size: 1.1rem; line-height: 1.6;">
                    Aplikasi ini adalah wujud kepedulian kami, <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, 
                    untuk melindungi hak Bapak dan Mama mendapatkan informasi harga yang jujur dan transparan.
                </p>
                <p>Kesejahteraan keluarga di Ngada adalah prioritas utama kami.</p>
                <hr>
                <p style="font-size: 0.8rem; color: #94A3B8;">Dikembangkan untuk Proyek Aktualisasi CPNS Kabupaten Ngada Tahun 2026.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"⚠️ Gagal Memuat Data: {pesan_error}")
