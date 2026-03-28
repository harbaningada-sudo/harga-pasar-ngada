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

# --- 2. CSS KUSTOM (SMART ASN DESIGN) ---
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
    .card-container {
        background: white !important; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .border-naik { border-left: 10px solid #DC2626 !important; }
    .border-turun { border-left: 10px solid #059669 !important; }
    .border-stabil { border-left: 10px solid #94A3B8 !important; }
    
    .price-main { font-size: 1.5rem; font-weight: 800; color: #1E293B !important; }
    .price-sub { font-size: 0.9rem; color: #64748B !important; }
    
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
        df_h['HARGA KEMARIN'] = pd.to_numeric(df_h['HARGA KEMARIN'], errors='coerce').fillna(0)
        
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h, df_b.dropna(subset=['Kegiatan']).fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 4. INISIALISASI SESSION STATE (FIX ERROR) ---
if 'pilihan_komoditas' not in st.session_state:
    if not df_harga.empty:
        st.session_state.pilihan_komoditas = df_harga['KOMODITAS'].unique().tolist()[:5]
    else:
        st.session_state.pilihan_komoditas = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.divider()
    pilihan = st.radio("Layanan Digital Ekonomi:", [
        "🏠 Dashboard Beranda", 
        "📈 Analisis Tren & Smart Data", 
        "📰 Media & Dokumentasi", 
        "📥 Pusat Unduhan", 
        "ℹ️ Visi & Informasi Layanan"
    ])

# --- 6. LOGIKA TAMPILAN ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        # NARASI SMART ASN - HALAMAN DEPAN
        st.markdown("""
            <div class="hero-section">
                <h1>Smart Economy Ngada 👋</h1>
                <p>Wujud nyata transformasi digital dalam mengawal stabilitas harga pangan. 
                Kami hadir memberikan kepastian data yang akurat, jujur, dan transparan untuk kesejahteraan Bapak Mama semua.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            if os.path.exists("IMG_20251125_111048.jpg"):
                st.image("IMG_20251125_111048.jpg", width=350, caption="Digitalisasi Pengawasan Pasar")
        with col_txt:
            st.success("**Smart Indikator:** Merah (Naik), Hijau (Turun), Abu (Stabil).")
            search = st.text_input("🔍 Cari komoditas hari ini...", "")

        st.divider()
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
                        <div style="text-align: right;"><span class="price-main">Rp {h_ini:,}</span><br>
                        <span style="color: {warna}; font-weight: 700; font-size: 0.9rem;">{ikon} {ket}</span><br>
                        <span class="price-sub">Kemarin: Rp {h_kmrn:,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif pilihan == "📈 Analisis Tren & Smart Data":
        st.title("📈 Smart Data Analytics")
        st.info("Pilihan komoditas Anda tetap tersimpan meskipun Anda berpindah menu.")
        list_k = df_harga['KOMODITAS'].unique().tolist()
        
        # FIX ERROR: Pastikan default value ada di dalam list options
        valid_defaults = [v for v in st.session_state.pilihan_komoditas if v in list_k]
        
        pilih_baru = st.multiselect(
            "Pilih Komoditas Pengawasan:", options=list_k, default=valid_defaults
        )
        st.session_state.pilihan_komoditas = pilih_baru
        
        if pilih_baru:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pilih_baru)].melt(
                id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], 
                var_name='Waktu', value_name='Harga'
            )
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group',
                         color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "ℹ️ Visi & Informasi Layanan":
        # NARASI SMART ASN - TENTANG KAMI
        st.title("ℹ️ Komitmen Smart ASN Kabupaten Ngada")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Menuju Birokrasi Berbasis Digital</h3>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Sebagai bagian dari <b>Bagian Perekonomian & SDA Kabupaten Ngada</b>, kami berkomitmen menjadi <b>Smart ASN</b> yang adaptif 
                    terhadap kemajuan teknologi informasi.
                </p>
                <p style="font-size: 1.1rem; line-height: 1.7;">
                    Portal ini bukan sekadar alat pantau, melainkan instrumen untuk menjaga <b>Integritas</b> data dan memberikan <b>Pelayanan Prima</b> 
                    bagi masyarakat. Setiap perubahan harga kami kawal secara profesional demi menjaga daya beli masyarakat Ngada.
                </p>
                <hr>
                <p style="font-size: 0.85rem; color: #64748B;">
                    <b>Visi Smart ASN:</b> Integritas | Profesional | IT Mastery | Hospitality | Networking <br>
                    <i>Proyek Aktualisasi Latsar CPNS Kabupaten Ngada - Tahun 2026</i>
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Menu Media & Unduh tetap ada...
    elif pilihan == "📰 Media & Dokumentasi":
        st.title("Dokumentasi Digital")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>{row["Tanggal"]}</p></div>', unsafe_allow_html=True)
    elif pilihan == "📥 Pusat Unduhan":
        st.title("Pusat Data")
        st.download_button("Simpan CSV", df_harga.to_csv(index=False).encode('utf-8'), "Data_Ekonomi_Ngada.csv", "text/csv")

else:
    st.error("⚠️ Koneksi Spreadsheet Terputus.")
