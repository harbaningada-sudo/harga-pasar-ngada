import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE (JSON) ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Riung.",
        "kontak_email": "ekonomi@ngadakab.go.id",
        "kontak_alamat": "Jl. Soekarno-Hatta No. 1, Bajawa",
        "tren_pilihan": [] 
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                saved = json.load(f)
                for k, v in default_data.items():
                    if k not in saved: saved[k] = v
                return saved
        except: return default_data
    return default_data

def save_settings(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if "store" not in st.session_state:
    st.session_state.store = load_settings()

is_admin = st.query_params.get("status") == "set"
if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. CSS CUSTOM (GAYA PROTOKOLER) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    
    /* Header Area */
    .header-container { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }
    .photo-frame {
        position: relative; width: 120px; height: 120px;
        border-radius: 15px; border: 3px solid #047857;
        overflow: hidden; background: white; flex-shrink: 0;
    }
    .photo-frame img.main-img { width: 100%; height: 100%; object-fit: cover; }
    .photo-frame img.overlay-logo {
        position: absolute; bottom: 5px; right: 5px; width: 35px;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));
    }
    .title-text h1 { margin: 0; font-size: 1.8rem; color: #1e293b; }
    .title-text p { margin: 0; color: #64748b; font-weight: bold; }

    /* Media & Card */
    .media-card {
        background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px;
        border-top: 4px solid #0369a1; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_m = pd.DataFrame(), pd.DataFrame()
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_m = pd.read_csv(url_m, skiprows=2)
        df_m.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    except: pass
    return df_h, df_m

df_harga, df_media = load_all_data()

# --- 5. HEADER (FOTO + LOGO) ---
def get_img_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_wabup = get_img_as_base64("IMG_20251125_111048.jpg")
img_logo = get_img_as_base64("logo_ngada.png")

st.markdown(f"""
    <div class="header-container">
        <div class="photo-frame">
            <img src="data:image/jpeg;base64,{img_wabup}" class="main-img">
            <img src="data:image/png;base64,{img_logo}" class="overlay-logo">
        </div>
        <div class="title-text">
            <h1>KABUPATEN NGADA</h1>
            <p>Bagian Perekonomian & SDA Setda</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. NAVIGASI ---
cols_nav = st.columns(7)
menu = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, m in enumerate(menu):
    if cols_nav[i].button(m, use_container_width=True):
        st.session_state.page = m
st.divider()

# --- 7. PANEL ADMIN ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Panel Editor Admin")
        with st.expander("🏠 Edit Beranda"):
            st.session_state.store["hero_title"] = st.text_input("Judul Utama", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        with st.expander("🏛️ Edit Potensi"):
            st.session_state.store["potensi_pertanian"] = st.text_area("Teks Pertanian", st.session_state.store["potensi_pertanian"])
            st.session_state.store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", st.session_state.store["potensi_pariwisata"])
        if st.button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
            save_settings(st.session_state.store)
            st.success("Data Berhasil Diperbarui!")

# --- 8. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.markdown(f'<div style="background:#e0f2fe; padding:20px; border-radius:10px; border-left:5px solid #0ea5e9;">{store["hero_subtitle"]}</div>', unsafe_allow_html=True)
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Wakil Bupati Ngada")

elif st.session_state.page == "Media":
    st.markdown("### 📰 Warta Ekonomi Ngada")
    if not df_media.empty:
        for _, row in df_media.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="media-card">
                <span style="color:#0369a1; font-weight:bold;">{row['Tipe']}</span> | <small>{row['Tanggal']}</small>
                <h4 style="margin: 10px 0;">{row['Kegiatan']}</h4>
                <a href="{row['Link']}" target="_blank" style="text-decoration:none; color:#0ea5e9; font-weight:bold;">🔗 Baca Selengkapnya</a>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Potensi":
    st.markdown("### 🏛️ Potensi Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        st.write(store["potensi_pertanian"])
        if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", use_container_width=True)
    with t2:
        st.write(store["potensi_pariwisata"])
        if os.path.exists("bena.webp"): st.image("bena.webp", use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Harga Komoditas")
    st.dataframe(df_harga, use_container_width=True)

elif st.session_state.page == "Tentang":
    st.markdown(f"### Profil")
    st.write(store["about_text"])
    st.info(f"📧 Email: {store['kontak_email']}\n\n📍 Alamat: {store['kontak_alamat']}")
