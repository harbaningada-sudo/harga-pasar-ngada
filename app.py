# --- 4. CSS OPTIMASI LOGO & FOTO (TIDAK MENUTUPI WAJAH) ---
st.markdown(f"""
    <style>
    /* Container Bingkai */
    .pimpinan-frame {{
        position: relative;
        width: 120px;
        height: 120px;
        border-radius: 15px;
        background-image: url("data:image/jpeg;base64,{img_pimpinan if img_pimpinan else ''}");
        background-size: cover;
        background-position: center;
        border: 2px solid #059669;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        overflow: hidden;
    }}

    /* Logo Ngada dibuat KECIL di Pojok Kanan Bawah */
    .logo-ngada-mini {{
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 35px; /* Diperkecil agar tidak menutupi wajah */
        height: 35px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 5px;
        padding: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .logo-ngada-mini img {{
        width: 100%;
        height: auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. UPDATE BAGIAN HEADER ---
with st.container():
    col_img, col_txt = st.columns([1, 4])
    with col_img:
        # Menampilkan Foto Pimpinan dengan Logo Kecil di Pojok
        st.markdown(f'''
            <div class="pimpinan-frame">
                <div class="logo-ngada-mini">
                    <img src="data:image/png;base64,{img_logo if img_logo else ''}">
                </div>
            </div>
        ''', unsafe_allow_html=True)
    with col_txt:
        st.markdown("<h2 style='margin:0;'>KABUPATEN NGADA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#059669; font-size:1.1rem; margin:0;'><b>Bagian Perekonomian & SDA Setda Ngada</b></p>", unsafe_allow_html=True)
