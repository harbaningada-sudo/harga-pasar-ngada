import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM PENYIMPANAN ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Riung.",
        "tren_pilihan": [] 
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return default_data
    return default_data

def save_settings(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if "store" not in st.session_state:
    st.session_state.store = load_settings()

is_admin = st.query_params.get("status") == "set"
if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. CSS CUSTOM ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E0F2FE !important; }}
    .price-card {{
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }}
    .status-badge {{
        padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; display: inline-block;
    }}
    .box-harga {{
        flex: 1; min-width: 140px; padding: 10px; background: #f8fafc; border-radius: 10px; margin: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_b = pd.DataFrame(), pd.DataFrame()
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])
    except: pass
    return df_h

df_harga = load_all_data()

# --- 5. NAVIGASI ---
st.title("🏛️ Portal Ekonomi Ngada")
m = st.columns(7)
pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, p in enumerate(pages):
    if m[i].button(p, use_container_width=True): st.session_state.page = p
st.divider()

# --- 6. ADMIN ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        st.session_state.store["hero_title"] = st.text_input("Judul", st.session_state.store["hero_title"])
        st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        if st.button("💾 SIMPAN PERMANEN"):
            save_settings(st.session_state.store)
            st.success("Tersimpan!")

# --- 7. LOGIKA HALAMAN HARGA (FIX BOCOR) ---
if st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Komoditas")
    query = st.text_input("🔍 Cari Komoditas...", "").lower()
    
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            # Cek kenaikan Besar
            db = r['B_INI'] - r['B_KMRN']
            cb, bgb, txtb = ("#EF4444", "#FEE2E2", "▲ NAIK") if db > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if db < 0 else ("#64748B", "#F1F5F9", "— STABIL")
            
            # Cek kenaikan Kecil
            dk = r['K_INI'] - r['K_KMRN']
            ck, bgk, txtk = ("#EF4444", "#FEE2E2", "▲ NAIK") if dk > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if dk < 0 else ("#64748B", "#F1F5F9", "— STABIL")

            # Render kartu tanpa variabel terpisah untuk menghindari bug penutup div
            st.markdown(f"""
            <div class="price-card">
                <div style="display: flex; flex-wrap: wrap; align-items: center;">
                    <div style="flex: 1.5; min-width: 200px;">
                        <div style="font-size: 1.2rem; font-weight: bold; color: #000;">{r['KOMODITAS']}</div>
                        <div style="color: #64748B; font-size: 0.9rem;">Satuan: {r['SATUAN']}</div>
                    </div>
                    <div class="box-harga">
                        <div style="font-weight: bold; font-size: 0.8rem; color: #0369a1;">PEDAGANG BESAR</div>
                        <div style="font-size: 1.1rem; font-weight: bold; color: {cb};">Rp {r['B_INI']:,}</div>
                        <div class="status-badge" style="background: {bgb}; color: {cb};">{txtb}</div>
                    </div>
                    <div class="box-harga">
                        <div style="font-weight: bold; font-size: 0.8rem; color: #0369a1;">PEDAGANG KECIL</div>
                        <div style="font-size: 1.1rem; font-weight: bold; color: {ck};">Rp {r['K_INI']:,}</div>
                        <div class="status-badge" style="background: {bgk}; color: {ck};">{txtk}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- 8. HALAMAN POTENSI (FIX GAMBAR) ---
elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Ekonomi Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Cengkeh Ngada")
        with c2:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Pertanian")
        st.write(st.session_state.store["potensi_pertanian"])
    with t2:
        c3, c4 = st.columns(2)
        with c3:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena")
        with c4:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Riung")
        st.write(st.session_state.store["potensi_pariwisata"])

# Default Beranda
elif st.session_state.page == "Beranda":
    st.subheader(st.session_state.store["hero_title"])
    st.info(st.session_state.store["hero_subtitle"])
