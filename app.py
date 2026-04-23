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
is_admin = st.query_params.get("status") == "set"

if 'halaman_aktif' not in st.session_state:
    st.session_state.halaman_aktif = "Beranda"

def navigasi(target):
    st.session_state.halaman_aktif = target
    st.rerun()

# --- 3. CSS KUSTOM (KEJELASAN VISUAL) ---
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
    .label-kemarin { color: #64748B; font-size: 0.85rem; }
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

# --- 5. HEADER & NAVIGASI (6 MENU) ---
with st.container():
    c_logo, c_title = st.columns([0.6, 4])
    with c_logo:
        if os.path.exists("logo-ngada.png"): st.image("logo-ngada.png", width=80)
    with c_title:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2><p style='color:green; margin:0;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)
    
    # 6 Menu Navigasi
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    if m1.button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if m2.button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if m3.button("📈 Trend Harga", use_container_width=True): navigasi("Trend Harga")
    if m4.button("ℹ️ Tentang Kita", use_container_width=True): navigasi("Tentang Kita")
    if m5.button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if m6.button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")

st.divider()

# --- 6. LOGIKA HALAMAN ---

# Fungsi Helper untuk warna status
def get_status_html(ini, kmrn):
    if ini > kmrn: return f"<span class='status-naik'>Rp {ini:,} ▲</span>"
    if ini < kmrn: return f"<span class='status-turun'>Rp {ini:,} ▼</span>"
    return f"<span class='status-stabil'>Rp {ini:,} =</span>"

# A. BERANDA
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f'<div class="hero-box"><h1>{store["hero_title"]}</h1><p>{store["hero_subtitle"]}</p></div>', unsafe_allow_html=True)
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        if os.path.exists("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"):
            st.image("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg", use_container_width=True)
    with col_txt:
        st.info("### Visi Ekonomi Daerah")
        st.write(store["about_text"])

# B. HARGA (PERBANDINGAN JELAS)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Tabel Perbandingan Harga Komoditas")
    st.markdown("<p style='font-size:0.8rem; color:gray;'>* ▲ Naik | ▼ Turun | = Stabil</p>", unsafe_allow_html=True)
    
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"<div style='background:#E2E8F0; padding:5px 10px; border-radius:5px; font-weight:bold; margin-top:15px;'>📂 {r['KOMODITAS']}</div>", unsafe_allow_html=True)
            continue
            
        st.markdown(f"""
        <div class="price-box">
            <div style="display: flex; justify-content:建设; align-items: center;">
                <div style="flex: 1.5;"><b>{r['KOMODITAS']}</b><br><small>{r['SATUAN']}</small></div>
                <div style="flex: 1; border-left: 1px solid #EEE; padding-left:10px;">
                    <small class="label-kemarin">PEDAGANG BESAR</small><br>
                    {get_status_html(r['B_INI'], r['B_KMRN'])}<br>
                    <small class="label-kemarin">Kmrn: Rp {r['B_KMRN']:,}</small>
                </div>
                <div style="flex: 1; border-left: 1px solid #EEE; padding-left:10px;">
                    <small class="label-kemarin">PEDAGANG KECIL</small><br>
                    {get_status_html(r['K_INI'], r['K_KMRN'])}<br>
                    <small class="label-kemarin">Kmrn: Rp {r['K_KMRN']:,}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# C. TREND HARGA (LOGIKA BESAR & KECIL)
elif st.session_state.halaman_aktif == "Trend Harga":
    st.header("📈 Tren Fluktuasi Pasar")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        
        def get_trend_label(ini, kmrn):
            if ini > kmrn: return 'Naik'
            if ini < kmrn: return 'Turun'
            return 'Stabil'
        
        t_besar, t_kecil = st.tabs(["Tren Pedagang Besar", "Tren Pedagang Kecil"])
        
        with t_besar:
            df_p['Status'] = df_p.apply(lambda x: get_trend_label(x['B_INI'], x['B_KMRN']), axis=1)
            fig_b = px.bar(df_p, x="KOMODITAS", y="B_INI", color="Status",
                           color_discrete_map={'Naik': '#DC2626', 'Turun': '#16A34A', 'Stabil': '#D97706'},
                           title="Pergerakan Harga Pedagang Besar")
            st.plotly_chart(fig_b, use_container_width=True)
            
        with t_kecil:
            df_p['Status'] = df_p.apply(lambda x: get_trend_label(x['K_INI'], x['K_KMRN']), axis=1)
            fig_k = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status",
                           color_discrete_map={'Naik': '#DC2626', 'Turun': '#16A34A', 'Stabil': '#D97706'},
                           title="Pergerakan Harga Pedagang Kecil")
            st.plotly_chart(fig_k, use_container_width=True)
    else:
        st.warning("Silakan pilih komoditas yang ingin dipantau di Panel Admin.")

# D. TENTANG KITA
elif st.session_state.halaman_aktif == "Tentang Kita":
    st.header("ℹ️ Tentang Kita")
    st.write(store["about_text"])

# E. UNDUHAN
elif st.session_state.halaman_aktif == "Unduhan":
    st.header("📥 Pusat Unduhan")
    st.write(store["unduhan_info"])
    st.download_button("Download Data Harga CSV", df_harga.to_csv(index=False), "data_harga_ngada.csv", "text/csv")

# F. POTENSI DAERAH
elif st.session_state.halaman_aktif == "Potensi":
    st.header("🏛️ Potensi Daerah")
    st.success(store["potensi_text"])

# G. ADMIN
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Panel Admin")
    t1, t2 = st.tabs(["Edit Konten Teks", "Pilih Grafik Tren"])
    with t1:
        store["hero_title"] = st.text_input("Judul Beranda:", store["hero_title"])
        store["about_text"] = st.text_area("Teks Tentang Kita:", store["about_text"])
        store["potensi_text"] = st.text_area("Teks Potensi Daerah:", store["potensi_text"])
    with t2:
        store["tren_publikasi"] = st.multiselect("Pilih Komoditas untuk Grafik:", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    if st.button("Simpan Perubahan"):
        st.success("Data diperbarui!")
