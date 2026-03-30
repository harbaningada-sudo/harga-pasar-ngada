import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Digital Ngada", page_icon="🏛️", layout="wide")

# --- 2. CSS KUSTOM (TEKS HITAM & UI BARU) ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, div, label { 
        font-family: 'Inter', sans-serif; color: #000000 !important; 
    }
    .stApp { background-color: #FFFFFF !important; }
    .hero-section {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 20px; margin-bottom: 25px; color: white !important;
    }
    .group-header {
        background: #F1F5F9 !important; padding: 12px 20px; border-radius: 10px;
        margin-top: 25px; font-weight: 800; border-left: 10px solid #059669;
    }
    .card-container {
        background: white !important; padding: 20px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .price-box { text-align: right; border-left: 1px solid #EEE; padding-left: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MUAT DATA (SESUAI GAMBAR SPREADSHEET BARU) ---
@st.cache_data(ttl=60)
def load_all_data():
    try:
        # Gunakan link CSV stabil Bapak
        url_h = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR54g3RrvlqqZ3ppTrKiKK-L1fVT8YSvnXfihtO-H795s0KQ6H_TewZLFFAXPi-ktMizomg3JHdIIjI/pub?gid=929993273&single=true&output=csv"
        
        # Sesuai gambar: baris judul ada di baris ke-2, data mulai baris ke-3
        df_h = pd.read_csv(url_h, skiprows=1) 
        
        # Beri nama kolom secara manual agar tidak 'NAN'
        # Urutan: A=KOMODITAS, B=SATUAN, C=BESAR_KMRN, D=BESAR_INI, E=KECIL_KMRN, F=KECIL_INI
        df_h = df_h.iloc[:, [0, 1, 2, 3, 4, 5]]
        df_h.columns = ['KOMODITAS', 'SATUAN', 'BESAR_KMRN', 'BESAR_INI', 'KECIL_KMRN', 'KECIL_INI']
        
        # Bersihkan data: Hapus baris yang komoditasnya kosong
        df_h = df_h.dropna(subset=['KOMODITAS'])

        # Logika Kategori Otomatis (Jika SATUAN kosong, berarti itu JUDUL)
        current_cat = "LAIN-LAIN"
        categories = []
        for i, row in df_h.iterrows():
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                current_cat = str(row['KOMODITAS']).upper()
            categories.append(current_cat)
        df_h['KATEGORI_INDUK'] = categories
        
        return df_h
    except:
        return pd.DataFrame()

df_harga = load_all_data()

# --- 4. TAMPILAN DASHBOARD ---
if not df_harga.empty:
    st.markdown('<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Informasi harga pedagang besar dan kecil secara transparan.</p></div>', unsafe_allow_html=True)
    
    col_foto, col_data = st.columns([1, 2.5])
    with col_foto:
        if os.path.exists("IMG_20251125_111048.jpg"): 
            st.image("IMG_20251125_111048.jpg", use_container_width=True, caption="Dokumentasi Pasar")
    
    with col_data:
        search = st.text_input("🔍 Cari komoditas...", "")
        df_show = df_harga.copy()
        if search: 
            df_show = df_show[df_show['KOMODITAS'].str.contains(search, case=False, na=False)]
        
        last_header = ""
        for _, row in df_show.iterrows():
            # Tampilkan Header Kategori
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "":
                st.markdown(f'<div class="group-header">📂 {row["KOMODITAS"]}</div>', unsafe_allow_html=True)
                continue
            
            # Konversi harga ke angka agar bisa dihitung selisihnya
            try:
                k_ini = int(pd.to_numeric(row['KECIL_INI'], errors='coerce') or 0)
                k_kmrn = int(pd.to_numeric(row['KECIL_KMRN'], errors='coerce') or 0)
                selisih = k_ini - k_kmrn
                warna = "#DC2626" if selisih > 0 else "#059669" if selisih < 0 else "#94A3B8"
                ikon = "🔺" if selisih > 0 else "🔻" if selisih < 0 else "➖"

                st.markdown(f"""
                <div class="card-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 2;">
                            <b style="font-size:1.1rem;">{row["KOMODITAS"]}</b><br>
                            <small>Satuan: {row["SATUAN"]}</small>
                        </div>
                        <div class="price-box" style="flex: 1.5;">
                            <small style="color: #64748B;">Pedagang Besar</small><br>
                            <b style="font-size:1rem;">Rp {int(row['BESAR_INI']):,}</b>
                        </div>
                        <div class="price-box" style="flex: 1.5;">
                            <small style="color: #64748B;">Pedagang Kecil</small><br>
                            <b style="font-size:1.1rem; color:{warna};">Rp {k_ini:,}</b><br>
                            <small style="color:{warna}; font-weight:bold;">{ikon} {abs(selisih):,}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except: continue
else:
    st.error("Gagal memuat data. Periksa link CSV atau format kolom.")
