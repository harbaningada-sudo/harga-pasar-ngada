import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATA INTERNAL (BERANDA & POTENSI) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_tani": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Hortikultura.",
        "potensi_wisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "potensi_lain": "Sektor UMKM Tenun Ikat dan Bambu menjadi penggerak ekonomi kreatif."
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. HELPER GAMBAR & STYLE ---
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
    .news-card {{
        background: white; padding: 15px; border-radius: 10px; border-bottom: 4px solid #059669; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA SPREADSHEET (HARGA & BERITA) ---
@st.cache_data(ttl=60)
def fetch_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid={gid}&single=true&output=csv"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# Data Harga (GID: 929993273)
df_harga_raw = fetch_sheet("929993273")
if not df_harga_raw.empty:
    df_harga = df_harga_raw.iloc[1:, :6].copy() # Menghindari error skiprows dengan slicing
    df_harga.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
    for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
        df_harga[col] = pd.to_numeric(df_harga[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
else:
    df_harga = pd.DataFrame()

# Data Berita (Pastikan GID-nya benar di Spreadsheet kamu, jika di Sheet1 biasanya gid=0)
df_berita = fetch_sheet("0") 

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
        if m[i].button(f"{icons[i]} {p}", key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

st.divider()

# --- 6. ADMIN PANEL (SIDEBAR) ---
if is_admin:
    with st.sidebar:
        st.title("🛠️ Kontrol Admin")
        with st.expander("📝 Edit Beranda"):
            store["hero_title"] = st.text_input("Judul", store["hero_title"])
            store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
        with st.expander("🏛️ Edit Potensi"):
            store["potensi_tani"] = st.text_area("Pertanian", store["potensi_tani"])
            store["potensi_wisata"] = st.text_area("Pariwisata", store["potensi_wisata"])
            store["potensi_lain"] = st.text_area("Lainnya", store["potensi_lain"])
        st.success("Mode Admin: ON")

# --- 7. LOGIKA HALAMAN ---

def get_status_ui(ini, kmrn):
    selisih = ini - kmrn
    if selisih > 0: return f"<span style='color:#EF4444; font-weight:bold;'>▲ Rp {abs(selisih):,}</span>"
    if selisih < 0: return f"<span style='color:#10B981; font-weight:bold;'>▼ Rp {abs(selisih):,}</span>"
    return "<span style='color:gray;'>— Stabil</span>"

if st.session_state.page == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas Rinci")
    for _, r in df_harga.iterrows():
        if pd.isna(r['SATUAN']) or r['SATUAN'] == 0:
            st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f"""<div class="price-card"><div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="flex:1.5;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
            <div style="flex:1; border-left:1px solid #eee; padding-left:15px;"><small>PEDAGANG BESAR</small><br><b>Rp {r['B_INI']:,}</b><br>{get_status_ui(r['B_INI'], r['B_KMRN'])}</div>
            <div style="flex:1; border-left:1px solid #eee; padding-left:15px;"><small>PEDAGANG KECIL</small><br><b>Rp {r['K_INI']:,}</b><br>{get_status_ui(r['K_INI'], r['K_KMRN'])}</div>
            </div></div>""", unsafe_allow_html=True)

elif st.session_state.page == "Media & Berita":
    st.subheader("📰 Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iterrows():
            st.markdown(f"""<div class="news-card">
                <small style="color:gray;">📅 {row.get('Tanggal', '-')}</small>
                <h4 style="margin:5px 0;">{row.get('Judul', 'Informasi Ekonomi')}</h4>
                <p style="font-size:0.95rem;">{row.get('Isi', '')}</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("Data berita belum terdeteksi. Pastikan GID Tab Berita sudah benar di kode.")

elif st.session_state.page == "Tren":
    st.subheader("📈 Analisis Tren Harga")
    if not df_harga.empty:
        top_10 = df_harga.head(10)
        fig = px.bar(top_10, x='KOMODITAS', y='K_INI', title="Harga Pedagang Kecil", color_discrete_sequence=['#059669'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Daerah")
    t1, t2, t3 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata", "✨ Lainnya"])
    with t1: st.write(store["potensi_tani"])
    with t2: st.write(store["potensi_wisata"])
    with t3: st.write(store["potensi_lain"])

elif st.session_state.page == "Tentang": st.write(store["about_text"])
elif st.session_state.page == "Unduhan": st.download_button("📥 Download Database", df_harga.to_csv(index=False), "harga_ngada.csv")
