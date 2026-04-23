import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
        "unduhan_info": "Klik tombol di bawah untuk mengunduh laporan harga harian dalam format CSV.",
        "tren_publikasi": [] 
    }

store = init_data()

# LOGIKA ADMIN: Tombol Admin akan muncul otomatis di navigasi jika URL mengandung ?status=set
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #F8FAFC !important; }
    .hero-box { 
        background: linear-gradient(135deg, #059669 0%, #15803D 100%); 
        padding: 20px; border-radius: 12px; text-align: center; color: white !important; margin-bottom: 15px; 
    }
    .price-box {
        background: white; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-naik { color: #DC2626; font-weight: bold; }
    .status-turun { color: #16A34A; font-weight: bold; }
    .status-stabil { color: #D97706; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        df = pd.read_csv(url_h, skiprows=1).iloc[:, [0, 1, 2, 3, 4, 5]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        return df.dropna(subset=['KOMODITAS'])
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 5. HEADER & 6 NAVIGASI UTAMA ---
with st.container():
    c_logo, c_title = st.columns([0.6, 4])
    with c_logo:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=80)
    with c_title:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2><p style='color:green; margin:0;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
    
    # Navigasi 6 Menu + Admin (Jika status=set)
    menu_cols = st.columns(7 if is_admin else 6)
    if menu_cols[0].button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if menu_cols[1].button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if menu_cols[2].button("📈 Trend Harga", use_container_width=True): navigasi("Trend Harga")
    if menu_cols[3].button("ℹ️ Tentang Kita", use_container_width=True): navigasi("Tentang Kita")
    if menu_cols[4].button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if menu_cols[5].button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
    if is_admin:
        if menu_cols[6].button("🛠️ Admin", type="primary", use_container_width=True): navigasi("Admin")

st.divider()

# --- 6. LOGIKA HALAMAN ---

def get_price_html(ini, kmrn):
    if ini > kmrn: return f"<span class='status-naik'>Rp {ini:,} ▲</span>"
    if ini < kmrn: return f"<span class='status-turun'>Rp {ini:,} ▼</span>"
    return f"<span class='status-stabil'>Rp {ini:,} =</span>"

if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    st.info(store["about_text"])

elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Harga Hari Ini vs Kemarin")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"<div style='background:#E2E8F0; padding:5px; font-weight:bold; margin-top:10px;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
        st.markdown(f"""
        <div class="price-box">
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1.5;"><b>{r['KOMODITAS']}</b> ({r['SATUAN']})</div>
                <div style="flex: 1;">
                    <small>Pedagang Besar:</small><br>{get_price_html(r['B_INI'], r['B_KMRN'])}<br><small>Kmrn: {r['B_KMRN']:,}</small>
                </div>
                <div style="flex: 1;">
                    <small>Pedagang Kecil:</small><br>{get_price_html(r['K_INI'], r['K_KMRN'])}<br><small>Kmrn: {r['K_KMRN']:,}</small>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

elif st.session_state.halaman_aktif == "Trend Harga":
    st.header("📈 Trend Harga")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        tab1, tab2 = st.tabs(["Besar", "Kecil"])
        with tab1:
            df_p['Status'] = df_p.apply(lambda x: 'Naik' if x['B_INI'] > x['B_KMRN'] else ('Turun' if x['B_INI'] < x['B_KMRN'] else 'Stabil'), axis=1)
            st.plotly_chart(px.bar(df_p, x="KOMODITAS", y="B_INI", color="Status", color_discrete_map={'Naik':'red','Turun':'green','Stabil':'orange'}), use_container_width=True)
        with tab2:
            df_p['Status'] = df_p.apply(lambda x: 'Naik' if x['K_INI'] > x['K_KMRN'] else ('Turun' if x['K_INI'] < x['K_KMRN'] else 'Stabil'), axis=1)
            st.plotly_chart(px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status", color_discrete_map={'Naik':'red','Turun':'green','Stabil':'orange'}), use_container_width=True)
    else: st.warning("Pilih data di Admin.")

elif st.session_state.halaman_aktif == "Tentang Kita":
    st.write(store["about_text"])
elif st.session_state.halaman_aktif == "Unduhan":
    st.write(store["unduhan_info"])
    st.download_button("Download CSV", df_harga.to_csv(index=False), "harga.csv")
elif st.session_state.halaman_aktif == "Potensi":
    st.success(store["potensi_text"])

elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    store["hero_title"] = st.text_input("Judul Beranda", store["hero_title"])
    store["about_text"] = st.text_area("Tentang Kita", store["about_text"])
    store["tren_publikasi"] = st.multiselect("Komoditas Tren:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    if st.button("Simpan Perubahan"): st.success("Tersimpan!")
