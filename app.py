import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. SISTEM MEMORI ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_text": "Kabupaten Ngada memiliki potensi unggulan di sektor Kopi, Pariwisata, dan Pertanian.",
        "tren_publikasi": [] 
    }

store = init_data()

# Cek parameter Admin
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target

# --- 3. HELPER GAMBAR (Didefinisikan di awal agar tidak NameError) ---
def get_img_as_base64(file):
    try:
        if os.path.exists(file):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        return ""
    return ""

# Ambil data gambar (Pastikan nama file di GitHub sama persis)
img_pimpinan_b64 = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
logo_ngada_b64 = get_img_as_base64("logo-ngada.png")

# --- 4. CSS CUSTOM (Tuntas & Rapih) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: #F8FAFC !important; }}
    
    /* Header Container */
    .header-pimpinan-box {{
        position: relative;
        width: 120px;
        height: 120px;
        background-image: url("data:image/jpeg;base64,{img_pimpinan_b64}");
        background-size: cover;
        background-position: center;
        border-radius: 15px;
        border: 2px solid #059669;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .logo-overlay {{
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        padding: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}

    /* Card Harga */
    .price-card {{
        background: white; border-radius: 12px; padding: 15px;
        border-left: 6px solid #059669; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .price-grid {{
        display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 10px;
    }}
    .status-naik {{ color: #DC2626; font-weight: bold; font-size: 0.85rem; }}
    .status-turun {{ color: #16A34A; font-weight: bold; font-size: 0.85rem; }}
    .status-stabil {{ color: #64748B; font-weight: bold; font-size: 0.85rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOAD DATA GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 6. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f"""
            <div class="header-pimpinan-box">
                <div class="logo-overlay">
                    <img src="data:image/png;base64,{logo_ngada_b64}" style="width:100%;">
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("## KABUPATEN NGADA")
        st.markdown("<p style='color:#059669; font-size:1.2rem; margin-top:-15px;'><b>Bagian Perekonomian & SDA Setda Ngada</b></p>", unsafe_allow_html=True)

    # 6 Tombol Navigasi
    n = st.columns(6)
    if n[0].button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if n[1].button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if n[2].button("📈 Tren", use_container_width=True): navigasi("Tren")
    if n[3].button("ℹ️ Tentang", use_container_width=True): navigasi("Tentang")
    if n[4].button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if n[5].button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
    
    if is_admin:
        st.button("🛠️ PANEL KONTROL ADMIN", type="primary", use_container_width=True, on_click=navigasi, args=("Admin",))

st.divider()

# --- 7. LOGIKA KONTEN ---

def get_trend_ui(ini, kmrn):
    selisih = ini - kmrn
    if selisih > 0: return f"<span class='status-naik'>▲ Rp {abs(selisih):,}</span>"
    if selisih < 0: return f"<span class='status-turun'>▼ Rp {abs(selisih):,}</span>"
    return "<span class='status-stabil'>— Stabil</span>"

# HALAMAN BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f"### {store['hero_title']}")
    st.write(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Kegiatan")
    st.info(store["about_text"])

# HALAMAN HARGA (Rinci & Clear)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas Rinci")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"#### 📂 {r['KOMODITAS']}")
            continue
        
        st.markdown(f"""
        <div class="price-card">
            <div class="price-grid">
                <div><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                <div>
                    <small>PEDAGANG BESAR</small><br>
                    <b>Rp {r['B_INI']:,}</b><br>
                    {get_trend_ui(r['B_INI'], r['B_KMRN'])}
                </div>
                <div>
                    <small>PEDAGANG KECIL</small><br>
                    <b>Rp {r['K_INI']:,}</b><br>
                    {get_trend_ui(r['K_INI'], r['K_KMRN'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# HALAMAN TREN
elif st.session_state.halaman_aktif == "Tren":
    st.subheader("📈 Tren Harga Pasar")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        df_p['Trend'] = df_p.apply(lambda x: 'Naik' if x['K_INI'] > x['K_KMRN'] else ('Turun' if x['K_INI'] < x['K_KMRN'] else 'Stabil'), axis=1)
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Trend",
                     color_discrete_map={'Naik': '#DC2626', 'Turun': '#16A34A', 'Stabil': '#64748B'},
                     title="Status Harga Pedagang Kecil")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada data tren yang dipilih oleh Admin.")

# HALAMAN TENTANG, UNDUHAN, POTENSI
elif st.session_state.halaman_aktif == "Tentang":
    st.write(store["about_text"])
elif st.session_state.halaman_aktif == "Unduhan":
    st.download_button("Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_ngada.csv")
elif st.session_state.halaman_aktif == "Potensi":
    st.success(store["potensi_text"])

# HALAMAN ADMIN
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    store["hero_title"] = st.text_input("Judul Banner", store["hero_title"])
    store["about_text"] = st.text_area("Teks Tentang Kita", store["about_text"])
    store["tren_publikasi"] = st.multiselect("Pilih Komoditas Tren", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    if st.button("Simpan Perubahan"):
        st.success("Berhasil disimpan!")
