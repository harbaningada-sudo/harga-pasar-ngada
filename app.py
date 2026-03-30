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

# --- 3. FUNGSI AMBIL DATA ---
@st.cache_data(ttl=5) # Cache sangat singkat agar cepat update
def load_data():
    try:
        # MASUKKAN LINK CSV BAPAK DI SINI
        URL_CSV = "TEMPEL_LINK_CSV_BARU_BAPAK_DI_SINI"
        
        # Baca data asli
        df_raw = pd.read_csv(URL_CSV)
        
        # Sesuai gambar Bapak: Baris judul (Beras, dll) ada di baris ke-7 (index 6)
        # Kita ambil data mulai dari baris data pertama
        df_data = df_raw.iloc[5:].copy()
        
        # Ambil kolom Jenis Komoditi(0), Satuan(2), Besar-Kmrn(3), Besar-Ini(4), Kecil-Kmrn(5), Kecil-Ini(6)
        df_final = df_data.iloc[:, [0, 2, 3, 4, 5, 6]]
        df_final.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        
        # Hapus baris yang komoditasnya kosong
        df_final = df_final.dropna(subset=['KOMODITAS'])

        # Bersihkan Karakter Titik agar bisa dihitung
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.replace('-', '0').str.strip()
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
            
        return df_final
    except Exception as e:
        st.error(f"Gagal Hubung ke Excel: {e}")
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
    menu = st.radio("Pilih Menu:", ["🏠 Dashboard", "📈 Tren Harga"])

# --- 5. TAMPILAN DASHBOARD ---
if df is not None:
    if menu == "🏠 Dashboard":
        st.markdown('<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Update harga komoditas pasar hari ini.</p></div>', unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            # Baris Kategori: Jika Satuan tidak ada harganya
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() in ["", "0", "3", "SATUAN"]:
                st.markdown(f"<h3 style='border-bottom:3px solid #059669; margin-top:30px; color:#059669;'>📂 {row['KOMODITAS']}</h3>", unsafe_allow_html=True)
            else:
                # Hitung naik/turun
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
    st.info("Sedang memproses link Spreadsheet baru Bapak...")
