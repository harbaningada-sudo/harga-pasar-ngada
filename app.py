import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM SUPER MODERN & RESPONSIVE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 24px 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 5px solid #059669; transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-5px); border-top: 5px solid #047857; }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 700 !important; color: #0F172A !important; }
    [data-testid="stMetricLabel"] { font-size: 1rem !important; font-weight: 600 !important; color: #64748B !important; }
    h1, h2, h3 { color: #0F172A; font-weight: 700; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    header { background-color: #059669 !important; border-bottom: none !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] {
        display: flex !important; align-items: center !important; justify-content: center !important;
        background-color: transparent !important; border: none !important; border-radius: 6px !important;
        padding: 4px !important; margin-left: 10px !important; margin-top: 10px !important; z-index: 999999 !important; color: #FFFFFF !important;
    }
    [data-testid="collapsedControl"] svg, [data-testid="collapsedControl"] path { fill: #FFFFFF !important; color: #FFFFFF !important; }
    
    .block-container { padding-top: 4.5rem; padding-bottom: 2rem; }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; } h2 { font-size: 1.3rem !important; } h3 { font-size: 1.1rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        div[data-testid="metric-container"] { padding: 15px 12px; }
        .block-container { padding-top: 4.5rem; padding-left: 1rem; padding-right: 1rem; }
    }
    
    /* CSS KHUSUS UNTUK TABEL LAPORAN KINERJA (FORMAL/CETAK) */
    .tabel-laporan {
        width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.95rem;
        color: #0F172A; background-color: #FFFFFF; margin-top: 10px;
    }
    .tabel-laporan th { background-color: #059669; color: #FFFFFF; padding: 12px 15px; text-align: left; border: 1px solid #CBD5E1; font-weight: 600; }
    .tabel-laporan td { padding: 12px 15px; border: 1px solid #CBD5E1; vertical-align: top; line-height: 1.5; }
    .tabel-laporan tr:hover { background-color: #F8FAFC; }
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
    df['KOMODITAS'] = df['KOMODITAS'].replace('eras Medium', 'Beras Medium')
    return df

@st.cache_data(ttl=600)
def load_data_kegiatan():
    url_kegiatan = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_kegiatan, skiprows=2)
    # Merapikan kolom "Unnamed: 3"
    if 'Unnamed: 3' in df.columns: df = df.rename(columns={'Unnamed: 3': 'Uraian Pelaksanaan'})
    if 'Tindak Lanjut' in df.columns: df = df.rename(columns={'Tindak Lanjut': 'Tahap'})
    # Mengisi baris yang kosong akibat Merge Cell di Excel
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

# --- MENU NAVIGASI (SIDEBAR) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2: st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669; margin-bottom: 0px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; font-weight: 600; color: #64748B;'>Bagian Perekonomian & SDA</p>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Navigasi Menu:", ["📊 Dashboard Utama", "📈 Analisis Harga", "📋 Laporan Kinerja", "📥 Pusat Unduhan", "ℹ️ Informasi Layanan"])
    st.divider()
    st.markdown("<p style='text-align: center; font-size: 0.75rem; color: #94A3B8;'>© 2026 Pemerintah Kabupaten Ngada<br>Proyek Aktualisasi</p>", unsafe_allow_html=True)

# --- KONTEN HALAMAN ---
if not data_tersedia:
    st.error(f"Gagal terhubung ke pangkalan data jaringan. Detail: {pesan_error}")
else:
    if pilihan == "📊 Dashboard Utama":
        st.title("📊 Pemantauan Harga Komoditas")
        st.markdown("<p style='color: #64748B; font-size: 1rem;'>Publikasi pergerakan harga bahan pokok secara aktual di wilayah Kabupaten Ngada.</p>", unsafe_allow_html=True)
        st.divider()
        st.subheader("📌 Sorotan Pergerakan Hari Ini")
        df_berubah = df_harga[df_harga['SELISIH (Rp)'] != 0]
        df_highlight = df_berubah.head(3) if len(df_berubah) > 0 else df_harga.head(3)
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if i < len(df_highlight):
                item = df_highlight.iloc[i]
                col.metric(label=f"🛒 {item['KOMODITAS']} ({item['SATUAN']})", value=f"Rp {int(item['HARGA HARI INI']):,}".replace(',', '.'), delta=f"Rp {int(item['SELISIH (Rp)'])} ({item['STATUS']})", delta_color="inverse")
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Rekapitulasi Harga Lengkap")
        with st.container():
            col_search, col_filter = st.columns([2, 1])
            with col_search: search_term = st.text_input("🔍 Pencarian:", placeholder="Ketik nama komoditas (misal: Beras)")
            with col_filter: status_filter = st.selectbox("🚦 Status Harga:", ["Semua", "Naik", "Turun", "Stabil"])
        df_display = df_harga.copy()
        if search_term: df_display = df_display[df_display['KOMODITAS'].str.contains(search_term, case=False, na=False)]
        if status_filter != "Semua": df_display = df_display[df_display['STATUS'] == status_filter]
        st.dataframe(df_display, use_container_width=True, hide_index=True, column_config={"KOMODITAS": st.column_config.TextColumn("Nama Komoditas"),"SATUAN": st.column_config.TextColumn("Satuan"),"HARGA KEMARIN": st.column_config.NumberColumn("Harga Kemarin", format="Rp %d"),"HARGA HARI INI": st.column_config.NumberColumn("Harga Hari Ini", format="Rp %d"),"SELISIH (Rp)": st.column_config.NumberColumn("Selisih (Rp)", format="Rp %d"),"PERUBAHAN (%)": st.column_config.NumberColumn("Perubahan (%)"),"STATUS": st.column_config.TextColumn("Status")})
    
    elif pilihan == "📈 Analisis Harga":
        st.title("📈 Komparasi & Tren Harga")
        st.divider()
        komoditas_pilihan = st.multiselect("Pilih komoditas:", options=df_harga['KOMODITAS'].tolist(), default=df_harga['KOMODITAS'].tolist()[:5])
        if komoditas_pilihan:
            df_filter = df_harga[df_harga['KOMODITAS'].isin(komoditas_pilihan)]
            df_melt = df_filter.melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Periode', value_name='Harga (Rp)')
            fig = px.bar(df_melt, x='KOMODITAS', y='Harga (Rp)', color='Periode', barmode='group', text_auto='.2s', color_discrete_sequence=['#94A3B8', '#059669'])
            fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig.update_layout(font_family="Inter", hovermode="x unified", xaxis_title="<b>Komoditas</b>", yaxis_title="<b>Nominal Harga (Rupiah)</b>", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend_title="<b>Keterangan</b>", margin=dict(t=30, b=0, l=0, r=0))
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Pilih minimal satu komoditas.")

    elif pilihan == "📋 Laporan Kinerja":
        st.title("📋 Dokumentasi Tindak Lanjut")
        st.markdown("<p style='color: #64748B; font-size: 1rem;'>Transparansi pencapaian dan laporan strategis Bagian Perekonomian dan SDA.</p>", unsafe_allow_html=True)
        st.divider()
        
        # 1. Menyiapkan data agar persis seperti template
        df_tampil = df_kegiatan.copy()
        
        # 2. Membuat efek "Merge Cell" (menghapus teks berulang ke bawah)
        if 'No' in df_tampil.columns and 'Kegiatan' in df_tampil.columns:
            mask = df_tampil['No'].duplicated()
            df_tampil.loc[mask, 'No'] = ""
            df_tampil.loc[mask, 'Kegiatan'] = ""

        # 3. Menampilkan tabel menggunakan HTML kustom
        html_table = df_tampil.to_html(classes="tabel-laporan", index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Portal Unduhan Data Base")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.success("📊 **Basis Data Harga Komoditas**")
            st.download_button("⬇️ Unduh CSV Harga Pasar", data=df_harga.to_csv(index=False).encode('utf-8'), file_name='Harga_Pasar_Ngada.csv', mime='text/csv', use_container_width=True)
        with col2:
            st.info("📋 **Basis Data Tindak Lanjut Kegiatan**")
            st.download_button("⬇️ Unduh CSV Laporan", data=df_kegiatan.to_csv(index=False).encode('utf-8'), file_name='Kegiatan_Ekonomi_Ngada.csv', mime='text/csv', use_container_width=True)

    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Profil Layanan Publik")
        st.divider()
        st.markdown("<div style='background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'><h3 style='margin-top: 0; color: #0F172A; font-size: 1.3rem;'>Bagian Perekonomian dan Sumber Daya Alam</h3><p style='color: #059669; font-weight: 600; font-size: 1rem;'>Pemerintah Kabupaten Ngada</p><p style='color: #475569; line-height: 1.6; font-size: 0.95rem;'>Sistem informasi ini dibangun sebagai bentuk wujud nyata <strong>inovasi digitalisasi pelayanan</strong> dan transparansi informasi publik. Kami berkomitmen untuk menyajikan data yang akurat guna mendukung kesejahteraan ekonomi masyarakat.</p></div>", unsafe_allow_html=True)
