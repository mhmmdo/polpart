import streamlit as st

from src.data_loader import filter_dataset, load_geojson
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.visualizations import correlation_heatmap, participation_map, participation_by_area, participation_trend

setup_page("Visualisasi")
render_header("Visualisasi", "Grafik korelasi, tren partisipasi, dan peta sederhana berbasis GeoJSON.")

df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan jalankan `python scripts/init_db.py` dan `python scripts/import_csv_to_sqlite.py` untuk menginisialisasi database dan mengimpor data awal.")
    st.stop()

selected_years, selected_areas = sidebar_filters(df)
filtered_df = filter_dataset(df, selected_years, selected_areas)

if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

st.plotly_chart(correlation_heatmap(filtered_df), use_container_width=True)

# Filter data to only include non-empty political participation values for the charts and map
chart_df = filtered_df.dropna(subset=["partisipasi_politik"])

if chart_df.empty:
    st.warning("Data partisipasi politik belum tersedia.")
else:
    st.plotly_chart(participation_by_area(chart_df), use_container_width=True)
    st.plotly_chart(participation_trend(chart_df), use_container_width=True)

    st.markdown("---")
    st.markdown("### Peta Partisipasi Politik")
    years = sorted(chart_df["tahun"].dropna().astype(int).unique().tolist())
    if not years:
        st.warning("Data partisipasi politik untuk peta belum tersedia.")
    else:
        selected_map_year = st.selectbox("Pilih tahun peta", years, index=len(years) - 1)
        try:
            geojson = load_geojson()
            st.plotly_chart(participation_map(chart_df, geojson, selected_map_year), use_container_width=True)
            st.caption("Batas wilayah kecamatan pada peta ini menggunakan koordinat simplifikasi sebagai contoh. Silakan ganti dengan file GeoJSON batas wilayah resmi untuk visualisasi geografis yang presisi.")
        except Exception as error:
            st.warning(f"Peta gagal dimuat: {error}")
