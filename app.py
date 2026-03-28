import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="auto")

# --- CSS KUSTOM GABUNGAN (ATRAKTIF & RAPI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    /* Header Hijau & Tombol Menu Putih */
    header { background-color: #059669 !important; z-index: 99999 !important; } 
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }
    
    /* Desain Banner Depan */
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    /* Card Box untuk Berita & Harga */
    .card-container {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .card-harga { border-left: 8px solid #059669; }

    .block-container { padding-top: 5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI MEMUAT DATA HARGA ---
@st.cache_data(ttl=300)
def load_data_harga():
    # Gunakan link publik CSV dari Google Sheets Anda untuk data harga
    url_harga = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
    df = pd.read_csv(url_harga)
    df['HARGA KEMARIN'] = pd.to_numeric(df['HARGA KEMARIN'], errors='coerce').fillna(0)
    df['HARGA HARI INI'] = pd.to_numeric(df['HARGA HARI INI'], errors='coerce').fillna(0)
    df['SELISIH (Rp)'] = pd.to_numeric(df['SELISIH (Rp)'], errors='coerce').fillna(0)
    return df

# --- FUNGSI MEMUAT DATA BERITA ---
@st.cache_data(ttl=60)
def load_data_berita():
    # Gunakan link publik CSV dari Google Sheets Anda untuk data berita (tab Laporan Kegiatan)
    url_berita = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_berita, skiprows=2)
    # Penyesuaian Kolom Berdasarkan Excel Anda: No, Kegiatan, Tipe, Link, Tanggal
    df.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    # Membersihkan baris kosong agar ikon gambar pecah tidak muncul
    df = df.dropna(subset=['Kegiatan'])
    df = df[df['Kegiatan'].astype(str).str.strip() != ""]
    return df.fillna("")

# Muat Semua Data
try:
    df_harga = load_data_harga()
    df_berita = load_data_berita()
    data_tersedia = True
except Exception as e:
    data_tersedia = False
    pesan_error = e

# --- MENU NAVIGASI (SIDEBAR) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo_ngada.png"):
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #059669;'>PEMKAB NGADA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #64748B;'>Bagian Perekonomian & SDA</p>", unsafe_allow_html=True)
    st.divider()
    # MENGEMBALIKAN SEMUA OPSI MENU UTAMA
    pilihan = st.radio("Navigasi Menu:", [
        "🏠 Beranda (Harga Pangan)", 
        "📈 Tren & Analisis Harga", 
        "📰 Media & Berita Terkini", 
        "📥 Pusat Unduhan Data", 
        "ℹ️ Informasi Layanan"
    ])

# --- LOGIKA TAMPILAN KONTEN ---
if data_tersedia:
    
    # 1. MENU BERANDA (DASHBOARD HARGA ATRAKTIF)
    if pilihan == "🏠 Beranda (Harga Pangan)":
        st.markdown("""
            <div class="hero-section">
                <h1 style='margin:0; color:white;'>Dashboard Ekonomi Ngada 👋</h1>
                <p style='font-size:1.1rem; opacity:0.9;'>Informasi harga bahan pokok terkini di Kabupaten Ngada.</p>
            </div>
        """, unsafe_allow_html=True)
        
        search = st.text_input("🔍 Cari Komoditas (Contoh: Beras, Cabai, Telur)...", "")
        df_show = df_harga.copy()
        if search:
            df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False)]

        for _, row in df_show.iterrows():
            selisih = int(row['SELISIH (Rp)'])
            warna = "#DC2626" if selisih > 0 else ("#059669" if selisih < 0 else "#64748B")
            simbol = "🔺" if selisih > 0 else ("🔹" if selisih < 0 else "➖")
            
            st.markdown(f"""
                <div class="card-container card-harga">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.1rem; font-weight: 700;">{row['KOMODITAS']}</span><br>
                            <span style="color: #64748B; font-size: 0.8rem;">Satuan: {row['SATUAN']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.4rem; font-weight: 800; color: #059669;">Rp {int(row['HARGA HARI INI']):,}.00</span><br>
                            <span style="color: {warna}; font-size: 0.9rem; font-weight: 600;">{simbol} Selisih: Rp {abs(selisih):,}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # 2. MENU TREN & ANALISIS (GRAFIK)
    elif pilihan == "📈 Tren & Analisis Harga":
        st.title("📈 Komparasi & Analisis Harga")
        st.markdown("Pilih beberapa komoditas untuk melihat perbandingan harga Kemarin vs Hari Ini.")
        st.divider()
        list_k = df_harga['KOMODITAS'].unique().tolist()
        pick = st.multiselect("Pilih Komoditas untuk Grafik:", options=list_k, default=list_k[:5])
        
        if pick:
            df_p = df_harga[df_harga['KOMODITAS'].isin(pick)].melt(id_vars=['KOMODITAS'], value_vars=['HARGA KEMARIN', 'HARGA HARI INI'], var_name='Waktu', value_name='Harga')
            fig = px.bar(df_p, x='KOMODITAS', y='Harga', color='Waktu', barmode='group', text_auto='.2s', color_discrete_map={'HARGA KEMARIN': '#94A3B8', 'HARGA HARI INI': '#059669'})
            fig.update_layout(xaxis_title="Komoditas", yaxis_title="Harga (Rp)", legend_title="Waktu")
            st.plotly_chart(fig, use_container_width=True)

    # 3. MENU BERITA (OTOMATISASI MEDIA)
    elif pilihan == "📰 Media & Berita Terkini":
        st.title("📰 Media & Informasi Kegiatan Terkini")
        st.divider()
        
        if df_berita.empty:
            st.info("Belum ada berita atau informasi kegiatan terbaru.")
        else:
            for _, row in df_berita.iterrows():
                with st.container():
                    st.markdown(f'<div class="card-container"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                    
                    tipe = str(row['Tipe']).lower()
                    link = str(row['Link']).strip()

                    # HANYA TAMPILKAN MEDIA JIKA LINK VALID
                    if "http" in link and link != "0":
                        try:
                            # Konversi Link Drive Otomatis agar Muncul Gambar Langsung
                            if "drive.google.com" in link:
                                f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                                link = f"https://drive.google.com/uc?export=view&id={f_id}"

                            if "foto" in tipe:
                                st.image(link, use_container_width=True)
                            elif "video" in tipe:
                                st.video(link)
                            else:
                                st.info(f"🔗 [Lihat Dokumen Lengkap]({link})")
                        except Exception as e:
                            st.error("Gagal memuat media. Pastikan link benar dan akses publik aktif.")
                    
                    # Tampilkan Tanggal
                    if row['Tanggal'] and str(row['Tanggal']) != "0":
                        st.markdown(f'<p style="color: gray; font-size: 0.8rem; margin-top:10px;">📅 Tanggal: {row["Tanggal"]}</p>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

    # 4. MENU UNDUH DATA
    elif pilihan == "📥 Pusat Unduhan Data":
        st.title("📥 Unduh Rekapitulasi Data")
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.success("📊 Data Harga Komoditas")
            st.download_button("Unduh CSV Harga", df_harga.to_csv(index=False).encode('utf-8'), "Harga_Ngada.csv", "text/csv")
        with col2:
            st.info("📰 Data Berita & Kegiatan")
            st.download_button("Unduh CSV Berita", df_berita.to_csv(index=False).encode('utf-8'), "Berita_Ngada.csv", "text/csv")

    # 5. MENU INFORMASI LAYANAN
    elif pilihan == "ℹ️ Informasi Layanan":
        st.title("ℹ️ Tentang Aplikasi")
        st.divider()
        st.markdown("""
            <div class="card-container">
                <h3 style="color: #059669;">Tujuan Inovasi</h3>
                <p>Portal ini merupakan inovasi digital Bagian Perekonomian & SDA Kabupaten Ngada untuk mewujudkan keterbukaan informasi publik dan digitalisasi pelayanan.</p>
                <hr>
                <p><b>Bagian Perekonomian & Sumber Daya Alam</b><br>Pemerintah Kabupaten Ngada</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"⚠️ Koneksi Gagal: {pesan_error}")
