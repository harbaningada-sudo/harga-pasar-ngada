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
    
    /* Header Hijau & Tombol Menu Putih */
    header { background-color: #059669 !important; border-bottom: none !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    
    /* Desain Tabel Laporan Formal */
    .tabel-laporan {
        width: 100%; border-collapse: collapse; font-size: 0.95rem;
        color: #0F172A; background-color: #FFFFFF; margin-top: 10px;
    }
    .tabel-laporan th { background-color: #059669; color: #FFFFFF; padding: 12px; text-align: left; border: 1px solid #CBD5E1; }
    .tabel-laporan td { padding: 12px; border: 1px solid #CBD5E1; vertical-align: top; }
    
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
def load_data_kegiatan():
    url_kegiatan = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_kegiatan, skiprows=2)
    if 'Unnamed: 3' in df.columns: df = df.rename(columns={'Unnamed: 3': 'Uraian Pelaksanaan'})
    if 'Kegiatan' in df.columns: df['Kegiatan'] = df['Kegiatan'].ffill() 
    if 'No' in df.columns: df['No'] = df['No'].ffill()
    return df.fillna("")

try:
    df_harga = load_data_harga()
    df_kegiatan = load_data_kegiatan()
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
    st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #64748B;'>Bagian Perekonomian & SDA</p>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Navigasi Menu:", ["📊 Dashboard Utama", "📈 Analisis Harga", "📋 Laporan Kinerja", "📥 Pusat Unduhan", "ℹ️ Informasi Layanan"])

# --- KONTEN ---
if data_tersedia:
    if pilihan == "📊 Dashboard Utama":
        st.title("📊 Pemantauan Harga Komoditas")
        st.divider()
        # Ringkasan Metrik
        df_highlight = df_harga.head(3)
        cols = st.columns(3)
        for i, col in enumerate(cols):
            item = df_highlight.iloc[i]
            col.metric(label=item['KOMODITAS'], value=f"Rp {int(item['HARGA HARI INI']):,}".replace(',', '.'), delta=f"Rp {int(item['SELISIH (Rp)'])}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_harga, use_container_width=True, hide_index=True)

    elif pilihan == "📈 Analisis Harga":
        st.title("📈 Komparasi Harga")
        st.divider()
        fig = px.bar(df_harga.head(10), x='KOMODITAS', y='HARGA HARI INI', color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📋 Laporan Kinerja":
        st.title("📋 Dokumentasi Tindak Lanjut")
        st.divider()
        df_tampil = df_kegiatan.copy()
        mask = df_tampil['No'].duplicated()
        df_tampil.loc[mask, 'No'] = ""
        df_tampil.loc[mask, 'Kegiatan'] = ""
        html_table = df_tampil.to_html(classes="tabel-laporan", index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Pusat Unduhan")
        st.markdown("Silakan unduh data laporan dalam format CSV di bawah ini:")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Harga")
            st.download_button("⬇️ Unduh CSV Harga", data=df_harga.to_csv(index=False).encode('utf-8'), file_name='Harga_Ngada.csv', mime='text/csv', use_container_width=True)
        with col2:
            st.subheader("Data Laporan")
            st.download_button("⬇️ Unduh CSV Laporan", data=df_kegiatan.to_csv(index=False).encode('utf-8'), file_name='Laporan_Kegiatan.csv', mime='text/csv', use_container_width=True)

    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Latar Belakang Pembuatan")
        st.divider()
        st.markdown("""
        <div style='background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0;'>
            <h3 style='color: #059669;'>Tujuan Aplikasi</h3>
            <p>Aplikasi Dashboard Ekonomi Ngada ini dibangun sebagai bagian dari <b>Proyek Aktualisasi CPNS</b> di Bagian Perekonomian dan SDA Kabupaten Ngada.</p>
            <p>Fokus utama aplikasi ini adalah untuk menyediakan data harga pasar yang transparan dan laporan kinerja yang akuntabel bagi pimpinan dan masyarakat.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error(f"Koneksi Gagal: {pesan_error}")
