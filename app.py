import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI ---
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

# --- 4. LOAD DATA (HARGA & BERITA) ---
@st.cache_data(ttl=60)
def load_all_data():
    # Load Harga
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df_h[col] = pd.to_numeric(df_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = df_h.dropna(subset=['KOMODITAS'])
    except: df_h = pd.DataFrame()

    # Load Berita (GID 201409714)
    try:
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        df_b = pd.read_csv(url_b, skiprows=2)
        df_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = df_b.dropna(subset=['Kegiatan']).fillna("")
    except: df_b = pd.DataFrame()

    return df_h, df_b

df_harga, df_berita = load_all_data()

# --- 5. HEADER & NAVIGASI (7 MENU) ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h1 style='margin-bottom:0;'>KABUPATEN NGADA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#059669; margin-top:0;'>Bagian Perekonomian & SDA Setda Ngada</h4>", unsafe_allow_html=True)

    # Update Navigasi jadi 7 Kolom
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media & Berita", "Tentang", "Unduhan", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, use_container_width=True): st.session_state.page = p

st.divider()

# --- 6. LOGIKA HALAMAN ---

def format_status(ini, kmrn):
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
    st.subheader("🛍️ Laporan Harga Komoditas Rinci")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0 or pd.isna(r['SATUAN']): 
            st.markdown(f"### 📂 {r['KOMODITAS']}"); continue
        st.markdown(f"""
        <div class="price-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1.5;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                <div style="flex: 1; border-left: 1px solid #eee; padding-left:15px;"><small>BESAR</small><br><b>Rp {r['B_INI']:,}</b><br>{format_status(r['B_INI'], r['B_KMRN'])}</div>
                <div style="flex: 1; border-left: 1px solid #eee; padding-left:15px;"><small>KECIL</small><br><b>Rp {r['K_INI']:,}</b><br>{format_status(r['K_INI'], r['K_KMRN'])}</div>
            </div>
        </div>""", unsafe_allow_html=True)

elif st.session_state.page == "Media & Berita":
    st.subheader("📰 Media & Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows(): # Urutan terbaru di atas
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <small style="color:#059669; font-weight:bold;">{row['Tipe']}</small>
                    <h3 style="margin:5px 0;">{row['Kegiatan']}</h3>
                    <p style="font-size:0.9rem; color:gray;">📅 {row['Tanggal']}</p>
                </div>""", unsafe_allow_html=True)
                
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']):
                        st.image(link, use_container_width=True)
                    st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none; background:#059669; color:white; padding:8px 15px; border-radius:8px;">🔗 Lihat Detail</a>', unsafe_allow_html=True)
                st.divider()
    else:
        st.info("Belum ada berita untuk ditampilkan.")

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Tren Harga")
    pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].iloc[:5].tolist()
    df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
    fig = px.bar(df_p, x='KOMODITAS', y='K_INI', title="Harga Pedagang Kecil", color_discrete_sequence=['#059669'])
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Unggulan Ngada")
    t1, t2, t3 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata", "✨ Lainnya"])
    with t1: st.write(store["potensi_pertanian"])
    with t2: st.write(store["potensi_pariwisata"])
    with t3: st.write(store["potensi_lainnya"])

elif st.session_state.page == "Tentang": st.write(store["about_text"])

elif st.session_state.page == "Unduhan":
    st.download_button("📥 Unduh CSV Harga", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
