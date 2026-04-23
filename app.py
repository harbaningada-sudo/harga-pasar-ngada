import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (BISA DIEDIT ADMIN) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "media_berita": [
            {"tgl": "2024-03-20", "judul": "Operasi Pasar Murah di Bajawa", "isi": "Pemerintah menjamin stok beras aman."},
            {"tgl": "2024-03-18", "judul": "Kunjungan Kerja Sektor Pertanian", "isi": "Peningkatan kapasitas petani kopi."}
        ],
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_tani": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Hortikultura.",
        "potensi_wisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "potensi_lain": "Sektor UMKM Tenun Ikat dan Bambu menjadi penggerak ekonomi kreatif.",
        "tren_pilihan": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. ASSET & CSS ---
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_pimpinan = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
img_logo = get_base64("logo_ngada.png")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAFC; }}
    .pimpinan-frame {{
        width: 130px; height: 130px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 8px; right: 8px; width: 38px; height: 38px;
        background: white; border-radius: 8px; padding: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .price-card {{
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #059669;
    }}
    .status-naik {{ color: #EF4444; font-weight: bold; }}
    .status-turun {{ color: #10B981; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA ---
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

df_harga = load_data()

# --- 5. HEADER & NAVIGASI (7 MENU) ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h1 style='margin-bottom:0;'>KABUPATEN NGADA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#059669; margin-top:0;'>Bagian Perekonomian & SDA Setda Ngada</h4>", unsafe_allow_html=True)

    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media & Berita", "Tentang", "Unduhan", "Potensi"]
    icons = ["🏠", "🛍️", "📈", "📰", "ℹ️", "📥", "🏛️"]
    for i, p in enumerate(pages):
        if m[i].button(f"{icons[i]} {p}", use_container_width=True):
            st.session_state.page = p

st.divider()

# --- 6. PANEL ADMIN ---
if is_admin:
    with st.sidebar:
        st.title("🛠️ Editor Konten")
        with st.expander("Edit Beranda"):
            store["hero_title"] = st.text_input("Judul", store["hero_title"])
            store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
        with st.expander("Edit Media & Berita"):
            st.write("Edit berita terakhir:")
            store["media_berita"][0]["judul"] = st.text_input("Judul Berita 1", store["media_berita"][0]["judul"])
            store["media_berita"][0]["isi"] = st.text_area("Isi Berita 1", store["media_berita"][0]["isi"])
        with st.expander("Edit Potensi"):
            store["potensi_tani"] = st.text_area("Pertanian", store["potensi_tani"])
            store["potensi_wisata"] = st.text_area("Pariwisata", store["potensi_wisata"])
            store["potensi_lain"] = st.text_area("Lainnya", store["potensi_lain"])
        st.success("Mode Admin Aktif!")

# --- 7. KONTEN ---
def get_status(ini, kmrn):
    s = ini - kmrn
    if s > 0: return f"<span class='status-naik'>▲ Rp {abs(s):,}</span>"
    if s < 0: return f"<span class='status-turun'>▼ Rp {abs(s):,}</span>"
    return "<span style='color:gray;'>— Stabil</span>"

if st.session_state.page == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.subheader("🛍️ Pantauan Harga Rinci")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0: st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f"""<div class="price-card"><div style="display:flex; justify-content:space-between;">
            <div style="flex:1.5;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
            <div style="flex:1; border-left:1px solid #eee; padding-left:15px;"><small>BESAR</small><br><b>Rp {r['B_INI']:,}</b><br>{get_status(r['B_INI'], r['B_KMRN'])}</div>
            <div style="flex:1; border-left:1px solid #eee; padding-left:15px;"><small>KECIL</small><br><b>Rp {r['K_INI']:,}</b><br>{get_status(r['K_INI'], r['K_KMRN'])}</div>
            </div></div>""", unsafe_allow_html=True)

elif st.session_state.page == "Media & Berita":
    st.subheader("📰 Media & Berita Terkini")
    for b in store["media_berita"]:
        with st.expander(f"{b['tgl']} - {b['judul']}"):
            st.write(b["isi"])

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Tren")
    pilih = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].iloc[:5].tolist()
    st.plotly_chart(px.bar(df_harga[df_harga['KOMODITAS'].isin(pilih)], x='KOMODITAS', y='K_INI', color_discrete_sequence=['#059669']), use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Daerah")
    t1, t2, t3 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata", "✨ Lainnya"])
    with t1: st.write(store["potensi_tani"])
    with t2: st.write(store["potensi_wisata"])
    with t3: st.write(store["potensi_lain"])

elif st.session_state.page == "Tentang": st.write(store["about_text"])
elif st.session_state.page == "Unduhan": st.download_button("📥 Download CSV", df_harga.to_csv(index=False), "harga.csv", use_container_width=True)
