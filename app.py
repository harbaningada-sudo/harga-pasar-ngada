# --- 7. LOGIKA HALAMAN (BAGIAN HARGA YANG DIPERBAIKI) ---
store = st.session_state.store

def format_price(ini, kmrn):
    diff = ini - kmrn
    
    # Logika Warna dan Status
    if diff > 0:
        color = "#EF4444" # Merah
        status = "NAIK"
        icon = "▲"
    elif diff < 0:
        color = "#10B981" # Hijau
        status = "TURUN"
        icon = "▼"
    else:
        color = "#64748B" # Abu-abu
        status = "STABIL"
        icon = "—"
    
    return f"""
        <div style="line-height:1.2;">
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom:2px;">Hari Ini:</div>
            <div style="font-size: 1.1rem; font-weight: bold; color: #1E293B;">Rp {ini:,}</div>
            <div style="font-size: 0.75rem; color: #94A3B8; margin-top:4px;">Kemarin: Rp {kmrn:,}</div>
            <div style="margin-top: 6px; padding: 2px 6px; border-radius: 4px; background-color: {color}20; display: inline-block;">
                <span style="color:{color}; font-weight:bold; font-size: 0.75rem;">{icon} {status} (Rp {abs(diff):,})</span>
            </div>
        </div>
    """

if st.session_state.page == "Harga":
    st.markdown("### 🛍️ Pantauan Harga Komoditas")
    st.caption("Data diperbarui secara berkala berdasarkan survei di pasar.")
    
    query = st.text_input("🔍 Cari Nama Komoditas...", placeholder="Contoh: Beras, Cabai, Minyak...", label_visibility="collapsed").lower()
    
    if not df_harga.empty:
        filtered = df_harga[df_harga['KOMODITAS'].str.lower().str.contains(query)]
        
        for _, r in filtered.iterrows():
            # Cek jika ini adalah baris Kategori/Judul (Satuan 0)
            if r['SATUAN'] == 0 or str(r['SATUAN']) == "0":
                st.markdown(f"<div style='margin-top:25px; padding: 5px 0; border-bottom: 2px solid #0369a1;'><h4 style='color:#0369a1; margin:0;'>📂 {r['KOMODITAS']}</h4></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div class="flex-container" style="align-items: flex-start;">
                        <div style="flex: 1.4;">
                            <div style="font-size: 1.1rem; font-weight: bold; color: #0369a1;">{r['KOMODITAS']}</div>
                            <div style="font-size: 0.85rem; color: #64748B;">Satuan: {r['SATUAN']}</div>
                        </div>
                        <div style="flex: 1; border-left: 1px solid #F1F5F9; padding-left: 10px;">
                            <div style="font-size: 0.7rem; font-weight: bold; color: #0369a1; text-transform: uppercase; margin-bottom: 5px;">🏪 Pedagang Besar</div>
                            {format_price(r['B_INI'], r['B_KMRN'])}
                        </div>
                        <div style="flex: 1; border-left: 1px solid #F1F5F9; padding-left: 10px;">
                            <div style="font-size: 0.7rem; font-weight: bold; color: #0369a1; text-transform: uppercase; margin-bottom: 5px;">🛍️ Pedagang Kecil</div>
                            {format_price(r['K_INI'], r['K_KMRN'])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Data harga belum tersedia atau gagal memuat dari server.")
