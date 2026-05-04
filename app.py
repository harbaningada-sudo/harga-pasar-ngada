import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SISTEM DATABASE (DENGAN PERBAIKAN KEYERROR) ---
DB_FILE = "settings_db.json"

def load_settings():
    # Struktur data default yang lengkap
    default_data = {
        "hero_title": "Smart Economy Ngada 👋",
        "hero_subtitle": "Data harga komoditas akurat untuk masyarakat Ngada.",
        "about_text": "Bagian Perekonomian & SDA Setda Ngada berkomitmen menjaga stabilitas harga daerah.",
        "potensi_pertanian": "Ngada unggul di sektor Kopi Arabika, Cengkeh, dan Pertanian.",
        "potensi_pariwisata": "Destinasi ikonik meliputi Kampung Adat Bena dan Riung.",
        "kontak_email": "ekonomi@ngadakab.go.id",
        "kontak_alamat": "Jl. Soekarno-Hatta No. 1, Bajawa",
        "tren_pilihan": [] 
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                saved_data = json.load(f)
                # Sinkronisasi: Jika ada key baru di default yang belum ada di saved_data, tambahkan!
                for key, value in default_data.items():
                    if key not in saved_data:
                        saved_data[key] = value
                return saved_data
        except:
            return default_data
    return default_data

def save_settings(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Inisialisasi store ke session state
if "store" not in st.session_state:
    st.session_state.store = load_settings()

# Cek Mode Admin
is_admin = st.query_params.get("status") == "set"
if 'page' not in st.session_state:
    st.session_state.page = "Beranda"

# --- 3. CSS CUSTOM ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .price-card {
        background: white; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid #0369a1;
    }
    .box-harga {
        flex: 1; min-width: 160px; padding: 12px; background: #f8fafc; border-radius: 10px; margin: 5px;
        border: 1px solid #e2e8f0;
    }
    .media-container {
        background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px;
        border-top: 4px solid #0369a1; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .status-badge {
        padding: 3px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA LOADER ---
@st.cache_data(ttl=60)
def load_all_data():
    df_h, df_m = pd.DataFrame(), pd.DataFrame()
    try:
        # Harga
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        raw_h = pd.read_csv(url_h, skiprows=1).iloc[:, :6]
        raw_h.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            raw_h[col] = pd.to_numeric(raw_h[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
        df_h = raw_h.dropna(subset=['KOMODITAS'])
        # Media
        url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
        raw_m = pd.read_csv(url_m, skiprows=2)
        raw_m.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
        df_m = raw_m.dropna(subset=['Kegiatan']).fillna("")
    except: pass
    return df_h, df_m

df_harga, df_media = load_all_data()

# --- 5. PANEL EDIT ADMIN ---
if is_admin:
    with st.sidebar:
        st.header("⚙️ Control Panel Admin")
        
        with st.expander("🏠 Edit Beranda", expanded=False):
            st.session_state.store["hero_title"] = st.text_input("Judul Utama", st.session_state.store["hero_title"])
            st.session_state.store["hero_subtitle"] = st.text_area("Sub-Judul", st.session_state.store["hero_subtitle"])
        
        with st.expander("📊 Edit Tren", expanded=False):
            all_items = df_harga['KOMODITAS'].unique().tolist() if not df_harga.empty else []
            st.session_state.store["tren_pilihan"] = st.multiselect("Komoditas di Grafik", all_items, default=st.session_state.store["tren_pilihan"])
        
        with st.expander("🏛️ Edit Potensi", expanded=False):
            st.session_state.store["potensi_pertanian"] = st.text_area("Deskripsi Pertanian", st.session_state.store["potensi_pertanian"])
            st.session_state.store["potensi_pariwisata"] = st.text_area("Deskripsi Pariwisata", st.session_state.store["potensi_pariwisata"])
        
        with st.expander("ℹ️ Edit Tentang & Kontak", expanded=False):
            st.session_state.store["about_text"] = st.text_area("Sejarah/Visi", st.session_state.store["about_text"])
            st.session_state.store["kontak_email"] = st.text_input("Email", st.session_state.store.get("kontak_email", "ekonomi@ngadakab.go.id"))
            st.session_state.store["kontak_alamat"] = st.text_input("Alamat", st.session_state.store.get("kontak_alamat", "Jl. Soekarno-Hatta No. 1, Bajawa"))

        st.divider()
        if st.button("💾 SIMPAN PERUBAHAN", use_container_width=True, type="primary"):
            save_settings(st.session_state.store)
            st.success("Berhasil Disimpan!")
            st.balloons()

# --- 6. NAVIGASI UTAMA ---
st.title("🏛️ Portal Ekonomi Ngada")
cols_nav = st.columns(7)
menu = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, m in enumerate(menu):
    if cols_nav[i].button(m, use_container_width=True, key=f"nav_{m}"):
        st.session_state.page = m
st.divider()

# --- 7. LOGIKA TAMPILAN ---
store = st.session_state.store

if st.session_state.page == "Media":
    st.markdown("### 📰 Warta Ekonomi Terkini")
    if not df_media.empty:
        for _, row in df_media.iloc[::-1].iterrows():
            st.markdown(f"""
            <div class="media-container">
                <span style="background:#E0F2FE; color:#0369a1; padding:4px 10px; border-radius:15px; font-size:12px; font-weight:bold;">{row['Tipe']}</span>
                <span style="color:#64748B; font-size:13px; margin-left:10px;">📅 {row['Tanggal']}</span>
                <div style="font-size:1.3rem; font-weight:bold; color:#1E293B; margin-top:10px;">{row['Kegiatan']}</div>
            </div>
            """, unsafe_allow_html=True)
            if "http" in str(row['Link']):
                st.link_button("🔗 Baca Selengkapnya", row['Link'])
            st.markdown("<br>", unsafe_allow_html=True)

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
                        <div style="font-size: 0.75rem; color: #64748B;">Hari Ini: <b style="color:{cb}">Rp {r['B_INI']:,}</b></div>
                        <div style="font-size: 0.7rem; color: #94A3B8; text-decoration:line-through;">Kemarin: Rp {r['B_KMRN']:,}</div>
                        <div class="status-badge" style="background: {bgb}; color: {cb};">{txtb}</div>
                    </div>
                    <div class="box-harga">
                        <div style="color: #0369a1; font-weight: bold; font-size: 0.8rem;">PEDAGANG KECIL</div>
                        <div style="font-size: 0.75rem; color: #64748B;">Hari Ini: <b style="color:{ck}">Rp {r['K_INI']:,}</b></div>
                        <div style="font-size: 0.7rem; color: #94A3B8; text-decoration:line-through;">Kemarin: Rp {r['K_KMRN']:,}</div>
                        <div class="status-badge" style="background: {bgk}; color: {ck};">{txtk}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Potensi":
    st.markdown("### 🏛️ Potensi Ekonomi Unggulan")
    t1, t2 = st.tabs(["🌾 Pertanian & SDA", "🏞️ Pariwisata"])
    with t1:
        st.write(store["potensi_pertanian"])
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("cengkeh.jpeg"): st.image("cengkeh.jpeg", caption="Potensi Cengkeh", use_container_width=True)
        with c2:
            if os.path.exists("sawah ngada.webp"): st.image("sawah ngada.webp", caption="Lahan Pertanian", use_container_width=True)
    with t2:
        st.write(store["potensi_pariwisata"])
        c3, c4 = st.columns(2)
        with c3:
            if os.path.exists("bena.webp"): st.image("bena.webp", caption="Kampung Bena", use_container_width=True)
        with c4:
            if os.path.exists("17 pulau riung.webp"): st.image("17 pulau riung.webp", caption="Pulau Riung", use_container_width=True)

elif st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    if os.path.exists("IMG_20251125_111048.jpg"): st.image("IMG_20251125_111048.jpg", use_container_width=True)

elif st.session_state.page == "Tren":
    st.subheader("📈 Analisis Tren Harga")
    if not df_harga.empty:
        pilihan = store["tren_pilihan"] if store["tren_pilihan"] else df_harga['KOMODITAS'].head(5).tolist()
        df_p = df_harga[df_harga['KOMODITAS'].isin(pilihan)]
        fig = px.bar(df_p, x='KOMODITAS', y=['K_INI', 'B_INI'], barmode='group', labels={'value':'Harga (Rp)', 'variable':'Tipe Pedagang'}, color_discrete_sequence=['#0ea5e9', '#0369a1'])
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Tentang":
    st.subheader("Informasi Instansi")
    st.write(store["about_text"])
    st.divider()
    st.markdown(f"📧 **Email:** {store.get('kontak_email', '-')}")
    st.markdown(f"📍 **Alamat:** {store.get('kontak_alamat', '-')}")

elif st.session_state.page == "Unduh":
    st.download_button("Download CSV Data Harga", df_harga.to_csv(index=False), "harga_ngada.csv", use_container_width=True)
