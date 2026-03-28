import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM ATRAKTIF ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F0F4F8; }
    
    /* Header & Hero Banner */
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    /* Card Harga Atraktif */
    .card-harga {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #059669; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .card-harga:hover { transform: scale(1.02); }
    .harga-naik { color: #DC2626; font-weight: bold; }
    .harga-turun { color: #059669; font-weight: bold; }
    .harga-tetap { color: #64748B; font-weight: bold; }

    .block-container { padding-top: 5rem; }
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
    url_berita = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_berita, skiprows=2)
    df.columns = df.columns.str.strip()
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
    st.markdown("<h2 style='text-align: center; color: #059669;'>PEMKAB NGADA</h2>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Menu Layanan:", ["🏠 Beranda", "📈 Tren Harga", "📰 Berita & Pasar Murah", "📥 Unduh Data", "ℹ️ Tentang"])

# --- KONTEN ---
if data_tersedia:
    if pilihan == "🏠 Beranda":
        # Hero Banner
        st.markdown("""
            <div class="hero-section">
                <h1 style='margin:0; color:white;'>Halo, Masyarakat Ngada! 👋</h1>
                <p style='font-size:1.2rem; opacity:0.9;'>Pantau harga pangan hari ini dengan lebih mudah dan transparan.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🛒 Update Harga Bahan Pokok")
        
        # Filter Pencarian Ringan
        search = st.text_input("🔍 Cari bahan makanan (misal: Beras, Telur)...", "")
        df_show = df_harga.copy()
        if search:
            df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        # Tampilan Kartu Harga
        for _, row in df_show.iterrows():
            status_class = "harga-naik" if row['SELISIH (Rp)'] > 0 else ("harga-turun" if row['SELISIH (Rp)'] < 0 else "harga-tetap")
            simbol = "🔺" if row['SELISIH (Rp)'] > 0 else ("🔹" if row['SELISIH (Rp)'] < 0 else "➖")
            
            st.markdown(f"""
                <div class="card-harga">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.2rem; font-weight: 800; color: #1E293B;">{row['KOMODITAS']}</span><br>
                            <span style="color: #64748B; font-size: 0.9rem;">Satuan: {row['SATUAN']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.5rem; font-weight: 800; color: #059669;">Rp {int(row['HARGA HARI INI']):,}/ {row['SATUAN']}</span><br>
                            <span class="{status_class}">{simbol} Selisih: Rp {abs(int(row['SELISIH (Rp)'])):,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif pilihan == "📈 Tren Harga":
        st.title("📈 Analisis Tren Harga")
        list_k = df_harga['KOMODITAS'].unique().tolist()
        pick = st.multiselect("Pilih Bahan Pokok:", options=list_k, default=list_k[:3])
        if pick:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pick)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            st.plotly_chart(fig, use_container_width=True)

    elif pilihan == "📰 Berita & Pasar Murah":
        st.title("📰 Informasi Terkini")
        for _, row in df_berita.iterrows():
            judul = row.get('Kegiatan', 'Informasi Ekonomi')
            tipe = str(row.get('Tindak Lanjut', '')).lower()
            link = row.get('Unnamed: 3', '')
            
            with st.expander(f"📌 {judul}"):
                if 'foto' in tipe: st.image(link)
                elif 'video' in tipe: st.video(link)
                else: st.write(link)

    elif pilihan == "📥 Unduh Data":
        st.title("📥 Pusat Data")
        st.download_button("Unduh Rekap Harga (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")

    elif pilihan == "ℹ️ Tentang":
        st.title("ℹ️ Tentang Aplikasi")
        st.info("Portal ini adalah inovasi Bagian Perekonomian & SDA Kab. Ngada untuk digitalisasi pelayanan publik.")

else:
    st.error(f"Koneksi terputus: {pesan_error}")
