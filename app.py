import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    
    header { background-color: #059669 !important; border-bottom: none !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    
    .card-berita {
        background-color: white; padding: 20px; border-radius: 12px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .tag-jadwal { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    
    .block-container { padding-top: 4.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=600)
def load_data_harga():
    url_harga = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df = pd.read_csv(url_harga)
    df['HARGA KEMARIN'] = pd.to_numeric(df['HARGA KEMARIN'], errors='coerce').fillna(0)
    df['HARGA HARI INI'] = pd.to_numeric(df['HARGA HARI INI'], errors='coerce').fillna(0)
    df['SELISIH (Rp)'] = pd.to_numeric(df['SELISIH (Rp)'], errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=600)
def load_data_berita():
    # Menggunakan gid dari tab Laporan Kegiatan yang sudah ada (atau sesuaikan jika buat tab baru)
    url_berita = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_berita, skiprows=2)
    return df.fillna("")

try:
    df_harga = load_data_harga()
    df_berita = load_data_berita()
    data_tersedia = True
except Exception as e:
    data_tersedia = False
    pesan_error = e

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Navigasi Menu:", ["📊 Dashboard Utama", "📈 Analisis Harga", "📰 Berita & Pasar Murah", "📥 Pusat Unduhan", "ℹ️ Informasi Layanan"])

# --- KONTEN ---
if data_tersedia:
    if pilihan == "📊 Dashboard Utama":
        st.title("📊 Pemantauan Harga Komoditas")
        st.divider()
        df_highlight = df_harga.head(3)
        cols = st.columns(3)
        for i, col in enumerate(cols):
            item = df_highlight.iloc[i]
            col.metric(label=item['KOMODITAS'], value=f"Rp {int(item['HARGA HARI INI']):,}".replace(',', '.'), delta=f"Rp {int(item['SELISIH (Rp)'])}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_harga, use_container_width=True, hide_index=True)

    elif pilihan == "📈 Analisis Harga":
        st.title("📈 Komparasi Harga")
        list_komoditas = df_harga['KOMODITAS'].unique().tolist()
        pilihan_komoditas = st.multiselect("Pilih Komoditas:", options=list_komoditas, default=list_komoditas[:5])
        if pilihan_komoditas:
            df_filtered = df_harga[df_harga['KOMODITAS'].isin(pilihan_komoditas)]
            df_plot = df_filtered.melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Periode', value_name='Harga (Rp)')
            fig = px.bar(df_plot, x='KOMODITAS', y='Harga (Rp)', color='Periode', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📰 Berita & Pasar Murah":
        st.title("📰 Berita Terkini & Jadwal Pasar Murah")
        st.markdown("Informasi terbaru seputar perekonomian di Kabupaten Ngada.")
        st.divider()

        # Kita asumsikan kolom di Excel: Kegiatan (Judul), Tindak Lanjut (Tipe), Unnamed: 3 (Konten/Link)
        for index, row in df_berita.iterrows():
            with st.container():
                st.markdown(f"""<div class="card-berita">
                    <h3>{row['Kegiatan']}</h3>
                    <p style="color: gray; font-size: 0.8rem;">Update: {row['Keterangan']}</p>
                """, unsafe_allow_html=True)
                
                tipe = str(row['Tindak Lanjut']).lower()
                konten = row['Unnamed: 3']

                if 'foto' in tipe:
                    st.image(konten, use_container_width=True, caption=row['Kegiatan'])
                elif 'video' in tipe:
                    st.video(konten)
                elif 'jadwal' in tipe or 'pasar murah' in tipe:
                    st.markdown(f'<span class="tag-jadwal">📍 JADWAL PASAR MURAH</span>', unsafe_allow_html=True)
                    st.info(f"**Detail Pelaksanaan:**\n\n{konten}")
                
                st.markdown("</div>", unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Pusat Unduhan")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Harga")
            st.download_button("⬇️ Unduh CSV Harga", data=df_harga.to_csv(index=False).encode('utf-8'), file_name='Harga_Ngada.csv', mime='text/csv', use_container_width=True)

    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Latar Belakang")
        st.info("Aplikasi Dashboard Ekonomi Ngada dibangun sebagai bagian dari Proyek Aktualisasi CPNS.")

else:
    st.error(f"Koneksi Gagal: {pesan_error}")
