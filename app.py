import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (DAPAT DIEDIT ADMIN) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "potensi_lainnya": "Sektor UMKM Tenun Ikat dan Bambu menjadi penggerak ekonomi kreatif.",
        "tren_pilihan": [] 
    }

store = init_data()

# Mendeteksi status admin dari URL (?status=set)
is_admin = st.query_params.get("status") == "set"

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
    [data-testid="stSidebar"] {{ background-color: #f0f2f6; }}
    .stApp {{ background-color: #F8FAFC; }}
    
    /* Bingkai Pimpinan */
    .pimpinan-frame {{
        width: 130px; height: 130px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    .logo-mini {{
        position: absolute; bottom: 8px; right: 8px; width: 38px; height: 38px;
        background: white; border-radius: 8px; padding: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}

    /* Card Harga */
    .price-card {{
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #059669;
    }}
    .status-naik {{ color: #EF4444; font-weight: bold; font-size: 0.85rem; }}
    .status-turun {{ color: #10B981; font-weight: bold; font-size: 0.85rem; }}
    .status-stabil {{ color: #6B7280; font-size: 0.85rem; }}
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

# --- 5. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h1 style='margin-bottom:0;'>KABUPATEN NGADA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#059669; margin-top:0;'>Bagian Perekonomian & SDA Setda Ngada</h4>", unsafe_allow_html=True)

    # Menu Navigasi
    m = st.columns(6)
    pages = ["Beranda", "Harga", "Tren", "Tentang", "Unduhan", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, use_container_width=True): st.session_state.page = p

st.divider()

# --- 6. PANEL ADMIN (EDITOR) ---
if is_admin:
    with st.sidebar:
        st.title("🛠️ Editor Admin")
        st.info("Mode Edit Aktif. Perubahan akan langsung terlihat di aplikasi.")
        
        with st.expander("📝 Edit Beranda"):
            store["hero_title"] = st.text_input("Judul", store["hero_title"])
            store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
            
        with st.expander("📈 Edit Tren"):
            store["tren_pilihan"] = st.multiselect("Pilih Komoditas untuk Grafik", df_harga['KOMODITAS'].unique(), default=store["tren_pilihan"])
            
        with st.expander("🏛️ Edit Potensi"):
            store["potensi_pertanian"] = st.text_area("Sektor Pertanian", store["potensi_pertanian"])
            store["potensi_pariwisata"] = st.text_area("Sektor Pariwisata", store["potensi_pariwisata"])
            store["potensi_lainnya"] = st.text_area("Sektor Lainnya", store["potensi_lainnya"])
            
        with st.expander("ℹ️ Edit Tentang"):
            store["about_text"] = st.text_area("Teks Tentang Kami", store["about_text"])

# --- 7. LOGIKA HALAMAN ---

def format_status(ini, kmrn):
    selisih = ini - kmrn
    if selisih > 0: return f"<span class='status-naik'>▲ Naik (Rp {abs(selisih):,})</span>"
    if selisih < 0: return f"<span class='status-turun'>▼ Turun (Rp {abs(selisih):,})</span>"
    return "<span class='status-stabil'>— Stabil</span>"

if st.session_state.page == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.subheader("🛍️ Laporan Harga Komoditas Rinci")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0: 
            st.markdown(f"### 📂 {r['KOMODITAS']}")
            continue
        
        st.markdown(f"""
        <div class="price-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1.5;">
                    <b style="font-size: 1.2rem; color: #1E293B;">{r['KOMODITAS']}</b><br>
                    <small style="color: #64748B;">Satuan: {r['SATUAN']}</small>
                </div>
                <div style="flex: 1; border-left: 1px solid #E2E8F0; padding-left: 15px;">
                    <small style="text-transform: uppercase; color: #94A3B8; font-weight: bold;">Pedagang Besar</small><br>
                    <span style="font-size: 1.1rem; font-weight: bold;">Rp {r['B_INI']:,}</span><br>
                    {format_status(r['B_INI'], r['B_KMRN'])}<br>
                    <small style="color: #94A3B8;">Kemarin: Rp {r['B_KMRN']:,}</small>
                </div>
                <div style="flex: 1; border-left: 1px solid #E2E8F0; padding-left: 15px;">
                    <small style="text-transform: uppercase; color: #94A3B8; font-weight: bold;">Pedagang Kecil</small><br>
                    <span style="font-size: 1.1rem; font-weight: bold;">Rp {r['K_INI']:,}</span><br>
                    {format_status(r['K_INI'], r['K_KMRN'])}<br>
                    <small style="color: #94A3B8;">Kemarin: Rp {r['K_KMRN']:,}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Tren Harga")
    pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].iloc[:5].tolist()
    df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
    fig = px.bar(df_p, x='KOMODITAS', y='K_INI', title="Harga Pedagang Kecil Hari Ini", color_discrete_sequence=['#059669'])
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Unggulan Ngada")
    t1, t2, t3 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata", "✨ Lainnya"])
    with t1: st.write(store["potensi_pertanian"])
    with t2: st.write(store["potensi_pariwisata"])
    with t3: st.write(store["potensi_lainnya"])

elif st.session_state.page == "Tentang":
    st.write(store["about_text"])

elif st.session_state.page == "Unduhan":
    st.download_button("📥 Unduh Database Harga (CSV)", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
