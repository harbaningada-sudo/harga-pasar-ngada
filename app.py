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

# --- 2. CSS KUSTOM (SMART ASN & MODERN UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
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
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .hero-section h1, .hero-section p { color: white !important; }

    /* Card Box - Kunci Latar Putih & Teks Hitam */
    .card-container {
        background: white !important; 
        padding: 25px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-container h2, .card-container h3, .card-container p, .card-container span, .card-container b {
        color: #1E293B !important;
    }
    
    /* Garis Indikator Samping */
    .border-naik { border-left: 10px solid #DC2626 !important; }
    .border-turun { border-left: 10px solid #059669 !important; }
    .border-stabil { border-left: 10px solid #94A3B8 !important; }

    .price-main { font-size: 1.5rem; font-weight: 800; color: #1E293B !important; }
    .price-sub { font-size: 0.9rem; color: #64748B !important; font-weight: 500; }

    /* Tombol Link Dokumentasi */
    .link-tombol {
        display: inline-block; padding: 10px 20px; background-color: #EEF2FF;
        color: #4F46E5 !important; border-radius: 10px; text-decoration: none;
        font-weight: 600; font-size: 0.9rem; border: 1px solid #C7D2FE;
        margin-top: 10px;
    }

    /* Jarak Aman Atas */
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
        df_h['HARGA KEMARIN'] = pd.to_numeric(df_h['HARGA KEMARIN'], errors='coerce').fillna(0)
        
        # Data Berita
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = df_b.dropna(subset=['Kegiatan'])
        df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
        
        return df_h, df_b.fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 4. INISIALISASI SESSION STATE (MEMORI TREN HARGA) ---
if 'pilihan_komoditas' not in st.session_state:
    if not df_harga.empty:
        st.session_state.pilihan_komoditas = df_harga['KOMODITAS'].unique().tolist()[:5]
    else:
        st.session_state.pilihan_komoditas = []

# --- 5. SIDEBAR NAVIGASI (SEMUA MENU KEMBALI) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669; margin-top: -10px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Pilih Menu Layanan:", [
        "🏠 Dashboard Beranda", 
        "📈 Tren & Analisis Smart Data", 
        "📰 Berita & Media Digital", 
        "📥 Pusat Unduhan Data", 
        "ℹ️ Komitmen Smart ASN"
    ])

# --- 6. LOGIKA TAMPILAN KONTEN ---
if not df_harga.empty:
    # --- MENU 1: BERANDA ---
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown("""
            <div class="hero-section">
                <h1>Smart Economy Ngada 👋</h1>
                <p>Mewujudkan transformasi digital dalam pengawasan harga pasar. Kami hadir memberikan kepastian data yang akurat, akuntabel, dan transparan bagi seluruh masyarakat Ngada.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_img, col_leg = st.columns([1, 2])
        with col_img:
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                st.image(img_path, width=320, caption="Digitalisasi Monitoring Lapangan")
        with col_leg:
            st.info("""
                **Sistem Indikator Digital:**
                * 🔴 **Merah:** Harga mengalami kenaikan.
                * 🟢 **Hijau:** Harga mengalami penurunan.
                * ⚪ **Abu-abu:** Harga terpantau stabil.
            """)

        st.divider()
        search = st.text_input("🔍 Cari komoditas hari ini (Smart Search)...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            h_ini, h_kmrn = int(row['HARGA HARI INI']), int(row['HARGA KEMARIN'])
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
                            <span class="price-sub">Harga Kemarin: Rp {h_kmrn:,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- MENU 2: TREN HARGA (DENGAN MEMORI) ---
    elif pilihan == "📈 Tren & Analisis Smart Data":
        st.title("📈 Smart Data Analytics")
        st.markdown("Analisis perbandingan harga berbasis data digital.")
        st.divider()
        list_k = df_harga['KOMODITAS'].unique().tolist()
        
        # Validasi pilihan agar tidak error
        valid_defaults = [v for v in st.session_state.pilihan_komoditas if v in list_k]
        pilih_baru = st.multiselect("Pilih Komoditas Pengawasan:", options=list_k, default=valid_defaults)
        st.session_state.pilihan_komoditas = pilih_baru
        
        if pilih_baru:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pilih_baru)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    # --- MENU 3: BERITA ---
    elif pilihan == "📰 Berita & Media Digital":
        st.title("📰 Dokumentasi & Publikasi")
        st.divider()
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p style="color: #64748B; font-size: 0.85rem;">📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    st.markdown(f'<a href="{link}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi Lengkap</a>', unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)

    # --- MENU 4: UNDUH DATA ---
    elif pilihan == "📥 Pusat Unduhan Data":
        st.title("📥 Open Data Center")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📊 Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2:
            st.download_button("📰 Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Berita_Ngada.csv", "text/csv", use_container_width=True)

    # --- MENU 5: INFORMASI LAYANAN (SMART ASN NARASI) ---
    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Menuju Birokrasi Digital")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Dedikasi Untuk Ngada</h3>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Sebagai bagian dari <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, kami berkomitmen menjadi <b>Smart ASN</b> yang adaptif, berintegritas, dan profesional dalam melayani masyarakat di era digital.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Aplikasi ini adalah bukti nyata inovasi pelayanan publik untuk memastikan setiap warga Ngada mendapatkan hak atas informasi harga yang jujur dan transparan. Kesejahteraan Bapak Mama adalah prioritas utama kami.
                </p>
                <hr>
                <p style="font-size: 0.85rem; color: #94A3B8;">
                    <b>Visi Smart ASN:</b> Integritas | Nasionalisme | Profesionalisme | Berwawasan Global | IT & Bahasa Asing | Hospitality | Networking | Entrepreneurship <br><br>
                    <i>Dikembangkan sebagai Proyek Aktualisasi Latsar CPNS Kabupaten Ngada Tahun 2026.</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("⚠️ Gagal Memuat Data. Silakan periksa koneksi internet atau Spreadsheet Anda.")
