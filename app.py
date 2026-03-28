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

# --- 2. CSS KUSTOM (WARNA TEKS & INDIKATOR VISUAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        color: #1E293B !important; 
    }
    .stApp { background-color: #F8FAFC; }
    
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    
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
    
    /* Indikator Warna Samping */
    .border-naik { border-left: 8px solid #DC2626; }    /* Merah */
    .border-turun { border-left: 8px solid #059669; }   /* Hijau */
    .border-stabil { border-left: 8px solid #94A3B8; }  /* Abu-abu */

    .price-today { font-size: 1.4rem; font-weight: 800; color: #1E293B; }
    .price-yesterday { font-size: 0.85rem; color: #64748B; }
    
    .link-tombol {
        display: inline-block; padding: 10px 20px; background-color: #EEF2FF;
        color: #4F46E5 !important; border-radius: 10px; text-decoration: none;
        font-weight: 600; font-size: 0.9rem; border: 1px solid #C7D2FE;
    }

    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    # Load Data Harga
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    # Pastikan angka bersih dari teks
    df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
    df_h['HARGA KEMARIN'] = pd.to_numeric(df_h['HARGA KEMARIN'], errors='coerce').fillna(0)
    
    # Load Data Berita
    url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df_b = pd.read_csv(url_b, skiprows=2)
    df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    df_b = df_b.dropna(subset=['Kegiatan'])
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_all_data()
    data_ok = True
except:
    data_ok = False

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.divider()
    pilihan = st.radio("Pilih Menu:", ["🏠 Dashboard Beranda", "📈 Tren Harga", "📰 Berita & Media", "📥 Pusat Unduhan", "ℹ️ Informasi Layanan"])

# --- 5. LOGIKA TAMPILAN ---
if data_ok:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown("""
            <div class="hero-section">
                <h1>Halo, Bapak Mama & Saudara Semua! 👋</h1>
                <p>Membantu Bapak dan Mama merencanakan belanja keluarga dengan informasi harga pangan yang jujur dan transparan setiap hari.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Gambar Dokumentasi Proporsional
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                st.image(img_path, width=320, caption="📌 Dokumentasi Lapangan")
        with col_txt:
            st.info("""
                **Cara Membaca Indikator:**
                * 🔴 **Merah:** Harga naik dibanding kemarin.
                * 🟢 **Hijau:** Harga turun (Waktunya belanja!).
                * ⚪ **Abu-abu:** Harga stabil/tetap.
            """)

        st.divider()
        search = st.text_input("🔍 Cari komoditas hari ini...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            h_hari_ini = int(row['HARGA HARI INI'])
            h_kemarin = int(row['HARGA KEMARIN'])
            selisih = h_hari_ini - h_kemarin
            
            # Logika Warna & Ikon
            if selisih > 0:
                status_css = "border-naik"
                ikon = "🔺"
                warna_teks = "#DC2626"
                ket = f"Naik Rp {abs(selisih):,}"
            elif selisih < 0:
                status_css = "border-turun"
                ikon = "🔻"
                warna_teks = "#059669"
                ket = f"Turun Rp {abs(selisih):,}"
            else:
                status_css = "border-stabil"
                ikon = "➖"
                warna_teks = "#64748B"
                ket = "Stabil"

            st.markdown(f"""
                <div class="card-container {status_css}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b style="font-size: 1.1rem;">{row['KOMODITAS']}</b><br>
                            <small style="color: #64748B;">Satuan: {row['SATUAN']}</small>
                        </div>
                        <div style="text-align: right;">
                            <span class="price-today">Rp {h_hari_ini:,}</span><br>
                            <span style="color: {warna_teks}; font-weight: 600; font-size: 0.9rem;">{ikon} {ket}</span><br>
                            <span class="price-yesterday">Kemarin: Rp {h_kemarin:,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Dari Kami, Untuk Ngada")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Kesejahteraan Dimulai dari Keterbukaan</h3>
                <p>Kami memahami bahwa setiap rupiah sangat berarti bagi keluarga di Ngada. Portal ini hadir untuk menghilangkan keraguan Bapak Mama saat melangkah ke pasar.</p>
                <p><b>Bagian Perekonomian & SDA Kabupaten Ngada</b> berkomitmen mengawal stabilitas harga demi masyarakat yang lebih sejahtera.</p>
                <hr>
                <p style="font-size: 0.8rem; color: #94A3B8;">Aktualisasi CPNS Kabupaten Ngada Tahun 2026 - Smart ASN.</p>
            </div>
        """, unsafe_allow_html=True)

    # Menu lain tetap ada agar fungsi tidak hilang
    elif pilihan == "📈 Tren Harga":
        st.title("Grafik Tren")
        fig = px.bar(df_harga, x="KOMODITAS", y="HARGA HARI INI", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)
    elif pilihan == "📰 Berita & Media":
        st.title("Berita Terkini")
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>{row["Tanggal"]}</p></div>', unsafe_allow_html=True)
                if str(row['Link']).startswith("http"):
                    st.markdown(f'<a href="{row["Link"]}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi</a>', unsafe_allow_html=True)
    elif pilihan == "📥 Pusat Unduhan":
        st.title("Pusat Unduhan")
        st.download_button("Simpan Data (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

else:
    st.error("Gagal Memuat Data. Pastikan Spreadsheet dapat diakses publik.")
