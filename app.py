import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN (TETAP SAMA) ---
st.set_page_config(
    page_title="Portal Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. SISTEM MEMORI (MEMPERTAHANKAN PENGATURAN) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_text": "Kabupaten Ngada memiliki potensi besar di sektor Kopi, Pariwisata, dan Pertanian.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. HELPER: MENGUBAH GAMBAR JADI BASE64 ---
# Fungsi ini wajib ada agar gambar bisa dijadikan background melalui CSS
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Ambil string base64 untuk foto pimpinan (pastikan nama filenya persis dengan di GitHub kamu)
img_pimpinan = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
logo_ngada = get_img_as_base64("logo-ngada.png") # Ambil juga logonya

# --- 4. CSS KUSTOM (KUNCI UTAMA TAMPILAN TERINTEGRASI) ---
# Di sinilah logika "Logo dengan Background Foto Pimpinan" dibuat
st.markdown(f"""
    <style>
    /* Menghilangkan Sidebar agar Fullscreen */
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    
    /* Background Web Hijau Muda Segar */
    .stApp {{ background-color: #F0FDF4 !important; }}
    
    /* Perbaikan Font */
    html, body, [class*="css"], .stMarkdown, p, span, div, label {{ 
        font-family: 'Inter', sans-serif; color: #1E293B !important; 
    }}

    /* CSS KOTAK LOGO DENGAN BACKGROUND FOTO */
    .header-pimpinan-logo-box {{
        width: 130px; 
        height: 130px; 
        background-image: url("data:image/jpeg;base64,{img_pimpinan if img_pimpinan else ''}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 2px solid white; /* Frame putih */
        margin-bottom: 20px;
        transition: 0.3s ease-in-out;
    }}
    .header-pimpinan-logo-box:hover {{
        transform: scale(1.05);
    }}

    /* CSS LOGO NGADA DI TENGAH FOTO */
    .logo-overlay {{
        width: 70px;
        z-index: 10;
        /* Menambahkan background putih tipis transparan di belakang logo 
           agar logo tetap terbaca meskipun background fotonya ramai */
        background: rgba(255, 255, 255, 0.85);
        padding: 5px;
        border-radius: 50%; /* Bulat */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Style Kartu Harga Rinci */
    .price-card-premium {{
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 8px solid #059669; /* Default Hijau */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .price-col {{ text-align: center; flex: 1; }}
    .status-naik {{ border-left-color: #DC2626 !important; }} /* Merah */
    .status-turun {{ border-left-color: #059669 !important; }} /* Hijau */
    .status-stabil {{ border-left-color: #D97706 !important; }} /* Kuning */
    </style>
    """, unsafe_allow_html=True)

# --- 5. MUAT DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        # Konversi angka (Handle error dan data kosong)
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
            
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 6. HEADER UTAMA (VISUAL TERINTEGRASI & 6 NAVIGASI) ---
with st.container():
    col_visual, col_title = st.columns([0.6, 4])
    
    with col_visual:
        # INI KUNCINYA: Menampilkan kotak pimpinan-logo terintegrasi
        if logo_ngada and img_pimpinan:
            st.markdown(f'''
                <div class="header-pimpinan-logo-box">
                    <img src="data:image/png;base64,{logo_ngada}" class="logo-overlay">
                </div>
            ''', unsafe_allow_html=True)
        elif logo_ngada: # Fallback jika foto pimpinan tidak ada
            st.image(f"data:image/png;base64,{logo_ngada}", width=100)
        else: # Fallback total
            st.markdown("<h3>🏛️</h3>", unsafe_allow_html=True)

    with col_title:
        st.markdown("<h2 style='margin:0; color:#15803D;'>🏛️ KABUPATEN NGADA</h2><p style='color:#059669; margin:0;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Baris Navigasi 6 Menu yang KOKOH (Sistem Top Nav)
        n1, n2, n3, n4, n5, n6 = st.columns(6)
        with n1: st.button("🏠 Beranda", use_container_width=True, on_click=navigasi, args=("Beranda",))
        with n2: st.button("🛍️ Harga", use_container_width=True, on_click=navigasi, args=("Harga",))
        with n3: st.button("📈 Tren", use_container_width=True, on_click=navigasi, args=("Tren",))
        with n4: st.button("ℹ️ Tentang", use_container_width=True, on_click=navigasi, args=("Tentang",))
        with n5: st.button("📥 Unduhan", use_container_width=True, on_click=navigasi, args=("Unduhan",))
        with n6: st.button("🏛️ Potensi", use_container_width=True, on_click=navigasi, args=("Potensi",))

        # Panel Admin Terpisah di Bawah Navigasi
        if is_admin:
            st.button("🛠️ PANEL KONTROL ADMIN", type="primary", use_container_width=True, on_click=navigasi, args=("Admin",))

st.divider()

# --- 7. LOGIKA HALAMAN ---

# Fungsi Helper untuk indikator status harga di Tabel Harga
def hitung_status_harga_rincian(ini, kmrn):
    selisih = ini - kmrn
    if selisih > 0: 
        return "Naik", f"<span style='color:#DC2626;'>▲ Rp {selisih:,}</span>", "status-naik"
    if selisih < 0: 
        return "Turun", f"<span style='color:#059669;'>▼ Rp {abs(selisih):,}</span>", "status-turun"
    return "Stabil", f"<span style='color:#D97706;'>— Rp 0</span>", "status-stabil"

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    # Hero section (Gaya Banner)
    st.markdown(f'''
        <div style="background:linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%); padding:20px; border-radius:15px; border:1px solid #DCFCE7; margin-bottom:20px;">
            <h2 style="margin:0; color:#15803D;">{store["hero_title"]}</h2>
            <p style="margin:0; color:#64748B;">{store["hero_subtitle"]}</p>
        </div>
    ''', unsafe_allow_html=True)
    
    col_operasi, col_informasi = st.columns([1.5, 1])
    with col_operasi:
        st.subheader("📢 Dokumentasi Kegiatan")
        # Menampilkan foto operasi pasar
        if os.path.exists("IMG_20251125_111048.jpg"):
            st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Operasi Pasar Setda Ngada")
    with col_informasi:
        st.subheader("📝 Visi & Misi")
        st.info(store["about_text"])

# B. HARGA KOMODITAS (RINCI BESAR VS KECIL)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas Rinci")
    
    search = st.text_input("🔍 Cari komoditas...", "")
    df_filtered = df_harga.copy()
    if search:
        df_filtered = df_filtered[df_filtered['KOMODITAS'].str.contains(search, case=False, na=False)]

    for _, row in df_filtered.iterrows():
        # Judul Grup/Kategori
        if row['SATUAN'] == 0:
            st.markdown(f"<div style='background:#059669; color:white; padding:8px 15px; border-radius:10px; margin-top:25px; font-weight:bold; font-size:1.1rem;'>📂 {row['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
        
        # Logika angka
        try:
            # Hitung Besar
            status_b, selisih_b_txt, css_b = hitung_status_harga_rincian(row['B_INI'], row['B_KMRN'])
            # Hitung Kecil
            status_k, selisih_k_txt, css_k = hitung_status_harga_rincian(row['K_INI'], row['K_KMRN'])
            
            # CSS Kartu menggunakan CSS status Pedagang Kecil (Paling krusial buat masyarakat)
            st.markdown(f'''
            <div class="price-card-premium {css_k}">
                <div style="flex: 1.5;">
                    <b style="font-size: 1.2rem;">{row['KOMODITAS']}</b><br>
                    <span style="color:#64748B;">Satuan: {row['SATUAN']}</span>
                </div>
                
                <div class="price-col">
                    <small style="color:#64748B; text-transform:uppercase;">Pedagang Besar</small><br>
                    <b style="font-size:1.3rem;">Rp {row['B_INI']:,}</b><br>
                    <small>Kemarin: Rp {row['B_KMRN']:,}</small><br>
                    <small>{selisih_b_txt}</small>
                </div>
                
                <div class="price-col" style="border-left: 2px solid #F1F5F9;">
                    <small style="color:#64748B; text-transform:uppercase;">Pedagang Kecil</small><br>
                    <b style="font-size:1.3rem; color:{'#DC2626' if row['K_INI']>row['K_KMRN'] else '#059669' if row['K_INI']<row['K_KMRN'] else '#1E293B'};">Rp {row['K_INI']:,}</b><br>
                    <small>Kemarin: Rp {row['K_KMRN']:,}</small><br>
                    <small>{selisih_k_txt}</small>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        except:
            continue

# C. TREN (Hanya tampil yang dipublikasikan Admin)
elif st.session_state.halaman_aktif == "Tren":
    st.subheader("📈 Tren Fluktuasi")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        # Logika status warna tren (opsional, bisa pakai bar map plotly)
        def get_status_trend(ini, kmrn):
            if ini > kmrn: return 'Naik'
            if ini < kmrn: return 'Turun'
            return 'Stabil'
        
        df_p['Status'] = df_p.apply(lambda x: get_status_trend(x['K_INI'], x['K_KMRN']), axis=1)
        
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status", 
                     color_discrete_map={'Naik': '#EF4444', 'Turun': '#10B981', 'Stabil': '#FBBF24'},
                     title="Trend Harga Pedagang Kecil")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pilih data tren yang ingin dipublikasikan di Panel Admin.")

# D. TENTANG KITA
elif st.session_state.halaman_aktif == "Tentang":
    st.header("ℹ️ Tentang Kami")
    st.write(store["about_text"])

# E. PUSAT UNDUHAN
elif st.session_state.halaman_aktif == "Unduhan":
    st.header("📥 Pusat Unduhan")
    st.download_button("Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_ngada.csv", "text/csv")

# F. POTENSI DAERAH
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Daerah")
    st.success(store["potensi_text"])

# G. ADMIN
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin Konten")
    t1, t2 = st.tabs(["Publikasi Tren", "Edit Teks Beranda & Potensi"])
    
    with t1:
        st.subheader("Pilih Komoditas untuk Tampil di Grafik Publik")
        store["tren_publikasi"] = st.multiselect("Pilih:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
        if st.button("Simpan Pengaturan Tren"):
            st.success("Tren diperbarui!")

    with t2:
        st.subheader("Ubah Tulisan di Halaman Utama")
        store["hero_title"] = st.text_input("Judul Banner:", store["hero_title"])
        store["hero_subtitle"] = st.text_input("Sub-judul Banner:", store["hero_subtitle"])
        store["about_text"] = st.text_area("Teks Profil (Visi Misi):", store["about_text"], height=200)
        store["potensi_text"] = st.text_area("Teks Potensi Daerah:", store["potensi_text"])
        
        if st.button("Simpan Semua Perubahan Teks"):
            st.success("Konten diperbarui!")
