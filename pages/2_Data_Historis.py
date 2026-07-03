import streamlit as st
import pandas as pd

from src.config import DISPLAY_NAMES, TARGET_COLUMN
from src.data_loader import filter_dataset
from src.model import train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.utils import rename_for_display
from src.visualizations import feature_importance_bar, prediction_scatter

setup_page("Data Historis")
render_header("Data Historis", "Tabel data sosio-ekonomi dan partisipasi politik dari SQLite database, filter, serta evaluasi Random Forest.")

df = load_data_from_sidebar()

if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Anda dapat mengimpor data awal dari CSV template, atau menambahkan data secara manual melalui form di bawah.")
else:
    selected_years, selected_areas = sidebar_filters(df)
    filtered_df = filter_dataset(df, selected_years, selected_areas)

    if filtered_df.empty:
        st.warning("Data kosong setelah filter.")
    else:
        keyword = st.text_input("Cari kecamatan", placeholder="Contoh: Banjarmasin Timur")
        if keyword:
            filtered_df = filtered_df[filtered_df["kecamatan"].str.contains(keyword, case=False, na=False)]

        st.markdown("### Tabel Data")
        st.dataframe(rename_for_display(filtered_df), use_container_width=True, hide_index=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download data hasil filter", data=csv, file_name="data_hasil_filter.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Evaluasi Model Random Forest")
        try:
            model_result = train_random_forest(filtered_df)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("RMSE", f"{model_result.rmse:.3f}")
            col2.metric("R²", f"{model_result.r2:.3f}")
            col3.metric("Data Training", model_result.train_size)
            col4.metric("Data Testing", model_result.test_size)

            left, right = st.columns(2)
            with left:
                st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True)
            with right:
                st.plotly_chart(prediction_scatter(model_result.prediction_result), use_container_width=True)

            st.markdown("#### Hasil Aktual vs Prediksi")
            st.dataframe(model_result.prediction_result, use_container_width=True, hide_index=True)
        except ValueError as error:
            st.warning(str(error))
