import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_config(
    page_title="Portal Ekonomi Digital Ngada", 
    page_icon="🏛️", 
    layout="wide"
)

# --- 2. INISIALISASI MEMORI PILIHAN (SESSION STATE) ---
# Agar pilihan komoditas tidak hilang saat pindah menu
if 'pilihan_grafik' not in st.session_state:
    st.session_state['pilihan_grafik'] = []

# --- 3. CSS KUSTOM (UI RAMAH & PROFESIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B !important; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; } 
    
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white !important;
        margin-bottom: 25px;
    }
    .group-header {
        background: #F1F5F9; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; margin-bottom: 15px; font-weight: 800;
        border-left: 10px solid #059669;
    }
    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .price-main { font-size: 1.4rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        
        # Logika Kategori Otomatis
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

# --- 5. SIDEBAR ---
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

# --- 6. LOGIKA TAMPILAN ---
if not df_harga.empty:
    
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown("""
            <div class="hero-section">
                <h1>Smart Economy Ngada 👋</h1>
                <p>Membantu Bapak Mama memantau harga pasar secara transparan dan akuntabel setiap hari.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_foto, col_data = st.columns([1, 2])
        with col_foto:
            if os.path.exists("IMG_20251125_111048.jpg"):
                st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Pasar")
        
        with col_data:
            search = st.text_input("🔍 Cari komoditas...", "")
            df_show = df_harga.copy()
            if search:
                df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

            last_header = ""
            for _, row in df_show.iterrows():
                if row['KATEGORI_INDUK'] != last_header:
                    st.markdown(f'<div class="group-header">📂 {row["KATEGORI_INDUK"]}</div>', unsafe_allow_html=True)
                    last_header = row['KATEGORI_INDUK']
                if pd.isna(row['SATUAN']): continue

                h_ini = int(pd.to_numeric(row['HARGA HARI INI'], errors='coerce') or 0)
                h_kmrn = int(pd.to_numeric(row['HARGA KEMARIN'], errors='coerce') or 0)
                selisih = h_ini - h_kmrn
                warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#94A3B8"
                ikon = "🔺" if selisih > 0 else "🔻" if selisih < 0 else "➖"

                st.markdown(f"""
                    <div class="card-container" style="border-left: 10px solid {warna};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div><b>{row['KOMODITAS']}</b><br><small>{row['SATUAN']}</small></div>
                            <div style="text-align: right;">
                                <span class="price-main">Rp {h_ini:,}</span><br>
                                <span style="color: {warna}; font-weight: 700;">{ikon} Rp {abs(selisih):,}</span><br>
                                <small style="color: gray;">Kemarin: Rp {h_kmrn:,}</small>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    elif pilihan == "📈 Tren Harga Komoditas":
        st.title("📈 Analisis Perbandingan Harga")
        st.markdown("Silakan pilih komoditas yang ingin Bapak Mama bandingkan harganya.")
        
        # Filter data agar hanya mengambil baris yang punya satuan (barang asli)
        df_valid = df_harga.dropna(subset=['SATUAN'])
        list_pilihan = df_valid['KOMODITAS'].unique().tolist()
        
        # Perbaikan Error: Cek apakah pilihan di memori masih ada di daftar terbaru
        defaults = [x for x in st.session_state['pilihan_grafik'] if x in list_pilihan]
        
        # Input Pilihan User
        pilihan_user = st.multiselect(
            "Pilih komoditas (Bisa pilih lebih dari satu):", 
            options=list_pilihan, 
            default=defaults
        )
        
        # Simpan ke memori
        st.session_state['pilihan_grafik'] = pilihan_user
        
        if pilihan_user:
            # Siapkan data untuk grafik (Bandingkan Kemarin vs Hari Ini)
            df_plot = df_valid[df_valid['KOMODITAS'].isin(pilihan_user)].melt(
                id_vars=['KOMODITAS'], 
                value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], 
                var_name='Waktu', 
                value_name='Harga (Rp)'
            )
            
            fig = px.bar(
                df_plot, 
                x="KOMODITAS", 
                y="Harga (Rp)", 
                color="Waktu", 
                barmode="group",
                text_auto='.2s',
                color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'}
            )
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"Menampilkan tren untuk {len(pilihan_user)} komoditas terpilih.")
        else:
            st.info("💡 Tips: Klik kolom di atas dan pilih beberapa barang (misal: Beras dan Telur) untuk melihat perbandingan harganya secara visual.")

    elif pilihan == "📰 Media & Berita":
        st.title("📰 Dokumentasi Pelayanan")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>📅 {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
            if str(row['Link']).startswith("http"):
                st.markdown(f'<a href="{row["Link"]}" target="_blank" style="text-decoration:none; color:#4F46E5; font-weight:bold;">📂 Lihat Dokumentasi</a>', unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Transparansi Data")
        st.download_button("Unduh Data Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

    elif pilihan == "ℹ️ Komitmen Smart ASN":
        st.title("ℹ️ Melayani dengan Transparan")
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Dedikasi Untuk Masyarakat Ngada</h3>
                <p>Sebagai <b>Smart ASN</b>, kami menjunjung tinggi transparansi. Aplikasi ini memastikan setiap kenaikan atau penurunan harga komoditas tersampaikan secara jujur kepada Bapak Mama.</p>
                <hr>
                <small>Proyek Aktualisasi Latsar CPNS Ngada 2026</small>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("⚠️ Data tidak tersedia.")
