import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="Ekonomi Digital Ngada", page_icon="🏛️", layout="wide")

# --- 2. CSS BIAR TULISAN HITAM PEKAT ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, div, label { color: #000000 !important; font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FFFFFF !important; }
    .hero-section { background: linear-gradient(135deg, #059669 0%, #10B981 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; color: white !important; }
    .card-container { background: white !important; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 10px; border-left: 10px solid #059669; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI AMBIL DATA (VERSI ANTI-ERROR) ---
@st.cache_data(ttl=10) # Cache diset sebentar saja biar cepat update
def load_data():
    try:
        # Link CSV Bapak
        URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCUaMJFl1dD_iZR9R7QE7dV5S-VlbwU_SUcS5wbzRlyOflTcRg18fiOvu29f4Zd1RMw-WCbwRFo-m2/pub?gid=659700295&single=true&output=csv"
        
        # Baca data langsung tanpa skip dulu untuk tes
        df = pd.read_csv(URL_CSV)
        
        # Kita ambil data mulai dari baris yang ada tulisan "Beras" (biasanya baris ke-7 atau index ke-6)
        # Kita bersihkan data agar mulai dari baris ke-7
        df_clean = df.iloc[5:].copy() 
        
        # Ambil kolom A (0), C (2), D (3), E (4), F (5), G (6)
        df_final = df_clean.iloc[:, [0, 2, 3, 4, 5, 6]]
        df_final.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        # Hapus baris kosong
        df_final = df_final.dropna(subset=['KOMODITAS'])

        # Bersihkan Karakter Titik/Koma agar bisa dihitung
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.replace('-', '0').str.strip()
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
            
        return df_final
    except Exception as e:
        st.error(f"Pesan Error Teknis: {e}") # Ini akan memunculkan error aslinya kalau gagal
        return None

df = load_data()

# --- 4. SIDEBAR ---
def get_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

with st.sidebar:
    img_p = get_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_l = get_base64("logo_ngada.png")
    st.markdown(f"""
        <div style="background:url(data:image/jpeg;base64,{img_p}); background-size:cover; height:180px; border-radius:15px; position:relative; margin-bottom:15px;">
            <div style="position:absolute; bottom:5px; left:5px; background:rgba(255,255,255,0.9); padding:5px; border-radius:8px; border:1px solid #059669;">
                <img src="data:image/png;base64,{img_l}" width="25"><br>
                <b style="font-size:0.55rem; color:#059669;">Bagian Perekonomian & SDA</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("Menu:", ["🏠 Dashboard Utama", "📈 Tren Harga"])

# --- 5. TAMPILAN ---
if df is not None and not df.empty:
    if menu == "🏠 Dashboard Utama":
        st.markdown('<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Data harga pasar terbaru Kabupaten Ngada.</p></div>', unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            # Logika Kategori: Jika Satuan kosong atau berupa angka aneh
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() in ["", "0", "3", "SATUAN"]:
                st.markdown(f"<h3 style='border-bottom:3px solid #059669; margin-top:30px; color:#059669;'>📂 {row['KOMODITAS']}</h3>", unsafe_allow_html=True)
            else:
                selisih = row['K_INI'] - row['K_KMRN']
                if selisih > 0:
                    status = f"<span style='color:red;'>🔺 Naik Rp {selisih:,.0f}</span>"
                elif selisih < 0:
                    status = f"<span style='color:green;'>🔻 Turun Rp {abs(selisih):,.0f}</span>"
                else:
                    status = "<span style='color:gray;'>➖ Stabil</span>"

                st.markdown(f"""
                <div class="card-container">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><b>{row['KOMODITAS']}</b><br><small>Satuan: {row['SATUAN']}</small></div>
                        <div style="text-align:right;">
                            {status}<br>
                            <span style="font-size:1.2rem; font-weight:800;">Rp {row['K_INI']:,.0f}</span><br>
                            <small style="color:gray;">Besar: Rp {row['B_INI']:,.0f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("Sedang menghubungkan ke Google Sheets... Jika lama, pastikan file Excel tidak sedang dalam keadaan 'Filter' aktif.")
