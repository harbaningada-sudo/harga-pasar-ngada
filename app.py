import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM ---
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

# --- FUNGSI MUAT DATA (SANGAT AMAN) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h)
        # Pastikan kolom harga ada, jika tidak isi 0
        if 'HARGA HARI INI' in df_h.columns:
            df_h['HARGA HARI INI'] = pd.to_numeric(df_h['HARGA HARI INI'], errors='coerce').fillna(0)
        
        # Data Berita
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        # Paksa nama kolom agar tidak KeyError
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = df_b.dropna(subset=['Kegiatan'])
        df_b = df_b[df_b['Kegiatan'].astype(str).str.strip() != ""]
        
        return df_h, df_b.fillna("")
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"): 
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #059669;'>PEMKAB NGADA</h3>", unsafe_allow_html=True)
    st.divider()
    pilihan = st.radio("Pilih Menu:", ["🏠 Beranda", "📈 Tren Harga", "📰 Berita & Media", "📥 Unduh Data"])

# --- KONTEN ---
# 1. MENU BERANDA
if pilihan == "🏠 Beranda":
    st.markdown('<div class="hero-section"><h1>Dashboard Ekonomi Ngada 👋</h1><p>Informasi harga hari ini.</p></div>', unsafe_allow_html=True)
    if not df_harga.empty:
        for _, row in df_harga.iterrows():
            # Cek apakah kolom 'KOMODITAS' ada untuk mencegah ValueError
            nama = row.get('KOMODITAS', 'Komoditas')
            harga = row.get('HARGA HARI INI', 0)
            st.markdown(f'<div class="card-container card-harga"><b>{nama}</b><br>Rp {int(harga):,}</div>', unsafe_allow_html=True)
    else:
        st.warning("Data harga tidak ditemukan atau Google Sheets belum siap.")

# 2. MENU TREN
elif pilihan == "📈 Tren Harga":
    st.title("Grafik Tren Harga")
    if not df_harga.empty:
        fig = px.bar(df_harga, x='KOMODITAS', y='HARGA HARI INI', color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Grafik tidak dapat ditampilkan karena data kosong.")

# 3. MENU BERITA (ANTI GAMBAR NOL)
elif pilihan == "📰 Berita & Media":
    st.title("📰 Informasi & Media")
    if not df_berita.empty:
        for _, row in df_berita.iterrows():
            with st.container():
                st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                
                link = str(row['Link']).strip()
                tipe = str(row['Tipe']).lower()

                # Filter ketat: Hanya proses jika link beneran link (bukan '0', bukan nan)
                if link and link.startswith("http"):
                    if "drive.google.com" in link:
                        f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                        link = f"https://drive.google.com/uc?export=view&id={f_id}"
                    
                    if "foto" in tipe:
                        st.image(link, use_container_width=True)
                    elif "video" in tipe:
                        st.video(link)
                
                # Tanggal hanya muncul jika isinya bukan '0'
                tgl = str(row['Tanggal']).strip()
                if tgl and tgl != "0" and tgl != "nan":
                    st.caption(f"📅 Tanggal: {tgl}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Belum ada berita yang dipublikasikan.")

# 4. MENU UNDUH
elif pilihan == "📥 Unduh Data":
    st.title("Pusat Unduhan")
    if not df_harga.empty:
        st.download_button("Simpan Data (CSV)", df_harga.to_csv(index=False).encode('utf-8'), "data.csv", "text/csv")
