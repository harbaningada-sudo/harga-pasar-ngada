import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide")

# --- 2. CSS KUSTOM (MODERN & RAPI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; }
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white; margin-bottom: 20px;
    }
    .card-container {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .link-tombol {
        display: inline-block; padding: 8px 16px; background-color: #EEF2FF;
        color: #4F46E5 !important; border-radius: 8px; text-decoration: none;
        font-weight: 600; font-size: 0.9rem; border: 1px solid #C7D2FE;
    }
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MUAT DATA DENGAN PROTEKSI ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        
        # Data Berita
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = df_b.dropna(subset=['Kegiatan'])
        df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
        
        return df_h, df_b.fillna(""), True
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), False

df_harga, df_berita, data_ok = load_all_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"): st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Navigasi:", ["🏠 Dashboard Beranda", "📈 Tren Harga", "📰 Berita & Media", "📥 Unduh Data"])

# --- 5. TAMPILAN KONTEN ---
if data_ok:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown('<div class="hero-section"><h1>Halo, Bapak Mama & Saudara Semua! 👋</h1><p>Pantau harga pangan hari ini untuk belanja yang lebih terencana.</p></div>', unsafe_allow_html=True)
        
        # Proteksi jika kolom KOMODITAS tidak ditemukan
        if not df_harga.empty and 'KOMODITAS' in df_harga.columns:
            for _, row in df_harga.iterrows():
                st.markdown(f'<div class="card-container"><b>{row["KOMODITAS"]}</b><br><span style="color:#059669; font-size:1.2rem; font-weight:800;">Rp {row["HARGA HARI INI"]}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Data harga sedang diperbarui oleh petugas.")

    elif pilihan == "📈 Tren Harga":
        st.title("📈 Analisis Tren Harga")
        if not df_harga.empty and 'KOMODITAS' in df_harga.columns:
            fig = px.bar(df_harga, x='KOMODITAS', y='HARGA HARI INI', color_discrete_sequence=['#059669'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Grafik belum tersedia.")

    elif pilihan == "📰 Berita & Media":
        st.title("📰 Informasi & Dokumentasi")
        if not df_berita.empty:
            for _, row in df_berita.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                    link = str(row['Link']).strip()
                    if link.startswith("http"):
                        st.markdown(f'<a href="{link}" target="_blank" class="link-tombol">📂 Lihat Dokumentasi Lengkap</a>', unsafe_allow_html=True)
                    else:
                        st.caption("ℹ️ Dokumentasi sedang diproses")
                    st.markdown(f'<p style="color:gray; font-size:0.8rem; margin-top:10px;">📅 Tanggal: {row["Tanggal"]}</p></div>', unsafe_allow_html=True)
        else:
            st.info("Belum ada berita terbaru.")

    elif pilihan == "📥 Unduh Data":
        st.title("📥 Pusat Unduhan")
        if not df_harga.empty:
            st.download_button("Simpan Data Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

else:
    st.error("⚠️ Gagal terhubung ke Google Sheets. Pastikan link Google Sheets sudah 'Publik ke Web'.")
