import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Ekonomi Digital Ngada", page_icon="🏛️", layout="wide")

# --- 2. CSS BIAR TULISAN HITAM & RAPI ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, p, span, div, label { color: #000000 !important; font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FFFFFF !important; }
    .hero-section { background: linear-gradient(135deg, #059669 0%, #10B981 100%); padding: 30px; border-radius: 15px; margin-bottom: 20px; color: white !important; }
    .hero-section h1, .hero-section p { color: white !important; }
    .card-container { background: white !important; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 10px; border-left: 10px solid #059669; }
    .status-badge { padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

# --- 3. FUNGSI MUAT DATA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        # LINK CSV DARI GAMBAR BAPAK (SUDAH SAYA MASUKKAN)
        URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCUaMJFl1dD_iZR9R7QE7dV5S-VlbwU_SUcS5wbzRlyOflTcRg18fiOvu29f4Zd1RMw-WCbwRFo-m2/pub?gid=659700295&single=true&output=csv"
        
        df = pd.read_csv(URL_CSV, skiprows=6)
        # Ambil kolom Jenis Komoditi(0), Satuan(2), Besar-Kemarin(3), Besar-HariIni(4), Kecil-Kemarin(5), Kecil-HariIni(6)
        df = df.iloc[:, [0, 2, 3, 4, 5, 6]]
        df.columns = ['KOMODITAS', 'SATUAN', 'B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']
        df = df.dropna(subset=['KOMODITAS'])

        # Bersihkan titik (.) agar bisa dihitung (Contoh: 13.500 jadi 13500)
        for col in ['B_KMRN', 'B_INI', 'K_KMRN', 'K_INI']:
            df[col] = df[col].astype(str).str.replace('.', '').str.replace(',', '').str.replace('-', '0').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        return None

df = load_data()

# --- 4. SIDEBAR MEWAH ---
with st.sidebar:
    img_p = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
    img_l = get_img_as_base64("logo_ngada.png")
    st.markdown(f"""
        <div style="background:url(data:image/jpeg;base64,{img_p}); background-size:cover; height:180px; border-radius:15px; position:relative; margin-bottom:15px;">
            <div style="position:absolute; bottom:5px; left:5px; background:rgba(255,255,255,0.9); padding:5px; border-radius:8px; border:1px solid #059669;">
                <img src="data:image/png;base64,{img_l}" width="25"><br>
                <b style="font-size:0.55rem; color:#059669;">Bagian Perekonomian & SDA</b>
            </div>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("Menu Layanan:", ["🏠 Dashboard", "📈 Tren Harga"])

# --- 5. TAMPILAN UTAMA ---
if df is not None:
    if menu == "🏠 Dashboard":
        st.markdown(f'<div class="hero-section"><h1>Smart Economy Ngada 👋</h1><p>Pelayanan transparan terhadap harga komoditas bagi masyarakat Ngada.</p></div>', unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            # Logika Kategori (jika Satuan kosong)
            if pd.isna(row['SATUAN']) or str(row['SATUAN']).strip() == "" or str(row['SATUAN']) == "0":
                st.markdown(f"<h3 style='border-bottom:3px solid #059669; margin-top:30px; color:#059669;'>📂 {row['KOMODITAS']}</h3>", unsafe_allow_html=True)
            else:
                # HITUNG SELISIH OTOMATIS (Fokus Pedagang Kecil)
                sel = row['K_INI'] - row['K_KMRN']
                if sel > 0:
                    stt = f"<span class='status-badge' style='background:#FEE2E2; color:#DC2626;'>🔺 Naik Rp {sel:,.0f}</span>"
                elif sel < 0:
                    stt = f"<span class='status-badge' style='background:#D1FAE5; color:#059669;'>🔻 Turun Rp {abs(sel):,.0f}</span>"
                else:
                    stt = f"<span class='status-badge' style='background:#F1F5F9; color:#64748B;'>➖ Stabil</span>"

                st.markdown(f"""
                <div class="card-container">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><b>{row['KOMODITAS']}</b><br><small>Satuan: {row['SATUAN']}</small></div>
                        <div style="text-align:right;">
                            {stt}<br>
                            <span style="font-size:1.2rem; font-weight:800;">Rp {row['K_INI']:,.0f}</span><br>
                            <small style="color:gray;">Pedagang Besar: Rp {row['B_INI']:,.0f}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    elif menu == "📈 Tren Harga":
        st.title("📈 Analisis Tren")
        df_v = df[df['SATUAN'].notna()]
        pilih = st.multiselect("Pilih Komoditas:", df_v['KOMODITAS'].unique())
        if pilih:
            df_p = df_v[df_v['KOMODITAS'].isin(pilih)]
            st.plotly_chart(px.bar(df_p, x="KOMODITAS", y=["K_KMRN", "K_INI"], barmode="group", color_discrete_map={"K_KMRN": "#94A3B8", "K_INI": "#059669"}))
else:
    st.error("⚠️ Data gagal dimuat. Tunggu sebentar atau refresh halaman.")
