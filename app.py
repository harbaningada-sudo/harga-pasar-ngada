import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM GABUNGAN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .card-container {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-harga { border-left: 8px solid #059669; }
    .block-container { padding-top: 5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_data():
    # Data Harga
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    
    # Data Berita
    url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df_b = pd.read_csv(url_b, skiprows=2)
    df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    
    # Pembersihan: Hapus baris yang tidak ada nama kegiatannya
    df_b = df_b.dropna(subset=['Kegiatan'])
    df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
    
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_data()
    data_ok = True
except:
    data_ok = False

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"): st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #059669;'>PEMKAB NGADA</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Pilih Menu:", ["🏠 Beranda", "📈 Grafik Harga", "📰 Berita & Media", "📥 Unduh Data"])

# --- ISI KONTEN ---
if data_ok:
    if menu == "🏠 Beranda":
        st.markdown('<div class="hero-section"><h1>Dashboard Ekonomi Ngada</h1><p>Pantauan harga komoditas hari ini.</p></div>', unsafe_allow_html=True)
        for _, row in df_harga.iterrows():
            st.markdown(f'<div class="card-container card-harga"><b>{row["KOMODITAS"]}</b><br><span style="font-size:1.2rem; color:#059669;">Rp {int(row["HARGA HARI INI"]):,}</span></div>', unsafe_allow_html=True)

    elif menu == "📈 Grafik Harga":
        st.title("Tren Harga")
        fig = px.bar(df_harga, x="KOMODITAS", y="HARGA HARI INI", color="KOMODITAS", title="Harga Hari Ini")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "📰 Berita & Media":
        st.title("Informasi & Dokumentasi")
        for _, row in df_berita.iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                
                link = str(row['Link']).strip()
                tipe = str(row['Tipe']).lower()

                # LOGIKA PEMBERSIH: Hanya munculkan jika link BUKAN "0", BUKAN kosong, dan diawali "http"
                if link and link != "0" and link != "0.0" and link.startswith("http"):
                    if "drive.google.com" in link:
                        f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                        link = f"https://drive.google.com/uc?export=view&id={f_id}"
                    
                    if "foto" in tipe:
                        st.image(link, use_container_width=True)
                    elif "video" in tipe:
                        st.video(link)
                
                if row['Tanggal'] and str(row['Tanggal']) != "0":
                    st.caption(f"📅 Tanggal: {row['Tanggal']}")
                st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "📥 Unduh Data":
        st.title("Download Data")
        st.download_button("Simpan Data Harga (CSV)", df_harga.to_csv().encode('utf-8'), "data_harga.csv")

else:
    st.error("Gagal mengambil data dari Google Sheets.")
