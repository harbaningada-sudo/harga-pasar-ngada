import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="auto"
)

# --- 2. CSS KUSTOM (DESAIN MODERN & EMOSIONAL) ---
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
        padding: 45px; border-radius: 20px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    .card-container {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-harga { border-left: 8px solid #059669; }
    .block-container { padding-top: 5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI MEMUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    # Data Harga
    url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df_h = pd.read_csv(url_h)
    df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
    
    # Data Berita (Tab Laporan Kegiatan)
    url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    # Membaca data dengan melewati 2 baris header awal (Laporan Kegiatan & Bulan)
    df_b = pd.read_csv(url_b, skiprows=2) 
    df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    
    # Filter: Hanya ambil baris yang kolom Kegiatannya berisi teks
    df_b = df_b.dropna(subset=['Kegiatan'])
    df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
    
    return df_h, df_b.fillna("")

try:
    df_harga, df_berita = load_all_data()
    data_ok = True
except Exception as e:
    data_ok = False
    pesan_error = e

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669; margin-top: -10px;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Pilih Menu Layanan:", ["🏠 Dashboard Beranda", "📈 Tren & Analisis Harga", "📰 Berita & Media", "📥 Pusat Unduhan", "ℹ️ Informasi Layanan"])

# --- 5. LOGIKA TAMPILAN ---
if data_ok:
    if pilihan == "🏠 Dashboard Beranda":
        st.markdown('<div class="hero-section"><h1>Halo, Bapak Mama & Saudara Semua! 👋</h1><p>Pemerintah hadir untuk memastikan dapur kita tetap mengepul. Pantau harga pangan hari ini agar belanja lebih tenang.</p></div>', unsafe_allow_html=True)
        search = st.text_input("🔍 Cari bahan makanan...", "")
        df_show = df_harga[df_harga['KOMODITAS'].str.contains(search, case=False)] if search else df_harga
        for _, row in df_show.iterrows():
            st.markdown(f'<div class="card-container card-harga"><div style="display: flex; justify-content: space-between;"><div><b>{row["KOMODITAS"]}</b><br><small>Satuan: {row["SATUAN"]}</small></div><div style="text-align: right;"><b style="color: #059669; font-size: 1.3rem;">Rp {int(row["HARGA HARI INI"]):,}.00</b></div></div></div>', unsafe_allow_html=True)

    elif pilihan == "📈 Tren & Analisis Harga":
        st.title("📈 Komparasi Harga Pangan")
        list_k = df_harga['KOMODITAS'].unique().tolist()
        pick = st.multiselect("Pilih Komoditas:", options=list_k, default=list_k[:5])
        if pick:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pick)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📰 Berita & Media":
        st.title("📰 Informasi & Dokumentasi Terkini")
        st.divider()
        for _, row in df_berita.iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                
                tipe = str(row['Tipe']).lower()
                link = str(row['Link']).strip()

                # PENJAGA PINTU: Hanya proses jika link diawali http dan bukan teks '0'
                if link and link != "0" and link != "0.0" and link.startswith("http"):
                    # Konversi otomatis link Google Drive
                    if "drive.google.com" in link:
                        try:
                            f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                            # Menghapus parameter tambahan jika ada
                            if '?' in f_id: f_id = f_id.split('?')[0]
                            link = f"https://drive.google.com/uc?export=view&id={f_id}"
                        except:
                            pass

                    if "foto" in tipe:
                        st.image(link, use_container_width=True)
                    elif "video" in tipe:
                        st.video(link)
                
                # Tanggal hanya tampil jika bukan nol
                if str(row['Tanggal']) != "0" and str(row['Tanggal']) != "nan":
                    st.caption(f"📅 Tanggal: {row['Tanggal']}")
                st.markdown('</div>', unsafe_allow_html=True)

    elif pilihan == "📥 Pusat Unduhan":
        st.title("📥 Akses Data Terbuka")
        st.download_button("Unduh Data Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Dari Kami, Untuk Ngada")
        st.info("Aplikasi ini adalah wujud kepedulian Bagian Perekonomian & SDA Kabupaten Ngada untuk melindungi hak Bapak Mama mendapatkan informasi harga yang jujur.")

else:
    st.error(f"Gagal memuat data: {pesan_error}")
