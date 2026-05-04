import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATA (JSON) ---
DB_FILE = "settings_db.json"

def load_settings():
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Riung.",
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

# --- 3. CSS CUSTOM (PROFESSIONAL LOOK) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    
    /* Harga Card */
    .price-card {
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }
    .box-harga {
        flex: 1; min-width: 160px; padding: 12px; background: #f8fafc; border-radius: 10px; margin: 5px;
        border: 1px solid #e2e8f0;
    }
    
    /* Professional Media Card */
    .media-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-top: 4px solid #0369a1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .media-tag {
        background: #E0F2FE; color: #0369a1; padding: 4px 12px;
        border-radius: 20px; font-size: 0.75rem; font-weight: bold;
        text-transform: uppercase;
    }
    .media-date { color: #64748B; font-size: 0.85rem; margin-left: 10px; }
    .media-title { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 10px 0; line-height: 1.4; }
    
    /* Potensi Gallery */
    .img-caption { font-size: 0.85rem; color: #64748B; font-style: italic; text-align: center; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_m = pd.DataFrame(), pd.DataFrame()
    try:
        # Data Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])

        # Data Media
        url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_m = pd.read_csv(url_m, skiprows=2)
        raw_m.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_m = raw_m.dropna(subset=['Kegiatan']).fillna("")
    except: pass
    return df_h, df_m

df_harga, df_media = load_all_data()

# --- 5. NAVIGASI ---
st.title("🏛️ Portal Ekonomi Ngada")
cols_nav = st.columns(7)
menu = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, m in enumerate(menu):
    if cols_nav[i].button(m, use_container_width=True, key=f"nav_{m}"):
        st.session_state.page = m
st.divider()

# --- 6. ADMIN ---
if is_admin:
    with st.sidebar:
        st.header("🛠️ Admin Editor")
        with st.expander("📝 Isi Beranda"):
            st.session_state.store["hero_title"] = st.text_input("Judul", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-judul", st.session_state.store["hero_subtitle"])
        with st.expander("🏛️ Isi Potensi"):
            st.session_state.store["potensi_pertanian"] = st.text_area("Deskripsi Tani", st.session_state.store["potensi_pertanian"])
            st.session_state.store["potensi_pariwisata"] = st.text_area("Deskripsi Wisata", st.session_state.store["potensi_pariwisata"])
        if st.button("💾 SIMPAN PERMANEN"):
            save_settings(st.session_state.store)
            st.success("Perubahan Disimpan!")

# --- 7. TAMPILAN MEDIA (PROFESIONAL) ---
if st.session_state.page == "Media":
    st.markdown("### 📰 Warta Ekonomi & Pembangunan")
    st.write("Informasi terkini kegiatan Bagian Perekonomian & SDA Setda Ngada.")
    
    if not df_media.empty:
        for _, row in df_media.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="media-container">
                <span class="media-tag">{row['Tipe']}</span>
                <span class="media-date">📅 {row['Tanggal']}</span>
                <div class="media-title">{row['Kegiatan']}</div>
            </div>
            """, unsafe_allow_html=True)
            if "http" in str(row['Link']):
                st.link_button(f"🔗 Baca Artikel Lengkap", row['Link'], use_container_width=False)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Belum ada rilis berita.")

# --- 8. TAMPILAN POTENSI (FOTO LENGKAP) ---
elif st.session_state.page == "Potensi":
    st.markdown("### 🏛️ Potensi Ekonomi Unggulan Ngada")
    
    t1, t2 = st.tabs(["🌾 Sektor Pertanian & SDA", "🏞️ Sektor Pariwisata"])
    
    with t1:
        st.write(st.session_state.store["potensi_pertanian"])
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("cengkeh.jpeg"): 
                st.image("cengkeh.jpeg", use_container_width=True)
                st.markdown('<div class="img-caption">Cengkeh: Emas Hijau Ngada</div>', unsafe_allow_html=True)
        with c2:
            if os.path.exists("sawah ngada.webp"): 
                st.image("sawah ngada.webp", use_container_width=True)
                st.markdown('<div class="img-caption">Ketahanan Pangan Ngada</div>', unsafe_allow_html=True)
        
        # Tambahan baris foto jika ada
        c1b, c2b = st.columns(2)
        with c1b:
            if os.path.exists("kopi.jpg"): # Pastikan nama file sesuai
                st.image("kopi.jpg", use_container_width=True)
                st.markdown('<div class="img-caption">Kopi Arabika Bajawa (MPIG)</div>', unsafe_allow_html=True)

    with t2:
        st.write(st.session_state.store["potensi_pariwisata"])
        c3, c4 = st.columns(2)
        with c3:
            if os.path.exists("bena.webp"): 
                st.image("bena.webp", use_container_width=True)
                st.markdown('<div class="img-caption">Kampung Adat Bena</div>', unsafe_allow_html=True)
        with c4:
            if os.path.exists("17 pulau riung.webp"): 
                st.image("17 pulau riung.webp", use_container_width=True)
                st.markdown('<div class="img-caption">Taman Laut 17 Pulau Riung</div>', unsafe_allow_html=True)

# --- 9. HALAMAN LAINNYA ---
elif st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Komoditas")
    query = st.text_input("🔍 Cari Komoditas...", "").lower()
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        for _, r in filtered.iterrows():
            db = r['B_INI'] - r['B_KMRN']
            cb, bgb, txtb = ("#EF4444", "#FEE2E2", "▲ NAIK") if db > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if db < 0 else ("#64748B", "#F1F5F9", "— STABIL")
            dk = r['K_INI'] - r['K_KMRN']
            ck, bgk, txtk = ("#EF4444", "#FEE2E2", "▲ NAIK") if dk > 0 else ("#10B981", "#D1FAE5", "▼ TURUN") if dk < 0 else ("#64748B", "#F1F5F9", "— STABIL")

            st.markdown(f"""
            <div class="price-card">
                <div style="display: flex; flex-wrap: wrap; align-items: flex-start;">
                    <div style="flex: 1.5; min-width: 200px; margin-bottom: 10px;">
                        <div style="font-size: 1.25rem; font-weight: bold; color: #1E293B;">{r['KOMODITAS']}</div>
                        <div style="color: #64748B; font-size: 0.9rem;">Satuan: {r['SATUAN']}</div>
                    </div>
                    <div class="box-harga">
                        <div style="color: #0369a1; font-weight: bold; font-size: 0.8rem;">PEDAGANG BESAR</div>
                        <div style="font-size: 0.7rem; color: #64748B;">Hari Ini: <b style="color:{cb}">Rp {r['B_INI']:,}</b></div>
                        <div style="font-size: 0.7rem; color: #64748B;">Kemarin: <span style="text-decoration:line-through">Rp {r['B_KMRN']:,}</span></div>
                        <div class="status-badge" style="background: {bgb}; color: {cb};">{txtb}</div>
                    </div>
                    <div class="box-harga">
                        <div style="color: #0369a1; font-weight: bold; font-size: 0.8rem;">PEDAGANG KECIL</div>
                        <div style="font-size: 0.7rem; color: #64748B;">Hari Ini: <b style="color:{ck}">Rp {r['K_INI']:,}</b></div>
                        <div style="font-size: 0.7rem; color: #64748B;">Kemarin: <span style="text-decoration:line-through">Rp {r['K_KMRN']:,}</span></div>
                        <div class="status-badge" style="background: {bgk}; color: {ck};">{txtk}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Beranda":
    st.subheader(st.session_state.store["hero_title"])
    st.info(st.session_state.store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Analisis Tren")
    if not df_harga.empty:
        pilihan = st.session_state.store["tren_pilihan"] if st.session_state.store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_INI', 'B_INI'], barmode='group', color_discrete_sequence=['#0ea5e9', '#0369a1'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Tentang":
    st.write(st.session_state.store["about_text"])

elif st.session_state.page == "Unduh":
    st.download_button("Download CSV Harga", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
