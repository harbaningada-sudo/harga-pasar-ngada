elif pilihan == "📰 Media & Berita":
        st.title("📰 Media & Berita")
        
        if df_berita.empty:
            st.info("Belum ada berita terbaru saat ini.")
        else:
            # Menampilkan dari yang terbaru (iloc[::-1])
            for _, row in df_berita.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card-container">
                        <span style="background:#EEF2FF; color:#4F46E5; padding:4px 10px; border-radius:15px; font-size:0.7rem; font-weight:bold;">
                            {row["Tipe"]}
                        </span>
                        <h3 style="margin-top:10px;">{row["Kegiatan"]}</h3>
                        <p style="color:#64748B; font-size:0.85rem;">📅 Tanggal: {row["Tanggal"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    link = str(row['Link']).strip()
                    if link.startswith("http"):
                        # Cek jika link adalah gambar
                        if any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg', '.webp']):
                            st.image(link, use_container_width=True)
                        
                        # Tombol aksi yang lebih keren
                        st.markdown(f"""
                            <a href="{link}" target="_blank" style="text-decoration:none;">
                                <div style="text-align:center; color:white; background:#059669; padding:10px; border-radius:8px; font-weight:bold; margin-bottom:20px;">
                                    🔗 Buka Tautan Detail
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                st.divider()
