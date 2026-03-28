import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN (SMART ASN DESIGN) ---
st.set_page_config(
    page_title="Portal Ekonomi Digital Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="auto"
)

# --- 2. CSS KUSTOM (KUNCI WARNA TEKS HITAM & RESPONSIVE HUB) ---
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
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .hero-section h1, .hero-section p { color: white !important; }

    /* Gaya Card Harga */
    .card-container {
        background: white !important; 
        padding: 20px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-container h3, .card-container p, .card-container span, .card-container b {
        color: #1E293B !important;
    }
    .card-harga { border-left: 8px solid #059669; }

    /* Pengaturan Ukuran Teks untuk HP */
    @media (max-width: 640px) {
        .hero-section h1 { font-size: 1.4rem; }
        .hero-section p { font-size: 0.9rem; }
        .card-container span { font-size: 0.9rem !important; }
        .price-text { font-size: 1.2rem !important; }
    }

    /* Jarak Aman Atas */
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MUAT DATA (AKURASI DATA ADALAH PRIORITAS) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga Komoditas (Google Sheets)
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
        df_h['SELISIH (Rp)'] = pd.to_numeric(df_h['SELISIH (Rp)'], errors='coerce').fillna(0)
        
        # Data Berita & Dokumentasi (Google Sheets)
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        
        # Filter baris kosong agar tidak ada error tampilan
        df_b = df_b.dropna(subset=['Kegiatan'])
        df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
        
        return df_h, df_b.fillna("")
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 4. SIDEBAR NAVIGASI (SEMUA MENU KEMBALI) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669; margin-top: -10px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Pilih Layanan Ekonomi Digital:", [
        "🏠 Dashboard Beranda", 
        "📈 Tren Harga Komoditas", 
        "📰 Berita Digital", 
        "📥 Pusat Unduhan Data", 
        "ℹ️ Komitmen Smart ASN"
    ])

# --- 5. LOGIKA TAMPILAN KONTEN ---
if not df_harga.empty:
    # --- MENU 1: BERANDA (ORIENTASI PELAYANAN & TRANSPARANSI) ---
    if pilihan == "🏠 Dashboard Beranda":
        # Narasi Pelayanan Ramah di Banner
        st.markdown("""
            <div class="hero-section">
                <h1>Halo, Bapak Mama & Saudara Semua! 👋</h1>
                <p>Membantu Bapak Mama merencanakan belanja keluarga dengan informasi harga pangan yang jujur, cepat, dan transparan setiap hari. Inilah wujud pelayanan tulus kami untuk Ngada.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- TEKNIK COLUMNS: GABUNGKAN FOTO DAN HARGA ---
        col_foto, col_harga = st.columns([1, 1.8]) # Kolom kiri 1, kolom kanan 1.8 (lebih lebar)

        with col_foto:
            st.markdown("<h3 style='color: #059669;'>Dokumentasi Pasar</h3>", unsafe_allow_html=True)
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                # Tampilkan foto, fit penuh di kolomnya, ada caption
                st.image(img_path, use_container_width=True, caption="Kegiatan Pemantauan Harga oleh Tim Bagian Perekonomian & SDA")
            else:
                st.warning("⚠️ File gambar tidak ditemukan di repositori.")

        with col_harga:
            st.markdown("<h3 style='color: #059669;'>Daftar Harga Hari Ini</h3>", unsafe_allow_html=True)
            search = st.text_input("🔍 Cari komoditas hari ini (misal: Beras, Telur, Cabai)...", "")
            df_show = df_harga.copy()
            if search: 
                df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

            for _, row in df_show.iterrows():
                selisih = int(row['SELISIH (Rp)'])
                warna = "#DC2626" if selisih > 0 else ("#059669" if selisih < 0 else "#64748B")
                simbol = "🔺" if selisih > 0 else ("🔹" if selisih < 0 else "➖")
                
                # Kartu Harga Responsive
                st.markdown(f"""
                    <div class="card-container card-harga">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1rem; font-weight: 700;">{row['KOMODITAS']}</span><br>
                                <span style="color: #64748B; font-size: 0.8rem;">Satuan: {row['SATUAN']}</span>
                            </div>
                            <div style="text-align: right;">
                                <span class="price-text" style="font-size: 1.3rem; font-weight: 800; color: #059669;">Rp {int(row['HARGA HARI INI']):,}.00</span><br>
                                <span style="color: {warna}; font-size: 0.85rem; font-weight: 600;">{simbol} Selisih: Rp {abs(selisih):,}</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- MENU 2: TREN HARGA (SMART ASN - DATA Mastery) ---
    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Komparasi Harga Pangan Digital")
        df_chart = df_harga.dropna(subset=['SATUAN', 'HARGA HARI INI'])
        fig = px.bar(df_chart, x="KOMODITAS", y="HARGA HARI INI", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)

    # --- MENU 3: BERITA ---
    elif pilihan == "📰 Berita Digital":
        st.title("📰 Informasi & Dokumentasi Terkini")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p style="color: #64748B; font-size: 0.85rem;">📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
            if str(row['Link']).startswith("http"):
                st.markdown(f'<a href="{row["Link"]}" target="_blank" style="text-decoration:none; color:#4F46E5; font-weight:bold;">📂 Lihat Dokumentasi Lengkap</a>', unsafe_allow_html=True)

    # --- MENU 4: UNDUH DATA ---
    elif pilihan == "📥 Pusat Unduhan Data":
        st.title("📥 Akses Data Terbuka (Open Data)")
        st.download_button("Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

    # --- MENU 5: INFORMASI LAYANAN (VISI SMART ASN) ---
    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Birokrasi Digital & Berorientasi Pelayanan")
        # Narasi Komitmen Smart ASN di Visi
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Mengapa Kami Hadir Digital?</h3>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Sebagai bagian dari <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, kami berkomitmen menjadi <b>Smart ASN</b> yang adaptif dan menguasai teknologi untuk transparansi data publik.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Melalui digitalisasi ini, kami menghilangkan keraguan Bapak dan Mama saat melangkah ke pasar. Data yang jujur dan dapat dipertanggungjawabkan adalah hak Bapak Mama, dan kami hadir untuk memenuhinya dengan sepenuh hati.
                </p>
                <hr>
                <p style="font-size: 0.9rem; color: #64748B;">
                    <i>Visi Smart ASN: Integritas | Profesionalisme | IT Mastery | Hospitality | Networking</i><br>
                    <i>Proyek Aktualisasi CPNS Kabupaten Ngada Tahun 2026.</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("⚠️ Gagal memuat data. Periksa Spreadsheet Anda.")
