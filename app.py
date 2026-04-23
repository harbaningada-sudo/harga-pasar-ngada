import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Ekonomi Ngada", 
    page_icon="🏛️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. SISTEM MEMORI ---
@st.cache_resource
def init_data():
    return {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.",
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

# --- 3. HELPER GAMBAR (DIPERKUAT) ---
def get_img_as_base64(file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

# Cek nama file sesuai screenshot GitHub kamu
foto_path = "Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg"
logo_path = "logo_ngada.png" # Cek di GitHub kamu apakah pakai '_' atau '-'

img_pimpinan = get_img_as_base64(foto_path)
img_logo = get_img_as_base64(logo_path)

# --- 4. CSS CUSTOM (ANTI-ERROR) ---
# Jika gambar tidak ada, CSS akan otomatis menggunakan warna cadangan
bg_style = f'background-image: url("data:image/jpeg;base64,{img_pimpinan}");' if img_pimpinan else 'background-color: #059669;'
logo_html = f'<img src="data:image/png;base64,{img_logo}" style="width:50px;">' if img_logo else '🏛️'

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: #F8FAFC !important; }}
    
    /* Box Header Pimpinan */
    .header-visual-box {{
        width: 120px;
        height: 120px;
        {bg_style}
        background-size: cover;
        background-position: center;
        border-radius: 20px;
        border: 3px solid white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }}
    
    .logo-circle {{
        width: 65px;
        height: 65px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Card Harga */
    .price-card {{
        background: white; border-radius: 15px; padding: 20px;
        border-left: 8px solid #059669; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .grid-container {{
        display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 15px;
    }}
    .price-tag {{ font-size: 1.3rem; font-weight: bold; color: #1E293B; }}
    .status-naik {{ color: #DC2626; font-size: 0.9rem; font-weight: bold; }}
    .status-turun {{ color: #16A34A; font-size: 0.9rem; font-weight: bold; }}
    .status-stabil {{ color: #64748B; font-size: 0.9rem; }}
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

# --- 6. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        # Visual Logo dan Foto Bupati
        st.markdown(f"""
            <div class="header-visual-box">
                <div class="logo-circle">
                    {logo_html}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#059669; font-size:1.2rem; margin:0;'><b>Bagian Perekonomian & SDA Setda Ngada</b></p>", unsafe_allow_html=True)

    # 6 Menu Utama
    st.write("")
    m = st.columns(6)
    if m[0].button("🏠 Beranda", use_container_width=True): navigasi("Beranda")
    if m[1].button("🛍️ Harga", use_container_width=True): navigasi("Harga")
    if m[2].button("📈 Tren", use_container_width=True): navigasi("Tren")
    if m[3].button("ℹ️ Tentang", use_container_width=True): navigasi("Tentang")
    if m[4].button("📥 Unduhan", use_container_width=True): navigasi("Unduhan")
    if m[5].button("🏛️ Potensi", use_container_width=True): navigasi("Potensi")
    
    if is_admin:
        st.button("🛠️ PANEL KONTROL ADMIN", type="primary", use_container_width=True, on_click=navigasi, args=("Admin",))

st.divider()

# --- 7. LOGIKA KONTEN ---

def show_trend(ini, kmrn):
    selisih = ini - kmrn
    if selisih > 0: return f"<span class='status-naik'>▲ Rp {abs(selisih):,} (Naik)</span>"
    if selisih < 0: return f"<span class='status-turun'>▼ Rp {abs(selisih):,} (Turun)</span>"
    return "<span class='status-stabil'>— Stabil</span>"

# Halaman Beranda
if st.session_state.halaman_aktif == "Beranda":
    st.markdown(f"## {store['hero_title']}")
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Kegiatan Operasi Pasar")
    st.write(store["about_text"])

# Halaman Harga (DIBUAT SANGAT JELAS)
elif st.session_state.halaman_aktif == "Harga":
    st.subheader("🛍️ Laporan Harga Hari Ini vs Kemarin")
    for _, r in df_harga.iterrows():
        if r['SATUAN'] == 0:
            st.markdown(f"### 📂 {r['KOMODITAS']}")
            continue
        
        st.markdown(f"""
        <div class="price-card">
            <div class="grid-container">
                <div>
                    <b style="font-size:1.2rem;">{r['KOMODITAS']}</b><br>
                    <small>Satuan: {r['SATUAN']}</small>
                </div>
                <div>
                    <small>PEDAGANG BESAR</small><br>
                    <span class="price-tag">Rp {r['B_INI']:,}</span><br>
                    {show_trend(r['B_INI'], r['B_KMRN'])}<br>
                    <small style="color:gray;">Kmrn: Rp {r['B_KMRN']:,}</small>
                </div>
                <div>
                    <small>PEDAGANG KECIL</small><br>
                    <span class="price-tag">Rp {r['K_INI']:,}</span><br>
                    {show_trend(r['K_INI'], r['K_KMRN'])}<br>
                    <small style="color:gray;">Kmrn: Rp {r['K_KMRN']:,}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Halaman Tren
elif st.session_state.halaman_aktif == "Tren":
    st.subheader("📈 Visualisasi Tren Harga")
    if store["tren_publikasi"]:
        df_p = df_harga[df_harga['KOMODITAS'].isin(store["tren_publikasi"])].copy()
        df_p['Status'] = df_p.apply(lambda x: 'Naik' if x['K_INI'] > x['K_KMRN'] else ('Turun' if x['K_INI'] < x['K_KMRN'] else 'Stabil'), axis=1)
        fig = px.bar(df_p, x="KOMODITAS", y="K_INI", color="Status",
                     color_discrete_map={'Naik': '#DC2626', 'Turun': '#16A34A', 'Stabil': '#64748B'},
                     barmode="group", title="Trend Harga Pedagang Kecil")
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Belum ada data tren yang dipilih Admin.")

# Halaman Lainnya
elif st.session_state.halaman_aktif == "Tentang": st.write(store["about_text"])
elif st.session_state.halaman_aktif == "Unduhan": st.download_button("Download CSV", df_harga.to_csv(index=False), "harga.csv")
elif st.session_state.halaman_aktif == "Potensi": st.success(store["potensi_text"])
elif st.session_state.halaman_aktif == "Admin":
    st.header("🛠️ Admin")
    store["hero_title"] = st.text_input("Judul", store["hero_title"])
    store["tren_publikasi"] = st.multiselect("Pilih Komoditas Tren", df_harga['KOMODITAS'].unique(), default=store["tren_publikasi"])
    if st.button("Simpan"): st.success("Data Tersimpan!")
