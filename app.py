import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM MODERN & RESPONSIVE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    header { background-color: #059669 !important; border-bottom: none !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; fill: #FFFFFF !important; }
    
    /* Desain Tabel Laporan */
    .tabel-laporan {
        width: 100%; border-collapse: collapse; font-size: 0.95rem;
        color: #0F172A; background-color: #FFFFFF;
    }
    .tabel-laporan th { background-color: #059669; color: #FFFFFF; padding: 12px; border: 1px solid #CBD5E1; }
    .tabel-laporan td { padding: 10px; border: 1px solid #CBD5E1; vertical-align: top; }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #059669;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI MEMUAT DATA HARGA ---
@st.cache_data(ttl=300)
def load_data_harga():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df = pd.read_csv(url)
    # Bersihkan angka
    for col in ['HARGA KEMARIN', 'HARGA HARI INI', 'SELISIH (Rp)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# --- FUNGSI MEMUAT DATA KEGIATAN (DIPERBAIKI) ---
@st.cache_data(ttl=300)
def load_data_kegiatan():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    # Tarik data asli tanpa skip dulu untuk cek kolom
    df = pd.read_csv(url, skiprows=2)
    
    # Deteksi kolom secara otomatis berdasarkan urutan (agar tidak error jika nama berubah)
    # Biasanya: 0=No, 1=Kegiatan, 2=Tahap, 3=Uraian, 4=Keterangan
    if len(df.columns) >= 5:
        df.columns = ['No', 'Kegiatan', 'Tahap', 'Uraian Pelaksanaan', 'Keterangan']
    
    # Efek Merge Cell: Isi baris kosong di bawah 'No' dan 'Kegiatan'
    df['No'] = df['No'].ffill()
    df['Kegiatan'] = df['Kegiatan'].ffill()
    
    return df.fillna("")

# Muat data
try:
    df_harga = load_data_harga()
    df_kegiatan = load_data_kegiatan()
    data_ok = True
except Exception as e:
    st.error(f"Koneksi Data Terputus: {e}")
    data_ok = False

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", width=100)
    st.title("PEMKAB NGADA")
    st.write("Bagian Perekonomian & SDA")
    st.divider()
    pilihan = st.radio("Navigasi:", ["📊 Dashboard", "📈 Analisis", "📋 Laporan Kinerja"])

# --- KONTEN ---
if data_ok:
    if pilihan == "📊 Dashboard":
        st.title("📊 Dashboard Harga")
        # Menampilkan 3 kartu teratas
        c1, c2, c3 = st.columns(3)
        for i, col in enumerate([c1, c2, c3]):
            if i < len(df_harga):
                row = df_harga.iloc[i]
                col.metric(f"{row['KOMODITAS']}", f"Rp {int(row['HARGA HARI INI']):,}", f"{row['STATUS']}")
        st.divider()
        st.dataframe(df_harga, use_container_width=True, hide_index=True)

    elif pilihan == "📈 Analisis":
        st.title("📈 Tren Harga")
        komo = st.multiselect("Pilih Barang:", df_harga['KOMODITAS'].unique(), default=df_harga['KOMODITAS'].unique()[:3])
        df_f = df_harga[df_harga['KOMODITAS'].isin(komo)]
        fig = px.bar(df_f, x='KOMODITAS', y=['HARGA KEMARIN', 'HARGA HARI INI'], barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📋 Laporan Kinerja":
        st.title("📋 Laporan Kegiatan")
        
        # Proses "Merge Cell" visual (hapus teks duplikat agar rapi)
        df_view = df_kegiatan.copy()
        mask = df_view['No'].duplicated()
        df_view.loc[mask, ['No', 'Kegiatan']] = ""
        
        # Tampilkan tabel HTML
        st.markdown(df_view.to_html(classes="tabel-laporan", index=False), unsafe_allow_html=True)
