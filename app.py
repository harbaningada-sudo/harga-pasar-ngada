import streamlit as st
import pandas as pd
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Portal Ekonomi Ngada", page_icon="🏛️", layout="wide")

# --- CSS KUSTOM ---
st.markdown("""
    <style>
    .card-berita {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    header { background-color: #059669 !important; }
    [data-testid="collapsedControl"] { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI MUAT DATA BERITA ---
@st.cache_data(ttl=60)
def load_data_berita():
    url_berita = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2LMrwn5xk782uKyRGkeOzCXt3DDK-iBxe_F8RUkI7Zk4iYgMVcE_f0XbSc8R72Q/pub?gid=201409714&single=true&output=csv"
    df = pd.read_csv(url_berita, skiprows=2)
    # Sesuaikan urutan kolom: No, Kegiatan, Tipe, Link, Tanggal
    df.columns = ["No", "Kegiatan", "Tipe", "Link", "Tanggal"]
    
    # MEMBERSIHKAN DATA: Hapus baris yang kolom 'Kegiatan'-nya kosong
    df = df.dropna(subset=['Kegiatan'])
    df = df[df['Kegiatan'].astype(str).str.strip() != ""]
    
    return df.fillna("")

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_ngada.png"): 
        st.image("logo_ngada.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #059669;'>PEMKAB NGADA</h2>", unsafe_allow_html=True)
    pilihan = st.radio("Navigasi:", ["🏠 Beranda (Harga)", "📰 Berita & Pasar Murah"])

# --- HALAMAN BERITA ---
if pilihan == "📰 Berita & Pasar Murah":
    st.title("📰 Berita & Media Terkini")
    df_berita = load_data_berita()
    
    if df_berita.empty:
        st.info("Belum ada berita terbaru.")
    else:
        for _, row in df_berita.iterrows():
            with st.container():
                st.markdown(f'<div class="card-berita"><h3>{row["Kegiatan"]}</h3>', unsafe_allow_html=True)
                
                tipe = str(row['Tipe']).lower()
                link = str(row['Link']).strip()

                # HANYA TAMPILKAN JIKA LINK BUKAN "0" ATAU KOSONG
                if link and link != "0" and link.startswith("http"):
                    try:
                        # Konversi link Google Drive Otomatis
                        if "drive.google.com" in link:
                            f_id = link.split('/')[-2] if '/view' in link else link.split('=')[-1]
                            link = f"https://drive.google.com/uc?export=view&id={f_id}"
                        
                        if "foto" in tipe:
                            st.image(link, use_container_width=True)
                        elif "video" in tipe:
                            st.video(link)
                        else:
                            st.info(f"🔗 [Lihat Dokumen Lengkap]({link})")
                    except:
                        st.error("Gagal memuat media. Cek izin akses file.")
                
                # Tampilkan tanggal jika ada isinya
                if row['Tanggal'] and str(row['Tanggal']) != "0":
                    st.write(f"📅 *Tanggal: {row['Tanggal']}*")
                
                st.markdown('</div>', unsafe_allow_html=True)
