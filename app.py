import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="auto" 
)

# --- CSS KUSTOM SUPER MODERN & RESPONSIVE ---
st.markdown("""
    <style>
    /* Import Font Modern (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Mengatur font seluruh halaman */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background utama aplikasi */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Modifikasi Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Desain Metrik / Kartu Sorotan untuk Desktop */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-top: 5px solid #059669; 
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-top: 5px solid #047857; 
    }
    
    /* Teks dalam Metrik Desktop */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    h1, h2, h3 { color: #0F172A; font-weight: 700; }
    
    /* PERBAIKAN HEADER: Warna putih solid agar tombol menu terlihat sangat jelas */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {
        background-color: #FFFFFF !important; 
        border-bottom: 1px solid #E2E8F0 !important;
    } 
    
    .block-container {
        padding-top: 4rem; /* Jarak atas ditambah agar konten tidak tertutup header putih */
        padding-bottom: 2rem;
    }

    /* =========================================
       MEDIA QUERIES (KHUSUS UNTUK TAMPILAN HP)
       ========================================= */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        div[data-testid="metric-container"] {
            padding: 15px 12px;
        }
        
        .block-container {
            padding-top: 3.5rem; 
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
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
        with col2:
            st.image("logo_ngada.png", use_container_width=True)
    else:
        st.warning("📌 Masukkan 'logo_ngada.png' ke folder proyek.")
        
    st.markdown("<h3 style='text-align: center; color: #059669; margin-bottom: 0px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; font-weight: 600; color: #64748B;'>Bagian Perekonomian & SDA</p>", unsafe_allow_html=True)
    st.divider()
    
    pilihan = st.radio("Navigasi Menu:", [
        "📊 Dashboard Utama", 
        "📈 Analisis Harga", 
        "📋 Laporan Kinerja",
        "📥 Pusat Unduhan",
        "ℹ️ Informasi Layanan"
    ])
    st.divider()
    st.markdown("<p style='text-align: center; font-size: 0.75rem; color: #94A3B8;'>© 2026 Pemerintah Kabupaten Ngada<br>Proyek Aktualisasi Publikasi Data</p>", unsafe_allow_html=True)

# --- KONTEN HALAMAN ---
if not data_tersedia:
    st.error(f"Gagal terhubung ke pangkalan data jaringan. Detail: {pesan_error}")
else:
    # --- HALAMAN 1: DASHBOARD UTAMA ---
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
                col.metric(
                    label=f"🛒 {item['KOMODITAS']} ({item['SATUAN']})", 
                    value=f"Rp {int(item['HARGA HARI INI']):,}".replace(',', '.'), 
                    delta=f"Rp {int(item['SELISIH (Rp)'])} ({item['STATUS']})", 
                    delta_color="inverse"
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("📋 Rekapitulasi Harga Lengkap")
        
        with st.container():
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                search_term = st.text_input("🔍 Pencarian:", placeholder="Ketik nama komoditas (misal: Beras, Cabai)")
            with col_filter:
                status_filter = st.selectbox("🚦 Status Harga:", ["Semua", "Naik", "Turun", "Stabil"])
                
        df_display = df_harga.copy()
        if search_term: df_display = df_display[df_display['KOMODITAS'].str.contains(search_term, case=False, na=False)]
        if status_filter != "Semua": df_display = df_display[df_display['STATUS'] == status_filter]

        st.dataframe(
            df_display, use_container_width=True, hide_index=True,
            column_config={
                "KOMODITAS": st.column_config.TextColumn("Nama Komoditas"),
                "SATUAN": st.column_config.TextColumn("Satuan"),
                "HARGA KEMARIN": st.column_config.NumberColumn("Harga Kemarin", format="Rp %d"),
                "HARGA HARI INI": st.column_config.NumberColumn("Harga Hari Ini", format="Rp %d"),
                "SELISIH (Rp)": st.column_config.NumberColumn("Selisih (Rp)", format="Rp %d"),
                "PERUBAHAN (%)": st.column_config.NumberColumn("Perubahan (%)"),
                "STATUS": st.column_config.TextColumn("Status")
            }
        )

    # --- HALAMAN 2: ANALISIS HARGA ---
    elif pilihan == "📈 Analisis Harga":
        st.title("📈 Komparasi & Tren Harga")
        st.markdown("<p style='color: #64748B; font-size: 1rem;'>Evaluasi visual pergerakan harga komoditas strategis hari ini vs kemarin.</p>", unsafe_allow_html=True)
        st.divider()
        
        komoditas_pilihan = st.multiselect(
            "Pilih komoditas yang ingin dikomparasi:",
            options=df_harga['KOMODITAS'].tolist(),
            default=df_harga['KOMODITAS'].tolist()[:5]
        )
        
        if komoditas_pilihan:
            df_filter = df_harga[df_harga['KOMODITAS'].isin(komoditas_pilihan)]
            df_melt = df_filter.melt(
                id_vars=['KOMODITAS'], 
                value_vars=['HARGA KEMARIN', 'HARGA HARI INI'],
                var_name='Periode', 
                value_name='Harga (Rp)'
            )
            
            fig = px.bar(
                df_melt, x='KOMODITAS', y='Harga (Rp)', color='Periode',
                barmode='group', text_auto='.2s', 
                color_discrete_sequence=['#94A3B8', '#059669'] 
            )
            
            fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            fig.update_layout(
                font_family="Inter",
                hovermode="x unified",
                xaxis_title="<b>Komoditas</b>",
                yaxis_title="<b>Nominal Harga (Rupiah)</b>",
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                legend_title="<b>Keterangan</b>",
                margin=dict(t=30, b=0, l=0, r=0) 
            )
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E2E8F0')
            
            st.plotly_chart(fig, use_container_width=True)
            
            komoditas_naik = df_filter[df_filter['STATUS'] == 'Naik']['KOMODITAS'].tolist()
            if komoditas_naik:
                st.warning(f"⚠️ **Atensi:** Terpantau kenaikan harga pada komoditas: **{', '.join(komoditas_naik)}**.")
            else:
                st.success("✅ Harga seluruh komoditas yang dipilih terpantau **stabil** atau **menurun**.")
        else:
            st.info("💡 Silakan pilih minimal satu komoditas pada kotak pencarian di atas untuk memunculkan grafik.")

    # --- HALAMAN 3: LAPORAN KINERJA ---
    elif pilihan == "📋 Laporan Kinerja":
        st.title("📋 Dokumentasi Tindak Lanjut")
        st.markdown("<p style='color: #64748B; font-size: 1rem;'>Transparansi pencapaian dan laporan strategis Bagian Perekonomian dan SDA.</p>", unsafe_allow_html=True)
        st.divider()
        st.dataframe(
            df_kegiatan, use_container_width=True, hide_index=True,
            column_config={
                "No": st.column_config.TextColumn("No.", width="small"),
                "Kegiatan": st.column_config.TextColumn("Agenda Kegiatan", width="medium"),
                "Tindak Lanjut": st.column_config.TextColumn("Tahapan", width="small"),
                "Unnamed: 3": st.column_config.TextColumn("Uraian Pelaksanaan", width="large"),
                "Keterangan": st.column_config.TextColumn("Status / Evaluasi", width="medium"),
            }, height=550
        )

    # --- HALAMAN 4: PUSAT UNDUHAN ---
    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Portal Unduhan Data Base")
        st.markdown("<p style='color: #64748B; font-size: 1rem;'>Akses rekapitulasi data asli dalam format CSV untuk keperluan pengarsipan atau pelaporan lanjutan.</p>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("📊 **Basis Data Harga Komoditas**")
            st.markdown("Dokumen pembaruan harga pasar hari ini berserta riwayat perbandingannya.")
            csv_harga = df_harga.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Unduh CSV Harga Pasar", data=csv_harga, file_name='Harga_Pasar_Ngada.csv', mime='text/csv', use_container_width=True)
        with col2:
            st.info("📋 **Basis Data Tindak Lanjut Kegiatan**")
            st.markdown("Dokumen rekapitulasi penertiban, pengurusan izin, dan kinerja lainnya.")
            csv_kegiatan = df_kegiatan.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Unduh CSV Laporan Kegiatan", data=csv_kegiatan, file_name='Kegiatan_Ekonomi_Ngada.csv', mime='text/csv', use_container_width=True)

    # --- HALAMAN 5: INFORMASI LAYANAN ---
    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Profil Layanan Publik")
        st.divider()
        st.markdown("""
        <div style="background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
            <h3 style="margin-top: 0; color: #0F172A; font-size: 1.3rem;">Bagian Perekonomian dan Sumber Daya Alam</h3>
            <p style="color: #059669; font-weight: 600; font-size: 1rem;">Pemerintah Kabupaten Ngada</p>
            <p style="color: #475569; line-height: 1.6; font-size: 0.95rem;">
                Sistem informasi ini dibangun sebagai bentuk wujud nyata <strong>inovasi digitalisasi pelayanan</strong> dan transparansi informasi publik. Kami berkomitmen untuk menyajikan data yang akurat guna mendukung kesejahteraan ekonomi masyarakat.
            </p>
            <hr style="border-top: 1px solid #E2E8F0; margin: 15px 0;">
            <h4 style="color: #0F172A; font-size: 1.1rem;">🎯 Tujuan Portal:</h4>
            <ul style="color: #475569; line-height: 1.6; font-size: 0.95rem;">
                <li>Menyajikan informasi pergerakan harga komoditas bahan pokok secara akurat dan mudah diakses masyarakat.</li>
                <li>Memfasilitasi pimpinan dalam merumuskan kebijakan terkait pengendalian inflasi daerah.</li>
                <li>Membuka akses dokumentasi progres kegiatan dan evaluasi kinerja instansi.</li>
            </ul>
            <hr style="border-top: 1px solid #E2E8F0; margin: 15px 0;">
            <h4 style="color: #0F172A; font-size: 1.1rem;">⏱️ Jadwal Sinkronisasi:</h4>
            <ul style="color: #475569; line-height: 1.6; font-size: 0.95rem;">
                <li><strong>Pemantauan Pasar:</strong> Pukul 06.00 - 10.00 WITA.</li>
                <li><strong>Pembaruan Sistem Harga:</strong> Diperbarui otomatis (Real-time) setiap hari kerja setelah data diunggah ke server.</li>
                <li><strong>Laporan Kinerja:</strong> Diperbarui secara berkala sesuai realisasi pelaksanaan program di lapangan.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
