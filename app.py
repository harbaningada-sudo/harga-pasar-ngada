# --- 3. HELPER GAMBAR (OPTIMASI) ---
def get_img_as_base64(file):
    try:
        if os.path.exists(file):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

# Pastikan nama file ini sesuai dengan yang ada di GitHub kamu
img_pimpinan = get_img_as_base64("Bupati-dan-Wakil-Bupati-Ngada-jpg.jpeg")
logo_ngada = get_img_as_base64("logo-ngada.png")

# --- 4. CSS KHUSUS LOGO & FOTO (TANPA MERUBAH LAINNYA) ---
st.markdown(f"""
    <style>
    /* Container Header Visual */
    .pimpinan-container {{
        position: relative;
        width: 120px;
        height: 120px;
        margin-bottom: 10px;
    }}

    /* Foto Bupati sebagai Background Bulat/Rounded */
    .pimpinan-bg {{
        width: 100%;
        height: 100%;
        background-image: url("data:image/jpeg;base64,{img_pimpinan if img_pimpinan else ''}");
        background-size: cover;
        background-position: center;
        border-radius: 15px; /* Box rounded elegan */
        border: 2px solid #059669;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: absolute;
        top: 0;
        left: 0;
    }}

    /* Logo Ngada di Tengah dengan Overlay Putih */
    .logo-overlay-center {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 55px;
        height: 55px;
        background: rgba(255, 255, 255, 0.9); /* Putih transparan agar logo jelas */
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        padding: 5px;
    }}
    
    .logo-overlay-center img {{
        width: 40px;
        height: auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. UPDATE BAGIAN HEADER (HANYA BAGIAN VISUAL) ---
with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        # Menampilkan kombinasi Foto + Logo
        st.markdown(f'''
            <div class="pimpinan-container">
                <div class="pimpinan-bg"></div>
                <div class="logo-overlay-center">
                    <img src="data:image/png;base64,{logo_ngada if logo_ngada else ''}">
                </div>
            </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown("<h2 style='margin-bottom:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.2rem; color:#059669; margin-top:0;'><b>Bagian Perekonomian & SDA Setda Ngada</b></p>", unsafe_allow_html=True)
