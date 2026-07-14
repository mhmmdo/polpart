import streamlit as st
import pandas as pd

from src.ui import load_data_from_sidebar, render_header, setup_page
from src.utils import rename_for_display

# Konfigurasi dasar halaman
setup_page("Data Historis")
render_header("Data Historis", "Tabel data partisipasi politik pemilih per TPS KPU Kota Banjarmasin.")

# Memuat data tingkat TPS (seluruh tahun)
df = load_data_from_sidebar()

if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan hubungi Admin.")
else:
    # Filter Tahun, Kecamatan & Kelurahan di halaman utama secara sejajar
    col_yr, col_f1, col_f2 = st.columns(3)
    
    with col_yr:
        years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
        default_index = years.index(2024) if 2024 in years else len(years) - 1
        active_year = st.selectbox("Pilih Tahun Pemilu", years, index=default_index, key="sel_tahun_historis")
        
    df_active = df[df["tahun"] == active_year]
    
    with col_f1:
        kec_list = ["Semua"] + sorted(df_active["kecamatan"].dropna().unique().tolist())
        sel_kec = st.selectbox("Pilih Kecamatan", kec_list, key="sel_kec_historis")
        
    with col_f2:
        if sel_kec != "Semua":
            kel_list = ["Semua"] + sorted(df_active[df_active["kecamatan"] == sel_kec]["kelurahan"].dropna().unique().tolist())
        else:
            kel_list = ["Semua"] + sorted(df_active["kelurahan"].dropna().unique().tolist())
        sel_kel = st.selectbox("Pilih Kelurahan", kel_list, key="sel_kel_historis")
        
    # Terapkan penyaringan
    filtered_df = df_active.copy()
    if sel_kec != "Semua":
        filtered_df = filtered_df[filtered_df["kecamatan"] == sel_kec]
    if sel_kel != "Semua":
        filtered_df = filtered_df[filtered_df["kelurahan"] == sel_kel]
        
    # Input Pencarian
    keyword = st.text_input("Cari kata kunci (Nomor TPS / Kelurahan / Kecamatan)", placeholder="Contoh: 001 atau Basirih", key="search_historis")
    
    if keyword:
        q_clean = keyword.strip()
        if q_clean.isdigit():
            # Fix Bug: Pencarian Angka (Nomor TPS) harus eksak agar "1" tidak memunculkan "11, 21, 31"
            val_exact = q_clean
            val_padded = q_clean.zfill(3)
            filtered_df = filtered_df[
                filtered_df["kecamatan"].str.contains(q_clean, case=False, na=False) |
                filtered_df["kelurahan"].str.contains(q_clean, case=False, na=False) |
                (filtered_df["no_tps"] == val_exact) |
                (filtered_df["no_tps"] == val_padded)
            ]
        else:
            # Pencarian teks biasa menggunakan substring contains
            filtered_df = filtered_df[
                filtered_df["kecamatan"].str.contains(q_clean, case=False, na=False) |
                filtered_df["kelurahan"].str.contains(q_clean, case=False, na=False) |
                filtered_df["no_tps"].str.contains(q_clean, case=False, na=False)
            ]
            
    # Tampilkan Data Grid
    st.dataframe(rename_for_display(filtered_df), use_container_width=True, hide_index=True)
    
    # Download Button
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data TPS (CSV)", 
        data=csv_bytes, 
        file_name=f"data_tps_pemilu_{active_year}.csv", 
        mime="text/csv", 
        use_container_width=True
    )
