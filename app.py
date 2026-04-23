import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (EDITABLE ADMIN) ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "tren_pilihan": [] 
    }

store = init_data()
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
        background: white; padding: 15px; border-radius: 12px; border-bottom: 4px solid #059669;
        margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h_raw = pd.read_csv(url_h)
        df_h = df_h_raw.skiprows(1).iloc[:, :6] if len(df_h_raw) > 1 else df_h_raw
        df_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df_h[col] = pd.to_numeric(df_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        return df_h.dropna(subset=['KOMODITAS']), df_b.dropna(subset=['Kegiatan']).fillna("")
    except: return pd.DataFrame(), pd.DataFrame()

df_harga, df_berita = load_all_data()

# --- 5. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h1 style='margin-bottom:0;'>KABUPATEN NGADA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#059669; margin-top:0;'>Bagian Perekonomian & SDA Setda Ngada</h4>", unsafe_allow_html=True)

    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media & Berita", "Tentang", "Unduhan", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"btn_{p}", use_container_width=True): st.session_state.page = p

st.divider()

# --- 6. PANEL ADMIN ---
if is_admin:
    with st.sidebar:
        st.title("🛠️ Editor Admin")
        store["hero_title"] = st.text_input("Judul", store["hero_title"])
        store["potensi_pertanian"] = st.text_area("Teks Pertanian", store["potensi_pertanian"])
        store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", store["potensi_pariwisata"])

# --- 7. LOGIKA HALAMAN ---

def format_price_ui(ini, kmrn):
    selisih = ini - kmrn
    status = f"<span style='color:#EF4444;'>▲ Rp {abs(selisih):,}</span>" if selisih > 0 else (f"<span style='color:#10B981;'>▼ Rp {abs(selisih):,}</span>" if selisih < 0 else "<span style='color:gray;'>— Stabil</span>")
    return f"<b>Rp {ini:,}</b><br><small style='color:gray;'>Kemarin: {kmrn:,}</small><br>{status}"

if st.session_state.page == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0 or pd.isna(r['SATUAN']): 
            st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f"""<div class="price-card"><div style="display: flex; justify-content: space-between;">
            <div style="flex: 1.2;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
            <div style="flex: 1; text-align:center;"><small>BESAR</small><br>{format_price_ui(r['B_INI'], r['B_KMRN'])}</div>
            <div style="flex: 1; text-align:center;"><small>KECIL</small><br>{format_price_ui(r['K_INI'], r['K_KMRN'])}</div>
        </div></div>""", unsafe_allow_html=True)

elif st.session_state.page == "Media & Berita":
    st.subheader("📰 Media & Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            st.markdown(f'<div class="news-card"><b>{row["Tipe"]}</b><br><h3>{row["Kegiatan"]}</h3><small>{row["Tanggal"]}</small></div>', unsafe_allow_html=True)
            if "http" in str(row['Link']): st.markdown(f"[🔗 Baca Berita]({row['Link']})")

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Unggulan Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    
    with t1:
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Potensi Cengkeh Ngada")
        with col2:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Lahan Pertanian")
        st.write(store["potensi_pertanian"])
        if os.path.exists("tanah-kebun-kopi-dan-cengkeh-siap-panen-.webp"):
            st.image("tanah-kebun-kopi-dan-cengkeh-siap-panen-.webp", use_container_width=True)

    with t2:
        col3, col4 = st.columns(2)
        with col3:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Adat Bena")
        with col4:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Taman Laut 17 Pulau Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Perbandingan Harga")
    pilihan = df_harga['KOMODITAS'].head(5).tolist()
    df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
    fig = px.bar(df_p, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group', title="Tren Harga Pedagang Kecil", color_discrete_map={'K_KMRN': '#94A3B8', 'K_INI': '#059669'})
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Tentang": st.write(store["about_text"])
elif st.session_state.page == "Unduhan":
    st.download_button("📥 Download CSV", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
