import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (ADMIN EDITABLE) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada dikenal dengan kopi arabika, cengkeh, dan pertanian sayur di daerah Bajawa.",
        "potensi_pariwisata": "Destinasi unggulan meliputi Kampung Adat Bena, Taman Laut 17 Pulau Riung, dan pemandian air panas.",
        "potensi_lainnya": "Sektor UMKM kerajinan tenun ikat dan bambu terus berkembang.",
        "tren_pilihan": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

# State Navigasi
if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. HELPER GAMBAR & CSS ---
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_pimpinan = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
img_logo = get_base64("logo_ngada.png")

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: #F8FAFC; }}
    .pimpinan-frame {{
        width: 120px; height: 120px; border-radius: 15px; border: 2px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 5px; right: 5px; width: 35px; height: 35px;
        background: white; border-radius: 5px; padding: 2px;
    }}
    .card {{ background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; border-left: 5px solid #059669; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA HARGA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url, skiprows=1).iloc[:, :6]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=['KOMODITAS'])
    except: return pd.DataFrame()

df = load_data()

# --- 5. HEADER & NAVIGASI UTAMA ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("## KABUPATEN NGADA\n**Bagian Perekonomian & SDA Setda Ngada**")

    # Menu Tombol
    m = st.columns(6)
    if m[0].button("🏠 Beranda", use_container_width=True): st.session_state.page = "Beranda"
    if m[1].button("🛍️ Harga", use_container_width=True): st.session_state.page = "Harga"
    if m[2].button("📈 Tren", use_container_width=True): st.session_state.page = "Tren"
    if m[3].button("ℹ️ Tentang", use_container_width=True): st.session_state.page = "Tentang"
    if m[4].button("📥 Unduhan", use_container_width=True): st.session_state.page = "Unduhan"
    if m[5].button("🏛️ Potensi", use_container_width=True): st.session_state.page = "Potensi"

st.divider()

# --- 6. LOGIKA HALAMAN ---

# A. BERANDA
if st.session_state.page == "Beranda":
    st.markdown(f"### {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

# B. HARGA
elif st.session_state.page == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas")
    for _, r in df.iterrows():
        if r['SATUAN'] == 0: st.markdown(f"#### 📂 {r['KOMODITAS']}"); continue
        diff = r['K_INI'] - r['K_KMRN']
        status = f"<span style='color:red'>▲ Rp {diff:,}</span>" if diff > 0 else (f"<span style='color:green'>▼ Rp {abs(diff):,}</span>" if diff < 0 else "— Stabil")
        st.markdown(f'''<div class="card"><b>{r['KOMODITAS']}</b> ({r['SATUAN']})<br>
                    Harga Hari Ini: <b>Rp {r['K_INI']:,}</b> | Perubahan: {status}</div>''', unsafe_allow_html=True)

# C. TREN
elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Tren Harga")
    pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df['KOMODITAS'].iloc[:5].tolist()
    df_plot = df[df['KOMODITAS'].isin(pilihan)]
    fig = px.bar(df_plot, x='KOMODITAS', y='K_INI', title="Harga Pedagang Kecil", color_discrete_sequence=['#059669'])
    st.plotly_chart(fig, use_container_width=True)

# D. POTENSI DAERAH (DIPISAH)
elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Unggulan Daerah")
    t1, t2, t3 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata", "✨ Lainnya"])
    with t1: st.write(store["potensi_pertanian"])
    with t2: st.write(store["potensi_pariwisata"])
    with t3: st.write(store["potensi_lainnya"])

# E. TENTANG & UNDUHAN
elif st.session_state.page == "Tentang":
    st.write(store["about_text"])
elif st.session_state.page == "Unduhan":
    st.download_button("Download Data Harga (CSV)", df.to_csv(index=False), "harga_ngada.csv")

# F. ADMIN PANEL (FULL EDIT)
if is_admin:
    st.sidebar.header("🛠️ PENGATURAN ADMIN")
    with st.sidebar.expander("📝 Edit Beranda"):
        store["hero_title"] = st.text_input("Judul Utama", store["hero_title"])
        store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
    with st.sidebar.expander("📈 Edit Tren"):
        store["tren_pilihan"] = st.multiselect("Pilih Komoditas Tren", df['KOMODITAS'].unique(), default=store["tren_pilihan"])
    with st.sidebar.expander("🏛️ Edit Potensi"):
        store["potensi_pertanian"] = st.text_area("Data Pertanian", store["potensi_pertanian"])
        store["potensi_pariwisata"] = st.text_area("Data Pariwisata", store["potensi_pariwisata"])
        store["potensi_lainnya"] = st.text_area("Potensi Lainnya", store["potensi_lainnya"])
    with st.sidebar.expander("ℹ️ Edit Tentang"):
        store["about_text"] = st.text_area("Teks Tentang Kami", store["about_text"])
    if st.sidebar.button("Simpan Semua Perubahan"):
        st.sidebar.success("Perubahan Berhasil Disimpan!")
