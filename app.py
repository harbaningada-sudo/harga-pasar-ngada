import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATA (JSON) ---
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

# --- 3. CSS CUSTOM (FIX TAMPILAN) ---
st.markdown("""
    <style>
    .stApp { background-color: #E0F2FE !important; }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }
    .box-harga {
        flex: 1; min-width: 160px; padding: 12px; background: #f8fafc; border-radius: 10px; margin: 5px;
        border: 1px solid #e2e8f0;
    }
    .label-harga { font-size: 0.75rem; color: #64748B; font-weight: bold; }
    .val-hari-ini { font-size: 1.1rem; font-weight: bold; margin-bottom: 2px; }
    .val-kemarin { font-size: 0.85rem; color: #94A3B8; text-decoration: line-through; }
    .status-badge {
        padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h = pd.DataFrame()
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

# --- 5. NAVIGASI UTAMA (Selalu Muncul) ---
st.title("🏛️ Portal Ekonomi Ngada")
cols_nav = st.columns(7)
menu = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, m in enumerate(menu):
    if cols_nav[i].button(m, use_container_width=True, key=f"btn_{m}"):
        st.session_state.page = m
st.divider()

# --- 6. ADMIN SIDEBAR (PILIHAN EDIT LENGKAP) ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        
        with st.expander("📝 Edit Beranda"):
            st.session_state.store["hero_title"] = st.text_input("Judul Beranda", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul Beranda", st.session_state.store["hero_subtitle"])
            
        with st.expander("📊 Edit Tren"):
            all_items = df_harga['KOMODITAS'].unique().tolist() if not df_harga.empty else []
            st.session_state.store["tren_pilihan"] = st.multiselect("Pilih Komoditas Grafik", all_items, default=st.session_state.store["tren_pilihan"])
            
        with st.expander("🏛️ Edit Potensi"):
            st.session_state.store["potensi_pertanian"] = st.text_area("Teks Pertanian", st.session_state.store["potensi_pertanian"])
            st.session_state.store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", st.session_state.store["potensi_pariwisata"])
            
        with st.expander("ℹ️ Edit Tentang"):
            st.session_state.store["about_text"] = st.text_area("Konten Tentang", st.session_state.store["about_text"])

        if st.button("💾 SIMPAN PERMANEN", use_container_width=True):
            save_settings(st.session_state.store)
            st.success("Perubahan Berhasil Disimpan!")

# --- 7. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Komoditas")
    query = st.text_input("🔍 Cari Komoditas...", "").lower()
    
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            # Hitung Status Besar
            db = r['B_INI'] - r['B_KMRN']
            cb, bgb, txtb = ("#EF4444", "#FEE2E2", "▲ NAIK") if db > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if db < 0 else ("#64748B", "#F1F5F9", "— STABIL")
            
            # Hitung Status Kecil
            dk = r['K_INI'] - r['K_KMRN']
            ck, bgk, txtk = ("#EF4444", "#FEE2E2", "▲ NAIK") if dk > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if dk < 0 else ("#64748B", "#F1F5F9", "— STABIL")

            # HTML Card (Harga Kemarin vs Hari Ini)
            st.markdown(f"""
            <div class="price-card">
                <div style="display: flex; flex-wrap: wrap; align-items: flex-start;">
                    <div style="flex: 1.5; min-width: 200px; margin-bottom: 10px;">
                        <div style="font-size: 1.25rem; font-weight: bold; color: #1e293b;">{r['KOMODITAS']}</div>
                        <div style="color: #64748B; font-size: 0.9rem;">Satuan: {r['SATUAN']}</div>
                    </div>
                    <div class="box-harga">
                        <div style="color: #0369a1; font-weight: bold; font-size: 0.8rem; border-bottom: 1px solid #e2e8f0; margin-bottom: 8px;">PEDAGANG BESAR</div>
                        <div class="label-harga">Hari Ini:</div>
                        <div class="val-hari-ini" style="color: {cb};">Rp {r['B_INI']:,}</div>
                        <div class="label-harga">Kemarin:</div>
                        <div class="val-kemarin">Rp {r['B_KMRN']:,}</div>
                        <div class="status-badge" style="background: {bgb}; color: {cb};">{txtb}</div>
                    </div>
                    <div class="box-harga">
                        <div style="color: #0369a1; font-weight: bold; font-size: 0.8rem; border-bottom: 1px solid #e2e8f0; margin-bottom: 8px;">PEDAGANG KECIL</div>
                        <div class="label-harga">Hari Ini:</div>
                        <div class="val-hari-ini" style="color: {ck};">Rp {r['K_INI']:,}</div>
                        <div class="label-harga">Kemarin:</div>
                        <div class="val-kemarin">Rp {r['K_KMRN']:,}</div>
                        <div class="status-badge" style="background: {bgk}; color: {ck};">{txtk}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Analisis Tren")
    if not df_harga.empty:
        pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_INI', 'B_INI'], barmode='group', labels={'value':'Harga (Rp)', 'variable':'Tipe'}, color_discrete_sequence=['#0ea5e9', '#0369a1'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Ekonomi")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        c1, c2 = st.columns(2)
        with c1: 
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Cengkeh Ngada")
        with c2: 
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Sektor Pertanian")
        st.write(store["potensi_pertanian"])
    with t2:
        c3, c4 = st.columns(2)
        with c3: 
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena")
        with c4: 
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.write(store["about_text"])

elif st.session_state.page == "Unduh":
    st.subheader("📥 Unduh Data")
    st.download_button("Download CSV Harga", df_harga.to_csv(index=False), "harga_ngada.csv", "text/csv", use_container_width=True)
