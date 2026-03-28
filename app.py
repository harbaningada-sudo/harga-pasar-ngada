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

# --- 2. CSS KUSTOM (DESAIN MODERN & EMOSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    /* Header Hijau Pemkab */
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    
    /* Hero Banner Beranda */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 45px; border-radius: 20px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    /* Card Box Informasi */
    .card-container {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .card-container:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .card-harga { border-left: 8px solid #059669; }

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
    
    # Filter baris kosong agar tidak ada error tampilan
    df_b = df_b.dropna(subset=['Kegiatan'])
    df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
    
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_all_data()
    data_ok = True
except Exception as e:
    data_ok = False
    pesan_error = e

# --- 4. SIDEBAR NAVIGASI ---
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
                <h1 style='margin:0; color:white;'>Halo, Bapak Mama & Saudara Semua! 👋</h1>
                <p style='font-size:1.2rem; opacity:0.9;'>
                    Pemerintah hadir untuk memastikan dapur kita tetap mengepul. 
                    Pantau harga pangan hari ini agar belanja lebih tenang dan terencana.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        search = st.text_input("🔍 Cari bahan makanan hari ini (misal: Beras, Telur, Cabai)...", "")
        df_show = df_harga.copy()
        if search: 
            df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            selisih = int(row['SELISIH (Rp)'])
            warna = "#DC2626" if selisih > 0 else ("#059669" if selisih < 0 else "#64748B")
            simbol = "🔺" if selisih > 0 else ("🔹" if selisih < 0 else "➖")
            
            st.markdown(f"""
                <div class="card-container card-harga">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.15rem; font-weight: 700;">{row['KOMODITAS']}</span><br>
                            <span style="color: #64748B; font-size: 0.85rem;">Satuan: {row['SATUAN']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.5rem; font-weight: 800; color: #059669;">Rp {int(row['HARGA HARI INI']):,}.00</span><br>
                            <span style="color: {warna}; font-size: 0.95rem; font-weight: 600;">{simbol} Selisih: Rp {abs(selisih):,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # --- MENU 2: TREN HARGA ---
    elif pilihan == "📈 Tren & Analisis Harga":
        st.title("📈 Komparasi Harga Pangan")
        st.markdown("Bandingkan harga kemarin dan hari ini untuk merencanakan belanja Anda.")
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
        
        for _, row in df_berita.iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                
                tipe = str(row['Tipe']).lower()
                link = str(row['Link']).strip()

                if link and link != "0" and link != "0.0" and link.startswith("http"):
                    if "drive.google.com" in link:
                        f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                        link = f"https://drive.google.com/uc?export=view&id={f_id}"
                    
                    if "foto" in tipe:
                        st.image(link, use_container_width=True)
                    elif "video" in tipe:
                        st.video(link)
                    else:
                        st.info(f"🔗 [Klik untuk melihat dokumen lengkap]({link})")
                
                if row['Tanggal'] and str(row['Tanggal']) != "0":
                    st.caption(f"📅 Tanggal Publikasi: {row['Tanggal']}")
                st.markdown('</div>', unsafe_allow_html=True)

    # --- MENU 4: UNDUH DATA ---
    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Akses Data Terbuka")
        col1, col2 = st.columns(2)
        with col1:
            st.success("📊 Data Harga Komoditas")
            st.download_button("Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv", use_container_width=True)
        with col2:
            st.info("📰 Data Berita & Kegiatan")
            st.download_button("Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Berita_Ngada.csv", "text/csv", use_container_width=True)

    # --- MENU 5: INFORMASI LAYANAN ---
    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Dari Kami, Untuk Ngada")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Mengapa Aplikasi Ini Ada?</h3>
                <p style="font-size: 1.1rem; line-height: 1.6;">
                    Aplikasi ini adalah wujud kepedulian kami, <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, 
                    untuk melindungi hak Bapak dan Mama mendapatkan informasi harga yang jujur dan transparan.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.6;">
                    Melalui digitalisasi ini, kami ingin memastikan tidak ada lagi keraguan saat Bapak dan Mama 
                    melangkah ke pasar. Karena bagi kami, kesejahteraan keluarga di Ngada adalah prioritas utama.
                </p>
                <hr>
                <p style="font-size: 0.9rem; color: #64748B;">
                    <i>Dikembangkan dengan sepenuh hati sebagai Proyek Aktualisasi CPNS Kabupaten Ngada Tahun 2026.</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"⚠️ Gagal Memuat Data: {pesan_error}")
