# --- 1. Pastikan Bagian CSS di paling atas sudah seperti ini ---
st.markdown("""
    <style>
    /* Container untuk Foto & Logo */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    /* Frame Foto dengan Logo di Dalamnya */
    .photo-frame {
        position: relative;
        width: 150px;
        height: 150px;
        border-radius: 15px;
        border: 3px solid #047857; /* Warna hijau sesuai gambar */
        overflow: hidden;
        background-color: white;
    }
    
    .main-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .overlay-logo {
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 40px;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));
    }

    .title-text {
        font-family: 'Arial', sans-serif;
    }
    .title-text h1 {
        margin: 0;
        color: #1e293b;
        font-size: 2rem;
        letter-spacing: 1px;
    }
    .title-text p {
        margin: 0;
        color: #475569;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Bagian Header (Foto & Logo) ---
# Fungsi untuk merender gambar ke Base64 agar bisa masuk HTML
def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

foto_base64 = get_base64("IMG_20251125_111048.jpg")
logo_base64 = get_base64("logo_ngada.png")

# Tampilan Header Atas
st.markdown(f"""
    <div class="header-container">
        <div class="photo-frame">
            <img src="data:image/jpeg;base64,{foto_base64}" class="main-img">
            <img src="data:image/png;base64,{logo_base64}" class="overlay-logo">
        </div>
        <div class="title-text">
            <h1>KABUPATEN NGADA 🔗</h1>
            <p>Bagian Perekonomian & SDA Setda</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. Menu Navigasi (Tombol Biru) ---
cols = st.columns(7)
menu_items = ["Beranda", "Harga", "Tren", "Media", "Tentang", "Unduh", "Potensi"]
for i, item in enumerate(menu_items):
    if cols[i].button(item, use_container_width=True, key=f"btn_{item}"):
        st.session_state.page = item

st.divider()

# --- 4. Isi Halaman Beranda ---
if st.session_state.page == "Beranda":
    st.markdown(f"## {st.session_state.store['hero_title']}")
    
    # Box Sub-judul
    st.markdown(f"""
        <div style="background-color: #e0f2fe; padding: 20px; border-radius: 10px; border-left: 5px solid #0ea5e9;">
            {st.session_state.store['hero_subtitle']}
        </div>
        """, unsafe_allow_html=True)
    
    # Foto Banner (Jika ingin munculkan lagi di bawah)
    if os.path.exists("IMG_20251125_111048.jpg"):
        st.image("IMG_20251125_111048.jpg", use_container_width=True)
