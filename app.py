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
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
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
    /* PAKSA WARNA HITAM & BG PUTIH */
    html, body, [data-testid="stWidgetLabel"], .stText, p, h1, h2, h3, h4, h5, h6, span, div, li {{
        color: #000000 !important;
    }}
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="column"] {{ min-width: 0px !important; }}
    
    /* Header & Pimpinan */
    .pimpinan-frame {{
        width: 100px; height: 100px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 5px; right: 5px; width: 30px; height: 30px;
        background: white; border-radius: 5px; padding: 2px;
    }}

    /* Card Harga */
    .price-card {{
        background: #FFFFFF !important; padding: 12px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 8px; border-left: 5px solid #059669;
    }}
    .flex-container {{ display: flex; justify-content: space-between; align-items: center; gap: 5px; }}
    .price-box {{ text-align: center; flex: 1; font-size: 0.85rem; }}

    /* Navigasi */
    .stButton button {{
        background-color: #f1f5f9 !important; color: #000000 !important;
        padding: 5px 2px; font-size: 0.75rem !important; border: 1px solid #e2e8f0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA ---
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

        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_b = pd.read_csv(url_b, skiprows=2)
        raw_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = raw_b.dropna(subset=['Kegiatan']).fillna("")
    except: pass
    return df_h, df_b

df_harga, df_berita = load_all_data()

# --- 5. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h3 style='margin:0;'>KABUPATEN NGADA</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#059669; font-weight:bold; margin:0;'>Bagian Perekonomian & SDA Setda</p>", unsafe_allow_html=True)

    st.write("")
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True): st.session_state.page = p
st.divider()

# --- 6. PANEL ADMIN LENGKAP ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        with st.expander("🏠 Beranda"):
            store["hero_title"] = st.text_input("Judul Utama", store["hero_title"])
            store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
        with st.expander("📈 Grafik Tren"):
            all_items = df_harga['KOMODITAS'].unique().tolist() if not df_harga.empty else []
            store["tren_pilihan"] = st.multiselect("Pilih Komoditas", all_items, default=all_items[:5] if all_items else [])
        with st.expander("🏛️ Potensi"):
            store["potensi_pertanian"] = st.text_area("Teks Pertanian", store["potensi_pertanian"])
            store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", store["potensi_pariwisata"])
        with st.expander("ℹ️ Tentang"):
            store["about_text"] = st.text_area("Konten Tentang", store["about_text"])

# --- 7. LOGIKA HALAMAN ---

def format_price(ini, kmrn):
    diff = ini - kmrn
    color = "#EF4444" if diff > 0 else ("#10B981" if diff < 0 else "#64748B")
    icon = "▲" if diff > 0 else ("▼" if diff < 0 else "—")
    return f"<b>Rp {ini:,}</b><br><small style='color:#64748B;'>Lalu: {kmrn:,}</small><br><span style='color:{color}; font-weight:bold;'>{icon} {abs(diff):,}</span>"

if st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga")
    query = st.text_input("🔍 Cari Komoditas...", "").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<h4 style='color:#059669; margin-top:15px;'>📂 {r['KOMODITAS']}</h4>", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="price-card"><div class="flex-container">
                    <div style="flex: 1.2;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                    <div class="price-box"><small>BESAR</small><br>{format_price(r['B_INI'], r['B_KMRN'])}</div>
                    <div class="price-box" style="border-left:1px solid #eee;"><small>KECIL</small><br>{format_price(r['K_INI'], r['K_KMRN'])}</div>
                </div></div>""", unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Tren Harga")
    if not df_harga.empty:
        pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group', color_discrete_map={'K_KMRN': '#94A3B8', 'K_INI': '#059669'})
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Media":
    st.subheader("📰 Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.expander(f"{row['Tanggal']} - {row['Kegiatan']}"):
                if "http" in str(row['Link']): st.link_button("Lihat", row['Link'])

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        c1, c2 = st.columns(2)
        if os.path.exists("cengkeh.jpeg"): c1.image("cengkeh.jpeg", caption="Cengkeh")
        if os.path.exists("sawah ngada.webp"): c2.image("sawah ngada.webp", caption="Sawah")
        st.write(store["potensi_pertanian"])
    with t2:
        c3, c4 = st.columns(2)
        if os.path.exists("bena.webp"): c3.image("bena.webp", caption="Kampung Bena")
        if os.path.exists("17 pulau riung.webp"): c4.image("17 pulau riung.webp", caption="Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.write(store["about_text"])

elif st.session_state.page == "Unduh":
    st.download_button("📥 Download CSV", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
