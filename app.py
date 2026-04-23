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
        "potensi_text": "Kabupaten Ngada memiliki potensi unggulan di sektor Kopi, Pariwisata, dan Pertanian.",
        "tren_publikasi": [] 
    }

store = init_data()
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target

# --- 3. HELPER GAMBAR ---
def get_img_as_base64(file):
    try:
        if os.path.exists(file):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

img_pimpinan = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
logo_ngada = get_img_as_base64("logo-ngada.png")

# --- 4. CSS ANTI-ERROR & UI PREMIUM ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: #F8FAFC !important; }}
    
    /* Header Visual */
    .header-box {{
        display: flex; align-items: center; gap: 20px; padding: 10px;
    }}
    .pimpinan-frame {{
        width: 100px; height: 100px; border-radius: 15px;
        background-image: url("data:image/jpeg;base64,{img_pimpinan if img_pimpinan else ''}");
        background-size: cover; background-position: center;
        display: flex; align-items: center; justify-content: center;
        border: 2px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .logo-small {{ width: 50px; background: rgba(255,255,255,0.8); border-radius: 50%; padding: 3px; }}

    /* Tabel Harga Kustom */
    .price-container {{
        background: white; border-radius: 12px; padding: 15px;
        border-left: 6px solid #059669; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .grid-price {{
        display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 10px;
    }}
    .price-val {{ font-size: 1.1rem; font-weight: bold; }}
    .diff-up {{ color: #DC2626; font-size: 0.8rem; }}
    .diff-down {{ color: #16A34A; font-size: 0.8rem; }}
    .diff-same {{ color: #64748B; font-size: 0.8rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOAD DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=['KOMODITAS'])
    except: return pd.DataFrame()

df_harga = load_all_data()

# --- 6. HEADER & NAVIGASI (FIXED) ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'''<div class="pimpinan-frame">
            <img src="data:image/png;base64,{logo_ngada if logo_ngada else ''}" class="logo-small">
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown("### KABUPATEN NGADA\n**Bagian Perekonomian & SDA Setda Ngada**")
    
    # 6 Menu Navigasi
    m = st.columns(6)
    if m[0].button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if m[1].button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if m[2].button("📈 Tren", use_container_width=True): navigasi("Tren")
    if m[3].button("ℹ️ Tentang", use_container_width=True): navigasi("Tentang")
    if m[4].button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if m[5].button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
    
    if is_admin:
        if st.button("🛠️ PANEL KONTROL ADMIN", type="primary", use_container_width=True): navigasi("Admin")

st.divider()

# --- 7. LOGIKA HALAMAN ---

def format_diff(ini, kmrn):
    diff = ini - kmrn
    if diff > 0: return f"<span class='diff-up'>▲ Rp {diff:,}</span>"
    if diff < 0: return f"<span class='diff-down'>▼ Rp {abs(diff):,}</span>"
    return "<span class='diff-same'>— Stabil</span>"

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f"## {store['hero_title']}\n{store['hero_subtitle']}")
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)
    st.info(store["about_text"])

# B. HARGA (RINCI)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas Rinci")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"#### 📂 {r['KOMODITAS']}")
            continue
        
        st.markdown(f"""
        <div class="price-container">
            <div class="grid-price">
                <div><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                <div>
                    <small>PEDAGANG BESAR</small><br>
                    <span class="price-val">Rp {r['B_INI']:,}</span><br>
                    {format_diff(r['B_INI'], r['B_KMRN'])}
                </div>
                <div>
                    <small>PEDAGANG KECIL</small><br>
                    <span class="price-val">Rp {r['K_INI']:,}</span><br>
                    {format_diff(r['K_INI'], r['K_KMRN'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# C. TREN (WARNA DINAMIS)
elif st.session_state.halaman_aktif == "Tren":
    st.subheader("📈 Tren Harga (Pedagang Kecil)")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        df_p['Status'] = df_p.apply(lambda x: 'Naik' if x['K_INI'] > x['K_KMRN'] else ('Turun' if x['K_INI'] < x['K_KMRN'] else 'Stabil'), axis=1)
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status",
                     color_discrete_map={'Naik': '#DC2626', 'Turun': '#16A34A', 'Stabil': '#D97706'})
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Pilih data di Admin.")

# D. TENTANG, UNDUHAN, POTENSI
elif st.session_state.halaman_aktif == "Tentang":
    st.write(store["about_text"])
elif st.session_state.halaman_aktif == "Unduhan":
    st.download_button("Unduh Data CSV", df_harga.to_csv(index=False), "harga_ngada.csv")
elif st.session_state.halaman_aktif == "Potensi":
    st.success(store["potensi_text"])

# E. ADMIN
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    store["hero_title"] = st.text_input("Judul Beranda", store["hero_title"])
    store["about_text"] = st.text_area("Teks Tentang Kita", store["about_text"])
    store["tren_publikasi"] = st.multiselect("Pilih Komoditas Tren", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    if st.button("Simpan"): st.success("Tersimpan!")
