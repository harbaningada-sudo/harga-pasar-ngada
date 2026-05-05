import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE (PERMANEN) ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Selamat Datang di Portal Resmi Bagian Perekonomian dan SDA Setda Ngada. Kami hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "about_text": "Bagian Perekonomian dan SDA Setda Ngada. Hadir sebagai pusat informasi, koordinasi, dan fasilitasi pembangunan ekonomi serta pengelolaan sumber daya alam demi kemajuan Kabupaten Ngada",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
        "tren_pilihan": [] 
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                saved_data = json.load(f)
                for key, value in default_data.items():
                    if key not in saved_data: saved_data[key] = value
                return saved_data
        except: return default_data
    return default_data

def save_settings(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Inisialisasi State agar tidak NameError
if "store" not in st.session_state:
    st.session_state.store = load_settings()

if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

is_admin = st.query_params.get("status") == "set"

# --- 3. HELPER GAMBAR & CSS ---
def get_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

img_pimpinan = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
img_logo = get_base64("logo_ngada.png")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #E0F2FE !important; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
    html, body, [data-testid="stWidgetLabel"], .stText, p, h1, h2, h3, h4, h5, h6, span, div, li {{
        color: #000000 !important;
    }}
    .pimpinan-frame {{
        width: 100px; height: 100px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 5px; right: 5px; width: 30px; height: 30px;
        background: white; border-radius: 5px; padding: 2px;
    }}
    .price-card {{
        background: #FFFFFF !important; padding: 15px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 12px; border-left: 5px solid #0369a1;
    }}
    .flex-container {{ display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }}
    .stButton button {{
        background-color: #0369a1 !important; color: #FFFFFF !important;
        border-radius: 8px !important; transition: 0.3s; padding: 5px 10px;
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
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#0369a1; font-weight:bold; margin:0; font-size:1.1rem;'>Bagian Perekonomian & SDA Setda</p>", unsafe_allow_html=True)

    st.write("")
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
st.divider()

# --- 6. ADMIN PANEL ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        st.session_state.store["hero_title"] = st.text_input("Judul Utama", st.session_state.store["hero_title"])
        st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        
        all_items = df_harga['KOMODITAS'].unique().tolist() if not df_harga.empty else []
        st.session_state.store["tren_pilihan"] = st.multiselect("Komoditas Tren", all_items, default=st.session_state.store["tren_pilihan"])
        
        st.session_state.store["potensi_pertanian"] = st.text_area("Teks Pertanian", st.session_state.store["potensi_pertanian"])
        st.session_state.store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", st.session_state.store["potensi_pariwisata"])
        st.session_state.store["about_text"] = st.text_area("Tentang Kami", st.session_state.store["about_text"])

        if st.button("💾 SIMPAN DATA PERMANEN", type="primary", use_container_width=True):
            save_settings(st.session_state.store)
            st.success("Tersimpan!")
            st.balloons()

# --- 7. FUNGSI FORMAT HARGA ---
def format_price_ui(ini, kmrn):
    diff = ini - kmrn
    if diff > 0: color, status, icon = "#EF4444", "NAIK", "▲"
    elif diff < 0: color, status, icon = "#10B981", "TURUN", "▼"
    else: color, status, icon = "#64748B", "STABIL", "—"
    
    return (
        f'<div style="line-height:1.2; margin-top:5px;">'
        f'<div style="font-size: 0.75rem; color: #64748B;">Hari Ini:</div>'
        f'<div style="font-size: 1.1rem; font-weight: bold; color: #1E293B;">Rp {ini:,}</div>'
        f'<div style="font-size: 0.7rem; color: #94A3B8;">Lalu: Rp {kmrn:,}</div>'
        f'<div style="margin-top: 5px; padding: 2px 6px; border-radius: 4px; background: {color}15; display: inline-block;">'
        f'<span style="color:{color}; font-weight:bold; font-size: 0.7rem;">{icon} {status}</span>'
        f'</div></div>'
    )

# --- 8. LOGIKA HALAMAN ---
store = st.session_state.store

if st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Pasar")
    query = st.text_input("🔍 Cari Nama Komoditas...", "").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<div style='background:#0369a1; color:white; padding:8px 15px; border-radius:8px; margin-top:20px; font-weight:bold;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div class="flex-container">
                        <div style="flex: 1.2; min-width:100px;">
                            <div style="font-size: 1.1rem; font-weight: bold; color: #0369a1; line-height:1.2;">{r['KOMODITAS']}</div>
                            <div style="font-size: 0.85rem; color: #64748B; margin-top:4px;">Satuan: {r['SATUAN']}</div>
                        </div>
                        <div style="flex: 1; border-left: 1px solid #eee; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: bold; color: #475569; letter-spacing:0.5px;">PEDAGANG BESAR</div>
                            {format_price_ui(r['B_INI'], r['B_KMRN'])}
                        </div>
                        <div style="flex: 1; border-left: 1px solid #eee; padding-left: 12px;">
                            <div style="font-size: 0.65rem; font-weight: bold; color: #475569; letter-spacing:0.5px;">PEDAGANG KECIL</div>
                            {format_price_ui(r['K_INI'], r['K_KMRN'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Tren Harga")
    if not df_harga.empty:
        pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group', labels={'value':'Harga (Rp)', 'variable':'Waktu'})
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Media":
    st.subheader("📰 Berita Ekonomi & SDA")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.expander(f"{row['Tanggal']} - {row['Kegiatan']}"):
                if "http" in str(row['Link']): st.link_button("Baca Berita", row['Link'])

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Daerah Ngada")
    tab1, tab2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with tab1:
        c_a, c_b = st.columns(2)
        with c_a: 
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Cengkeh Ngada")
        with c_b:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Pertanian")
        st.write(store["potensi_pertanian"])
    with tab2:
        c_c, c_d = st.columns(2)
        with c_c:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena")
        with c_d:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.markdown(f"### Profil Bagian Perekonomian & SDA\n\n{store['about_text']}")

elif st.session_state.page == "Unduh":
    st.download_button("📥 Download Data Harga (CSV)", df_harga.to_csv(index=False), "harga_pasar_ngada.csv", use_container_width=True)
