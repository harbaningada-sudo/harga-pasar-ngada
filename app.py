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

# --- 2. CSS KUSTOM (KUNCI TEKS HITAM & INDIKATOR VISUAL) ---
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

    /* Gaya Card Harga & Indikator Warna */
    .card-container {
        background: white !important; 
        padding: 25px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-container h3, .card-container p, .card-container span, .card-container b {
        color: #1E293B !important;
    }
    
    /* Garis Indikator Samping */
    .border-naik { border-left: 10px solid #DC2626 !important; }    /* Merah */
    .border-turun { border-left: 10px solid #059669 !important; }   /* Hijau */
    .border-stabil { border-left: 10px solid #94A3B8 !important; }  /* Abu-abu */

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
    # Data Harga Komoditas
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
    df_h['HARGA KEMARIN'] = pd.to_numeric(df_h['HARGA KEMARIN'], errors='coerce').fillna(0)
    
    # Data Berita & Dokumentasi
    url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df_b = pd.read_csv(url_b, skiprows=2)
    df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    df_b = df_b.dropna(subset=['Kegiatan'])
    df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
    
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_all_data()
    data_ok = True
except Exception as e:
    data_ok = False
    pesan_error = e

# --- 4. SIDEBAR NAVIGASI (SEMUA MENU KEMBALI LENGKAP) ---
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
        st.markdown("""
            <div class="hero-section">
                <h1>Halo, Bapak Mama & Saudara Semua! 👋</h1>
                <p>Membantu Bapak dan Mama merencanakan belanja keluarga dengan informasi harga pangan yang jujur dan transparan setiap hari.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Gambar Dokumentasi & Legenda Indikator
        col_img, col_leg = st.columns([1, 2])
        with col_img:
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                st.image(img_path, width=320, caption="📌 Dokumentasi Lapangan")
        with col_leg:
            st.info("""
                **Petunjuk Harga:**
                * 🔴 **Merah:** Harga naik dibanding kemarin.
                * 🟢 **Hijau:** Harga turun (Kabar baik!).
                * ⚪ **Abu-abu:** Harga stabil/tetap.
            """)

        st.divider()
        search = st.text_input("🔍 Cari komoditas hari ini...", "")
        df_show = df_harga.copy()
        if search: df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            h_ini = int(row['HARGA HARI INI'])
            h_kemarin = int(row['HARGA KEMARIN'])
            selisih = h_ini - h_kemarin
            
            # Logika Warna Indikator
            if selisih > 0:
                css_border, ikon, warna, ket = "border-naik", "🔺", "#DC2626", f"Naik Rp {abs(selisih):,}"
            elif selisih < 0:
                css_border, ikon, warna, ket = "border-turun", "🔻", "#059669", f"Turun Rp {abs(selisih):,}"
            else:
                css_border, ikon, warna, ket = "border-stabil", "➖", "#64748B", "Stabil"

            st.markdown(f"""
                <div class="card-container {css_border}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b style="font-size: 1.2rem;">{row['KOMODITAS']}</b><br>
                            <span style="color: #64748B; font-size: 0.85rem;">Satuan: {row['SATUAN']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span class="price-main">Rp {h_ini:,}</span><br>
                            <span style="color: {warna}; font-weight: 700; font-size: 0.95rem;">{ikon} {ket}</span><br>
                            <span class="price-sub">Harga Kemarin: Rp {h_kemarin:,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- MENU 2: TREN & ANALISIS ---
    elif pilihan == "📈 Tren & Analisis Harga":
        st.title("📈 Komparasi Harga Pangan")
        st.divider()
        list_k = df_harga['KOMODITAS'].unique().tolist()
        pick = st.multiselect("Pilih Komoditas:", options=list_k, default=list_k[:5])
        if pick:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pick)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    # --- MENU 3: BERITA & MEDIA ---
    elif pilihan == "📰 Berita & Media":
        st.title("📰 Informasi & Dokumentasi Terkini")
        st.divider()
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p style="color: #64748B; font-size: 0.85rem;">📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    st.markdown(f'<a href="{link}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi Lengkap</a>', unsafe_allow_html=True)
                st.markdown('<br>', unsafe_allow_html=True)

    # --- MENU 4: UNDUH DATA ---
    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Akses Data Terbuka")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📊 CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2:
            st.download_button("📰 CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Berita_Ngada.csv", "text/csv", use_container_width=True)

    # --- MENU 5: INFORMASI LAYANAN ---
    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Dari Kami, Untuk Ngada")
        st.markdown("""
            <div class="card-container">
                <h3>Kesejahteraan Dimulai dari Keterbukaan</h3>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Kami memahami bahwa setiap rupiah sangat berarti bagi keluarga di Ngada. Portal ini hadir untuk menghilangkan keraguan Bapak Mama saat melangkah ke pasar.
                </p>
                <p><b>Bagian Perekonomian & SDA Kabupaten Ngada</b> berkomitmen mengawal stabilitas harga demi masyarakat yang lebih sejahtera.</p>
                <hr>
                <p style="font-size: 0.8rem; color: #94A3B8;">Aktualisasi CPNS Kabupaten Ngada Tahun 2026 - Smart ASN.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"⚠️ Gagal Memuat Data: {pesan_error}")
