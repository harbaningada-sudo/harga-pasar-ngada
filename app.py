import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM MEMORI (EDITABLE) ---
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
    .stApp {{ background-color: #F8FAFC; }}
    .pimpinan-frame {{
        width: 120px; height: 120px; border-radius: 15px; border: 3px solid #059669;
        background-image: url("data:image/jpeg;base64,{img_pimpinan}");
        background-size: cover; background-position: center; position: relative;
    }}
    .logo-mini {{
        position: absolute; bottom: 5px; right: 5px; width: 35px; height: 35px;
        background: white; border-radius: 5px; padding: 2px;
    }}
    .price-card {{
        background: white; padding: 15px; border-radius: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px; border-left: 5px solid #059669;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD DATA ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h = pd.DataFrame(columns=['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI'])
    df_b = pd.DataFrame(columns=["No", "Kegiatan", "Tipe", "Link", "Tanggal"])
    try:
        # Load Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])

        # Load Berita
        url_b = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_b = pd.read_csv(url_b, skiprows=2)
        raw_b.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_b = raw_b.dropna(subset=['Kegiatan']).fillna("")
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
    return df_h, df_b

df_harga, df_berita = load_all_data()

# --- 5. HEADER & NAVIGASI ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f'<div class="pimpinan-frame"><div class="logo-mini"><img src="data:image/png;base64,{img_logo}" width="100%"></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h2 style='margin-bottom:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#059669; font-weight:bold;'>Bagian Perekonomian & SDA Setda Ngada</p>", unsafe_allow_html=True)

    m = st.columns(7)
    pages = ["Beranda", "Harga", "Tren", "Media & Berita", "Tentang", "Unduhan", "Potensi"]
    for i, p in enumerate(pages):
        if m[i].button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

st.divider()

# --- 6. PANEL ADMIN LENGKAP (URL: ?status=set) ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Panel Editor Admin")
        st.info("Mode Edit Aktif. Perubahan bersifat sementara di memori.")
        
        with st.expander("🏠 Edit Beranda"):
            store["hero_title"] = st.text_input("Judul Utama", store["hero_title"])
            store["hero_subtitle"] = st.text_area("Sub-judul", store["hero_subtitle"])
        
        with st.expander("📈 Edit Grafik Tren"):
            all_items = df_harga['KOMODITAS'].unique().tolist() if not df_harga.empty else []
            store["tren_pilihan"] = st.multiselect("Pilih Komoditas untuk Grafik", all_items, default=store["tren_pilihan"] if store["tren_pilihan"] else all_items[:5])
            
        with st.expander("🏛️ Edit Potensi Daerah"):
            store["potensi_pertanian"] = st.text_area("Teks Pertanian", store["potensi_pertanian"])
            store["potensi_pariwisata"] = st.text_area("Teks Pariwisata", store["potensi_pariwisata"])
            
        with st.expander("ℹ️ Edit Tentang"):
            store["about_text"] = st.text_area("Konten Tentang Kami", store["about_text"])
            
        st.success("Editor Berhasil Dimuat!")

# --- 7. LOGIKA HALAMAN ---

def format_price(ini, kmrn):
    diff = ini - kmrn
    color = "#EF4444" if diff > 0 else ("#10B981" if diff < 0 else "gray")
    icon = "▲" if diff > 0 else ("▼" if diff < 0 else "—")
    return f"<b>Rp {ini:,}</b><br><small style='color:gray;'>Kemarin: {kmrn:,}</small><br><span style='color:{color};'>{icon} Rp {abs(diff):,}</span>"

if st.session_state.page == "Beranda":
    st.title(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Harga":
    st.subheader("🛍️ Pantauan Harga Komoditas")
    if not df_harga.empty:
        for _, r in df_harga.iterrows():
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"#### 📂 {r['KOMODITAS']}")
            else:
                st.markdown(f"""<div class="price-card"><div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1.2;"><b>{r['KOMODITAS']}</b><br><small>Satuan: {r['SATUAN']}</small></div>
                    <div style="flex: 1; text-align:center;"><small>BESAR</small><br>{format_price(r['B_INI'], r['B_KMRN'])}</div>
                    <div style="flex: 1; text-align:center;"><small>KECIL</small><br>{format_price(r['K_INI'], r['K_KMRN'])}</div>
                </div></div>""", unsafe_allow_html=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Grafik Perbandingan Harga")
    if not df_harga.empty:
        # Gunakan pilihan dari admin jika ada
        pilihan_komoditas = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan_komoditas)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_KMRN', 'K_INI'], barmode='group', 
                     title="Tren Harga Pedagang Kecil", color_discrete_map={'K_KMRN': '#94A3B8', 'K_INI': '#059669'})
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Media & Berita":
    st.subheader("📰 Berita Terkini")
    if not df_berita.empty:
        for _, row in df_berita.iloc[::-1].iterrows():
            with st.expander(f"{row['Tanggal']} - {row['Kegiatan']}"):
                st.write(f"**Tipe:** {row['Tipe']}")
                link = str(row['Link']).strip()
                if link.startswith("http"):
                    if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']):
                        st.image(link, use_container_width=True)
                    st.link_button("🔗 Baca Selengkapnya", link)
    else: st.info("Data berita belum tersedia.")

elif st.session_state.page == "Potensi":
    st.subheader("🏛️ Potensi Unggulan Daerah")
    t1, t2 = st.tabs(["🌾 Pertanian", "🏞️ Pariwisata"])
    with t1:
        c1, c2 = st.columns(2)
        with c1: 
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Cengkeh")
        with c2:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Sawah")
        st.write(store["potensi_pertanian"])
    with t2:
        c3, c4 = st.columns(2)
        with c3:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena")
        with c4:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="17 Pulau Riung")
        st.write(store["potensi_pariwisata"])

elif st.session_state.page == "Tentang":
    st.markdown(f"### Profil & Tentang\n{store['about_text']}")

elif st.session_state.page == "Unduhan":
    st.download_button("📥 Unduh CSV Harga", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
