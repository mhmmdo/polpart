import streamlit as st

from src.data_loader import filter_dataset, load_geojson, get_comparison_2019_2024
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.visualizations import (
    correlation_heatmap,
    participation_map,
    participation_by_area,
    participation_comparison_chart,
    feature_importance_bar,
    prediction_scatter
)
from src.model import train_random_forest

setup_page("Visualisasi")
render_header("Visualisasi", "Grafik korelasi, peta spasial, perbandingan historis, dan evaluasi model Random Forest.")

# Memuat data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Hubungi Admin untuk mengunggah CSV data awal.")
    st.stop()

# Menampilkan tombol centang kecamatan dan tahun di sidebar
selected_years, selected_areas = sidebar_filters(df)
# Menyaring data sesuai centang
filtered_df = filter_dataset(df, selected_years, selected_areas)

if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

# 1. Menampilkan Peta Panas (Heatmap Korelasi)
st.markdown("### Korelasi Variabel Demografi & Partisipasi Politik")
st.plotly_chart(correlation_heatmap(filtered_df), use_container_width=True, theme=None)
st.caption("Matriks korelasi Pearson menunjukkan arah dan kekuatan hubungan linier antara 9 fitur demografi dengan persentase partisipasi politik.")

# Buang data partisipasi yang kosong/NaN agar tidak error saat digambar grafiknya
chart_df = filtered_df.dropna(subset=["partisipasi_politik"])

if chart_df.empty:
    st.warning("Data partisipasi politik belum tersedia.")
else:
    # 2. Menampilkan grafik batang rata-rata partisipasi per kecamatan
    st.markdown("---")
    st.markdown("### Rata-rata Partisipasi Politik Pemilu 2024 per Kecamatan")
    st.plotly_chart(participation_by_area(chart_df), use_container_width=True, theme=None)

    # 3. Menampilkan grafik perbandingan historis 2019 vs 2024
    st.markdown("---")
    st.markdown("### Grafik Perbandingan Historis (Pemilu 2019 vs Pemilu 2024)")
    comp_df = get_comparison_2019_2024()
    st.plotly_chart(participation_comparison_chart(comp_df), use_container_width=True, theme=None)

    # 4. Menampilkan Peta Partisipasi Politik
    st.markdown("---")
    st.markdown("### Peta Partisipasi Politik")
    years = sorted(chart_df["tahun"].dropna().astype(int).unique().tolist())
    if not years:
        st.warning("Data partisipasi politik untuk peta belum tersedia.")
    else:
        selected_map_year = st.selectbox("Pilih tahun peta", years, index=len(years) - 1)
        try:
            geojson = load_geojson()
            st.plotly_chart(participation_map(chart_df, geojson, selected_map_year), use_container_width=True, theme=None)
            st.caption("Peta spasial di atas mengagregasikan data TPS pemilu 2024 ke tingkat kecamatan secara dinamis agar sesuai dengan batas wilayah GeoJSON.")
        except Exception as error:
            st.warning(f"Peta gagal dimuat: {error}")

    # 5. Evaluasi Model Random Forest
    st.markdown("---")
    st.markdown("### Evaluasi Model Random Forest (Data TPS 2024)")
    try:
        model_result = train_random_forest(df)
        
        left, right = st.columns(2)
        with left:
            st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True, theme=None)
        with right:
            st.plotly_chart(prediction_scatter(model_result.prediction_result), use_container_width=True, theme=None)
    except Exception as e:
        st.warning(f"Evaluasi model gagal dimuat: {e}")
