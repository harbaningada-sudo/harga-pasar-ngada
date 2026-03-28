import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- 2. CSS KUSTOM (SMART ASN & CLEAN UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B !important; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    
    /* Hero Banner */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white !important;
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .hero-section h1, .hero-section p { color: white !important; }

    /* Gaya Card Kelompok/Judul (Tanpa Angka) */
    .group-header {
        background: #E2E8F0; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; margin-bottom: 15px; font-weight: 800;
        color: #1E293B; border-left: 10px solid #64748B;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* Gaya Card Harga */
    .card-container {
        background: white !important; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .border-naik { border-left: 10px solid #DC2626 !important; }
    .border-turun { border-left: 10px solid #059669 !important; }
    .border-stabil { border-left: 10px solid #94A3B8 !important; }
    
    .price-main { font-size: 1.5rem; font-weight: 800; color: #1E293B !important; }
    .price-sub { font-size: 0.9rem; color: #64748B !important; font-weight: 500; }
    
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        
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
    if os.path.exists("logo_ngada.png"): st.image("logo_ngada.png", use_container_width=True)
    st.divider()
    pilihan = st.radio("Menu Layanan:", ["🏠 Dashboard Beranda", "📈 Tren Harga", "📰 Berita Digital", "📥 Unduh Data", "ℹ️ Komitmen ASN"])

# --- 5. LOGIKA TAMPILAN ---
if not df_harga.empty:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown('<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Pantau harga pasar hari ini. Transparan, Akurat, dan Akuntabel.</p></div>', unsafe_allow_html=True)
        
        search = st.text_input("🔍 Cari komoditas (Smart Search)...", "")
        df_show = df_harga.copy()
        if search: 
            df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]

        for _, row in df_show.iterrows():
            # CEK APAKAH INI JUDUL KELOMPOK (NaN di Satuan/Harga)
            if pd.isna(row['SATUAN']) or pd.isna(row['HARGA HARI INI']):
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue

            # JIKA BUKAN JUDUL, TAMPILKAN SEBAGAI HARGA
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
            except:
                pass

    # (Sisa menu lainnya tetap sama agar fitur tidak hilang)
    elif pilihan == "📈 Tren Harga":
        st.title("Tren Harga")
        # Grafik hanya ambil yang ada angkanya
        df_chart = df_harga.dropna(subset=['SATUAN', 'HARGA HARI INI'])
        fig = px.bar(df_chart, x="KOMODITAS", y="HARGA HARI INI", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)
    
    elif pilihan == "📰 Berita Digital":
        st.title("Berita & Media")
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3><p>{row["Tanggal"]}</p></div>', unsafe_allow_html=True)
            if str(row['Link']).startswith("http"):
                st.markdown(f'<a href="{row["Link"]}" target="_blank" style="text-decoration:none; color:#4F46E5; font-weight:bold;">📂 Lihat Dokumentasi</a>', unsafe_allow_html=True)
                
    elif pilihan == "ℹ️ Komitmen ASN":
        st.title("Smart ASN")
        st.info("Aplikasi ini adalah wujud nyata transformasi digital Bagian Perekonomian & SDA Kabupaten Ngada untuk melayani masyarakat.")

else:
    st.error("⚠️ Gagal memuat data.")
