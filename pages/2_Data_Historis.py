import streamlit as st
import pandas as pd

from src.config import DISPLAY_NAMES, TARGET_COLUMN
from src.data_loader import filter_dataset
from src.model import train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.utils import rename_for_display
from src.visualizations import feature_importance_bar, prediction_scatter

# Konfigurasi dasar halaman
setup_page("Data Historis")
# Menampilkan judul teks besar
render_header("Data Historis", "Tabel data sosio-ekonomi dan partisipasi politik dari SQLite database, filter, serta evaluasi Random Forest.")

# Memuat data seluruhnya dari database ke dalam format tabel (DataFrame) pandas
df = load_data_from_sidebar()

# Mengecek apakah database masih kosong
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Anda dapat mengimpor data awal dari CSV template, atau menambahkan data secara manual melalui form di bawah.")
else:
    # Mengaktifkan tombol filter di sidebar
    selected_years, selected_areas = sidebar_filters(df)
    
    # Memfilter data sesuai tahun dan kecamatan yang dicentang di sidebar
    filtered_df = filter_dataset(df, selected_years, selected_areas)

    if filtered_df.empty:
        st.warning("Data kosong setelah filter.")
    else:
        # Menambahkan fitur kolom pencarian (search bar) berdasarkan nama kecamatan
        keyword = st.text_input("Cari kecamatan", placeholder="Contoh: Banjarmasin Timur")
        if keyword:
            filtered_df = filtered_df[filtered_df["kecamatan"].str.contains(keyword, case=False, na=False)]

        st.markdown("### Tabel Data")
        # Menggambar tabel di layar web dengan nama kolom yang sudah dipercantik (rename_for_display)
        st.dataframe(rename_for_display(filtered_df), width="stretch", hide_index=True)

        # Menyiapkan file untuk didownload pengguna menjadi format CSV
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download data hasil filter", data=csv, file_name="data_hasil_filter.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Evaluasi Model Random Forest")
        try:
            # Melatih ulang model Random Forest khusus dengan data yang sedang tampil/difilter
            model_result = train_random_forest(filtered_df)
            
            # Menampilkan metrik akurasi (RMSE, R2) ke dalam 4 kolom
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("RMSE", f"{model_result.rmse:.3f}") # Root Mean Square Error (makin kecil makin bagus)
            col2.metric("R²", f"{model_result.r2:.3f}") # R-squared (mendekati 1 makin bagus)
            col3.metric("Data Training", model_result.train_size) # Jumlah data untuk belajar
            col4.metric("Data Testing", model_result.test_size) # Jumlah data untuk ujian
            
            # Membagi area grafik menjadi kiri dan kanan
            left, right = st.columns(2)
            with left:
                # Menampilkan grafik batang mengenai fitur apa saja yang paling penting
                st.plotly_chart(feature_importance_bar(model_result.feature_importance), width="stretch")
            with right:
                # Menampilkan grafik scatter plot perbandingan tebakan mesin vs kunci jawaban
                st.plotly_chart(prediction_scatter(model_result.prediction_result), width="stretch")

            st.markdown("#### Hasil Aktual vs Prediksi")
            # Menampilkan tabel detail tebakan mesin satu per satu
            st.dataframe(model_result.prediction_result, width="stretch", hide_index=True)
        except ValueError as error:
            # Jika jumlah data terlalu sedikit untuk belajar, akan muncul peringatan ini
            st.warning(str(error))
