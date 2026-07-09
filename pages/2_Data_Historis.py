import streamlit as st
import pandas as pd

from src.config import DISPLAY_NAMES, TARGET_COLUMN
from src.data_loader import filter_dataset
from src.model import train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page
from src.utils import rename_for_display
from src.visualizations import feature_importance_bar, prediction_scatter

# Konfigurasi dasar halaman
setup_page("Data Historis")
render_header("Data Historis", "Tabel data partisipasi politik pemilu dari database SQLite, penyaringan data, dan evaluasi model Random Forest.")

# Memuat data 2024 tingkat TPS
df_2024 = load_data_from_sidebar()

if df_2024.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan hubungi Admin.")
else:
    # Membuat dua tab data historis
    tab2024, tab2019 = st.tabs(["Data TPS 2024", "Data Agregat 2019"])
    
    with tab2024:
        st.markdown("### Penyaringan Data TPS 2024")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            kec_list = ["Semua"] + sorted(df_2024["kecamatan"].dropna().unique().tolist())
            sel_kec = st.selectbox("Pilih Kecamatan", kec_list, key="sel_kec_2024")
        with col_f2:
            if sel_kec != "Semua":
                kel_list = ["Semua"] + sorted(df_2024[df_2024["kecamatan"] == sel_kec]["kelurahan"].dropna().unique().tolist())
            else:
                kel_list = ["Semua"] + sorted(df_2024["kelurahan"].dropna().unique().tolist())
            sel_kel = st.selectbox("Pilih Kelurahan", kel_list, key="sel_kel_2024")
            
        filtered_2024 = df_2024.copy()
        if sel_kec != "Semua":
            filtered_2024 = filtered_2024[filtered_2024["kecamatan"] == sel_kec]
        if sel_kel != "Semua":
            filtered_2024 = filtered_2024[filtered_2024["kelurahan"] == sel_kel]
            
        keyword = st.text_input("Cari kata kunci (Nomor TPS / Kelurahan / Kecamatan)", placeholder="Contoh: 001 atau Basirih", key="search_2024")
        if keyword:
            filtered_2024 = filtered_2024[
                filtered_2024["kecamatan"].str.contains(keyword, case=False, na=False) |
                filtered_2024["kelurahan"].str.contains(keyword, case=False, na=False) |
                filtered_2024["no_tps"].astype(str).str.contains(keyword, case=False, na=False)
            ]
            
        st.markdown("#### Tabel Data TPS 2024")
        st.dataframe(rename_for_display(filtered_2024), use_container_width=True, hide_index=True)
        
        csv_2024 = filtered_2024.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data 2024 (CSV)", data=csv_2024, file_name="data_tps_2024.csv", mime="text/csv", key="dl_2024", use_container_width=True)
        
    with tab2019:
        st.info("Catatan: Data Pemilu 2019 merupakan data agregat dapil/kecamatan yang digunakan murni sebagai data historis/perbandingan dan tidak dimasukkan ke dalam pelatihan model Random Forest.")
        
        from src.data_loader import load_dataset_2019
        df_2019 = load_dataset_2019()
        
        if df_2019.empty:
            st.warning("Data Pemilu 2019 tidak tersedia di database.")
        else:
            col_f19_1, col_f19_2 = st.columns(2)
            with col_f19_1:
                dapil_list = ["Semua"] + sorted(df_2019["dapil"].dropna().unique().tolist())
                sel_dapil = st.selectbox("Pilih Dapil Pemilu 2019", dapil_list, key="sel_dapil_2019")
            with col_f19_2:
                if sel_dapil != "Semua":
                    kec_19_list = ["Semua"] + sorted(df_2019[df_2019["dapil"] == sel_dapil]["kecamatan"].dropna().unique().tolist())
                else:
                    kec_19_list = ["Semua"] + sorted(df_2019["kecamatan"].dropna().unique().tolist())
                sel_kec_19 = st.selectbox("Pilih Kecamatan Pemilu 2019", kec_19_list, key="sel_kec_19")
                
            filtered_2019 = df_2019.copy()
            if sel_dapil != "Semua":
                filtered_2019 = filtered_2019[filtered_2019["dapil"] == sel_dapil]
            if sel_kec_19 != "Semua":
                filtered_2019 = filtered_2019[filtered_2019["kecamatan"] == sel_kec_19]
                
            st.markdown("#### Tabel Data Agregat 2019")
            st.dataframe(filtered_2019, use_container_width=True, hide_index=True)
            
            csv_2019 = filtered_2019.to_csv(index=False).encode("utf-8")
            st.download_button("Download Data 2019 (CSV)", data=csv_2019, file_name="data_agregat_2019.csv", mime="text/csv", key="dl_2019", use_container_width=True)

    st.markdown("---")
    st.markdown("### Evaluasi Model Random Forest (Data TPS 2024)")
    try:
        # Melatih ulang model Random Forest khusus dengan data 2024
        model_result = train_random_forest(df_2024)
        
        # Menampilkan metrik akurasi (RMSE, MAE, R2) ke dalam 5 kolom
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("RMSE", f"{model_result.rmse:.4f}")
        col2.metric("MAE", f"{model_result.mae:.4f}")
        col3.metric("R² Score", f"{model_result.r2:.4f} ({model_result.r2*100:.1f}%)")
        col4.metric("Data Training", model_result.train_size)
        col5.metric("Data Testing", model_result.test_size)
        
        # Membagi area grafik menjadi kiri dan kanan
        left, right = st.columns(2)
        with left:
            st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True, theme=None)
        with right:
            st.plotly_chart(prediction_scatter(model_result.prediction_result), use_container_width=True, theme=None)

        st.markdown("#### Hasil Aktual vs Prediksi")
        st.dataframe(model_result.prediction_result, use_container_width=True, hide_index=True)
    except ValueError as error:
        st.warning(str(error))
