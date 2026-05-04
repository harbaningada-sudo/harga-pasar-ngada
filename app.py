import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM PENYIMPANAN PERMANEN ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian Hortikultura.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Taman Laut 17 Pulau Riung.",
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
    html, body, [data-testid="stWidgetLabel"], .stText, p, h1, h2, h3, h4, h5, h6, span, div, li {{
        color: #000000 !important;
    }}
    .price-card {{
        background: #FFFFFF !important; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 10px solid #0369a1;
    }}
    .status-badge {{
        padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold;
    }}
    .price-label {{ font-size: 0.8rem; color: #64748B; margin-bottom: 2px; }}
    .price-value {{ font-size: 1.1rem; font-weight: bold; }}
    
    .pimpinan-frame {{
        width: 100px; height: 100px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 5px; right: 5px; width: 30px; height: 30px;
        background: white; border-radius: 5px; padding: 2px;
    }}
    .stButton button {{
        background-color: #0369a1 !important; color: #FFFFFF !important;
        border-radius: 8px !important;
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
        st.markdown("<p style='color:#0369a1; font-weight:bold; margin:0;'>Bagian Perekonomian & SDA Setda</p>", unsafe_allow_html=True)

    st.write("")
    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True): st.session_state.page = p
st.divider()

# --- 6. ADMIN PANEL ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        with st.expander("📝 Edit Konten"):
            st.session_state.store["hero_title"] = st.text_input("Judul Utama", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        if st.button("💾 SIMPAN PERMANEN"):
            save_settings(st.session_state.store)
            st.success("Tersimpan!")

# --- 7. LOGIKA HARGA ---
def get_price_display(ini, kmrn):
    diff = ini - kmrn
    if diff > 0:
        color = "#EF4444" # Merah
        badge = f"<span class='status-badge' style='background:#FEE2E2; color:#EF4444;'>▲ NAIK Rp {abs(diff):,}</span>"
    elif diff < 0:
        color = "#10B981" # Hijau
        badge = f"<span class='status-badge' style='background:#D1FAE5; color:#10B981;'>▼ TURUN Rp {abs(diff):,}</span>"
    else:
        color = "#64748B" # Abu-abu
        badge = f"<span class='status-badge' style='background:#F1F5F9; color:#64748B;'>— STABIL</span>"
    
    return f"""
        <div style="margin-bottom: 5px;">
            <div class="price-label">Hari Ini:</div>
            <div class="price-value" style="color:{color};">Rp {ini:,}</div>
        </div>
        <div style="margin-bottom: 8px;">
            <div class="price-label">Kemarin:</div>
            <div style="font-size: 0.9rem; color: #94A3B8; text-decoration: line-through;">Rp {kmrn:,}</div>
        </div>
        {badge}
    """

if st.session_state.page == "Beranda":
    st.subheader(st.session_state.store["hero_title"])
    st.info(st.session_state.store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Daftar Harga Komoditas Daerah")
    query = st.text_input("🔍 Cari Nama Komoditas (Contoh: Beras, Cabai...)", "").lower()
    
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<h4 style='color:#0369a1; margin-top:25px; border-bottom:2px solid #0369a1; padding-bottom:5px;'>📂 {r['KOMODITAS']}</h4>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                        <div style="flex: 1.2; min-width: 200px;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #1E293B;">{r['KOMODITAS']}</div>
                            <div style="color: #64748B; font-size: 0.9rem;">Satuan: {r['SATUAN']}</div>
                        </div>
                        <div style="flex: 1; min-width: 150px; padding: 10px; background: #f8fafc; border-radius: 10px;">
                            <div style="font-weight: bold; font-size: 0.85rem; color: #0369a1; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0;">🏪 PEDAGANG BESAR</div>
                            {get_price_display(r['B_INI'], r['B_KMRN'])}
                        </div>
                        <div style="flex: 1; min-width: 150px; padding: 10px; background: #f8fafc; border-radius: 10px;">
                            <div style="font-weight: bold; font-size: 0.85rem; color: #0369a1; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0;">🏪 PEDAGANG KECIL</div>
                            {get_price_display(r['K_INI'], r['K_KMRN'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.page == "Media":
    st.subheader("📰 Berita Ekonomi Ngada")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.expander(f"📅 {row['Tanggal']} - {row['Kegiatan']}"):
                if "http" in str(row['Link']): st.link_button("Baca Berita", row['Link'])
    else: st.info("Belum ada berita terbaru.")

elif st.session_state.page == "Tren":
    st.subheader("📈 Analisis Grafik Tren")
    if not df_harga.empty:
        pilihan = st.session_state.store["tren_pilihan"] if st.session_state.store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_INI', 'B_INI'], barmode='group', title="Perbandingan Harga Hari Ini", color_discrete_sequence=['#0ea5e9', '#0369a1'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Ekonomi Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1: st.write(st.session_state.store["potensi_pertanian"])
    with t2: st.write(st.session_state.store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.write(st.session_state.store["about_text"])

elif st.session_state.page == "Unduh":
    st.download_button("📥 Unduh Data Harga (CSV)", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
