import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE ---
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

# --- 3. CSS CUSTOM (TERMASUK OVERLAY LOGO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }
    .box-harga {
        flex: 1; min-width: 160px; padding: 12px; background: #f8fafc; border-radius: 10px; margin: 5px; border: 1px solid #e2e8f0;
    }
    .hero-container { position: relative; width: 100%; border-radius: 20px; overflow: hidden; }
    .floating-logo {
        position: absolute; top: 20px; left: 20px; width: 80px; z-index: 99;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5));
    }
    .media-container {
        background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px;
        border-top: 4px solid #0369a1; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_m = pd.DataFrame(), pd.DataFrame()
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])
        
        url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_m = pd.read_csv(url_m, skiprows=2)
        raw_m.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_m = raw_m.dropna(subset=['Kegiatan']).fillna("")
    except: pass
    return df_h, df_m

df_harga, df_media = load_all_data()

# --- 5. NAVIGASI ---
st.title("🏛️ Portal Ekonomi Ngada")
cols = st.columns(7)
menu = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, m in enumerate(menu):
    if cols[i].button(m, use_container_width=True): st.session_state.page = m
st.divider()

# --- 6. ADMIN PANEL ---
if is_admin:
    with st.sidebar:
        st.header("⚙️ Control Panel")
        with st.expander("🏠 Edit Beranda"):
            st.session_state.store["hero_title"] = st.text_input("Judul", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        with st.expander("🏛️ Edit Potensi"):
            st.session_state.store["potensi_pertanian"] = st.text_area("Teks Tani", st.session_state.store["potensi_pertanian"])
            st.session_state.store["potensi_pariwisata"] = st.text_area("Teks Wisata", st.session_state.store["potensi_pariwisata"])
        if st.button("💾 SIMPAN PERMANEN", use_container_width=True):
            save_settings(st.session_state.store)
            st.success("Tersimpan!")

# --- 7. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    
    foto_path = "IMG_20251125_111048.jpg"
    logo_path = "logo_ngada.png" # Ganti dengan nama file logo kamu di folder
    
    if os.path.exists(foto_path):
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f: logo_enc = base64.b64encode(f.read()).decode()
            with open(foto_path, "rb") as f: foto_enc = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div class="hero-container">
                    <img src="data:image/png;base64,{logo_enc}" class="floating-logo">
                    <img src="data:image/jpeg;base64,{foto_enc}" style="width:100%;">
                </div>
                """, unsafe_allow_html=True)
        else:
            st.image(foto_path, use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga")
    query = st.text_input("🔍 Cari Komoditas...").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            db = r['B_INI'] - r['B_KMRN']
            cb = "#EF4444" if db > 0 else "#10B981" if db < 0 else "#64748B"
            st.markdown(f"""
            <div class="price-card">
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1.5; min-width: 200px;">
                        <b>{r['KOMODITAS']}</b><br><small>Satuan: {r['SATUAN']}</small>
                    </div>
                    <div class="box-harga">
                        <small>PEDAGANG BESAR</small><br>
                        <b style="color:{cb}">Rp {r['B_INI']:,}</b><br>
                        <small style="text-decoration:line-through">Rp {r['B_KMRN']:,}</small>
                    </div>
                    <div class="box-harga">
                        <small>PEDAGANG KECIL</small><br>
                        <b>Rp {r['K_INI']:,}</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Media":
    st.markdown("### 📰 Berita Ekonomi")
    if not df_media.empty:
        for _, row in df_media.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="media-container">
                <small>📅 {row['Tanggal']} | 🏷️ {row['Tipe']}</small>
                <h4>{row['Kegiatan']}</h4>
            </div>
            """, unsafe_allow_html=True)
            if "http" in str(row['Link']): st.link_button("Baca Artikel", row['Link'])

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        st.write(store["potensi_pertanian"])
        if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg")
    with t2:
        st.write(store["potensi_pariwisata"])
        if os.path.exists("bena.webp"): st.image("bena.webp")

elif st.session_state.page == "Tren":
    st.subheader("📈 Tren Harga")
    if not df_harga.empty:
        fig = px.bar(df_harga.head(10), x='KOMODITAS', y='B_INI', color_discrete_sequence=['#0369a1'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Tentang":
    st.write(store["about_text"])
    st.write(f"📧 {store['kontak_email']} | 📍 {store['kontak_alamat']}")

elif st.session_state.page == "Unduh":
    st.download_button("Download CSV", df_harga.to_csv(), "harga.csv")
