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

# --- 2. CSS KUSTOM (WARNA TEKS & TAMPILAN RESPONSIVE) ---
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
        margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .hero-section h1, .hero-section p { color: white !important; }

    .card-container {
        background: white !important; 
        padding: 20px; 
        border-radius: 15px;
        border: 1px solid #E2E8F0; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-harga { border-left: 8px solid #059669; }
    
    /* Tombol Dokumentasi */
    .link-tombol {
        display: inline-block; padding: 10px 20px; background-color: #EEF2FF;
        color: #4F46E5 !important; border-radius: 10px; text-decoration: none;
        font-weight: 600; font-size: 0.9rem; border: 1px solid #C7D2FE;
        margin-top: 10px;
    }

    @media (max-width: 640px) {
        .hero-section h1 { font-size: 1.4rem; }
    }

    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
    df_h['SELISIH (Rp)'] = pd.to_numeric(df_h['SELISIH (Rp)'], errors='coerce').fillna(0)
    
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
        # NARASI HALAMAN DEPAN
        st.markdown("""
            <div class="hero-section">
                <h1>Halo, Bapak Mama & Saudara Semua! 👋</h1>
                <p>Membantu Bapak dan Mama merencanakan belanja keluarga dengan informasi harga pangan yang jujur, cepat, dan transparan setiap hari.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # GAMBAR DIPERKECIL (Gunakan Columns agar tidak mengganggu harga)
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            img_path = "IMG_20251125_111048.jpg"
            if os.path.exists(img_path):
                st.image(img_path, width=350, caption="📌 Dokumentasi Lapangan")
        with col_txt:
            st.info("💡 **Tips Belanja:** Cek selisih harga hari ini. Jika ada kenaikan drastis, pertimbangkan untuk mencari alternatif komoditas lain.")

        st.divider()
        search = st.text_input("🔍 Cari komoditas hari ini...", "")
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
                            <span style="color: {warna}; font-size: 0.85rem; font-weight: 600;">{simbol} Rp {abs(selisih):,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif pilihan == "ℹ️ Informasi Layanan":
        # NARASI TENTANG KAMI
        st.title("ℹ️ Dari Kami, Untuk Ngada")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Mengapa Kami Membangun Portal Ini?</h3>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Bagi kami, <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, kesejahteraan Bapak dan Mama dimulai dari informasi yang terbuka. 
                    Kami memahami bahwa setiap rupiah sangat berarti bagi keluarga.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Portal ini hadir untuk menghilangkan keraguan saat melangkah ke pasar. Kami berkomitmen untuk terus mengawal 
                    stabilitas harga dan memastikan Bapak Mama mendapatkan informasi yang paling akurat langsung dari sumbernya.
                </p>
                <hr>
                <p style="font-size: 0.9rem; color: #64748B;">
                    <i>Karya ini dipersembahkan sebagai wujud nyata dedikasi Smart ASN dalam Proyek Aktualisasi CPNS Kabupaten Ngada Tahun 2026.</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

    # (Sisa menu Grafik, Berita, & Unduh tetap sama agar tidak hilang)
    elif pilihan == "📈 Tren Harga":
        st.title("Tren Harga")
        fig = px.bar(df_harga, x="KOMODITAS", y="HARGA HARI INI", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)
    elif pilihan == "📰 Berita & Media":
        st.title("Berita Terkini")
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    st.markdown(f'<a href="{link}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi</a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    elif pilihan == "📥 Pusat Unduhan":
        st.title("Pusat Unduhan")
        st.download_button("Simpan Data (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

else:
    st.error("Gagal Memuat Data.")
