import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide")

# --- CSS KUSTOM ---
st.markdown("""
    <style>
    .card-berita {
        background: white; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    header { background-color: #059669 !important; }
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60) # Cache dipercepat jadi 1 menit untuk testing
def load_data_berita():
    url_berita = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_berita, skiprows=2)
    df.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"] # Memaksa nama kolom agar sesuai gambar Excel Anda
    return df.fillna("")

# Muat Data
try:
    df_berita = load_data_berita()
    data_tersedia = True
except:
    data_tersedia = False

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_ngada.png"): st.image("logo_ngada.png", use_container_width=True)
    pilihan = st.radio("Menu:", ["🏠 Beranda", "📰 Berita & Pasar Murah"])

# --- KONTEN BERITA ---
if pilihan == "📰 Berita & Pasar Murah" and data_tersedia:
    st.title("📰 Berita & Media Terkini")
    
    for _, row in df_berita.iterrows():
        if not row['Kegiatan']: continue # Lewati baris kosong
        
        with st.container():
            st.markdown(f'<div class="card-berita"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
            
            tipe = str(row['Tipe']).lower()
            link = str(row['Link']).strip()

            if "http" in link:
                # JIKA LINK GOOGLE DRIVE: Ubah otomatis ke link gambar langsung
                if "drive.google.com" in link:
                    file_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                    link = f"https://drive.google.com/uc?export=view&id={file_id}"

                if "foto" in tipe:
                    st.image(link, caption=row['Kegiatan'], use_container_width=True)
                elif "video" in tipe:
                    st.video(link)
                else:
                    st.info(f"🔗 [Lihat Dokumen Lengkap]({link})")
            
            st.write(f"📅 *Tanggal: {row['Tanggal']}*")
            st.markdown('</div>', unsafe_allow_html=True)
