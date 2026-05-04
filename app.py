# --- Tambahkan ini di bagian CSS (Point 3) agar logo bisa melayang di atas foto ---
st.markdown("""
    <style>
    .hero-container {
        position: relative;
        width: 100%;
    }
    .main-photo {
        width: 100%;
        border-radius: 20px;
        z-index: 1;
    }
    .floating-logo {
        position: absolute;
        top: 20px;
        left: 20px;
        width: 100px; /* Atur ukuran logo di sini */
        z-index: 2;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3));
    }
    </style>
    """, unsafe_allow_html=True)

# ... (Kode lainnya tetap sama) ...

# --- UPDATE LOGIKA HALAMAN BERANDA (Point 7) ---
elif st.session_state.page == "Beranda":
    st.subheader(store["hero_title"])
    st.info(store["hero_subtitle"])
    
    # Kontainer Foto & Logo
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    
    # Pastikan file name sesuai dengan yang ada di folder GitHub/Streamlit kamu
    foto_wabup = "IMG_20251125_111048.jpg" # Foto Wakil Bupati
    logo_kab = "logo_ngada.png" # Ganti dengan nama file logo kamu (misal: logo.png)

    # Logika Menampilkan Foto dengan Overlay Logo
    if os.path.exists(foto_wabup):
        # Jika ada logo, kita tampilkan melayang di atas foto
        if os.path.exists(logo_kab):
            with open(logo_kab, "rb") as f:
                data = f.read()
                bin_str = base64.b64encode(data).decode()
            
            # Tampilkan Logo & Foto menggunakan HTML/CSS
            st.markdown(f"""
                <div style="position: relative;">
                    <img src="data:image/png;base64,{bin_str}" class="floating-logo">
                    <img src="data:image/jpeg;base64,{base64.b64encode(open(foto_wabup, 'rb').read()).decode()}" class="main-photo">
                </div>
                """, unsafe_allow_html=True)
        else:
            # Jika logo tidak ada, tampilkan foto saja seperti biasa
            st.image(foto_wabup, use_container_width=True, caption="Wakil Bupati Ngada")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ... (Sisa kode lainnya) ...
