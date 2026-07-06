import streamlit as st

from src.data_loader import filter_dataset, load_geojson
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.visualizations import correlation_heatmap, participation_map, participation_by_area, participation_trend

setup_page("Visualisasi")
render_header("Visualisasi", "Grafik korelasi, tren partisipasi, dan peta sederhana berbasis GeoJSON.")

# Memuat data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan jalankan `python scripts/init_db.py` dan `python scripts/import_csv_to_sqlite.py` untuk menginisialisasi database dan mengimpor data awal.")
    st.stop()

# Menampilkan tombol centang kecamatan dan tahun di sidebar
selected_years, selected_areas = sidebar_filters(df)
# Menyaring data sesuai centang
filtered_df = filter_dataset(df, selected_years, selected_areas)

if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

# 1. Menampilkan Peta Panas (Heatmap)
# Grafik ini melihat hubungan antar-variabel. Jika warnanya terang/nilainya mendekati 1, berarti hubungannya kuat.
st.plotly_chart(correlation_heatmap(filtered_df), width="stretch")

# Buang data partisipasi yang kosong/NaN agar tidak error saat digambar grafiknya
chart_df = filtered_df.dropna(subset=["partisipasi_politik"])

if chart_df.empty:
    st.warning("Data partisipasi politik belum tersedia.")
else:
    # 2. Menampilkan grafik batang partisipasi tiap kecamatan
    st.plotly_chart(participation_by_area(chart_df), width="stretch")
    # 3. Menampilkan grafik tren (garis naik-turun) per tahun
    st.plotly_chart(participation_trend(chart_df), width="stretch")

    st.markdown("---")
    st.markdown("### Peta Partisipasi Politik")
    # Mengurutkan tahun dari yang terkecil sampai terbesar untuk peta
    years = sorted(chart_df["tahun"].dropna().astype(int).unique().tolist())
    if not years:
        st.warning("Data partisipasi politik untuk peta belum tersedia.")
    else:
        # Menampilkan dropdown pilihan tahun khusus untuk peta, defaultnya tahun paling terakhir (paling baru)
        selected_map_year = st.selectbox("Pilih tahun peta", years, index=len(years) - 1)
        try:
            # Membaca data GeoJSON (File koordinat dan garis batas kecamatan)
            geojson = load_geojson()
            # 4. Menggambar peta geospasial berwarna dengan Plotly (Choropleth Map)
            st.plotly_chart(participation_map(chart_df, geojson, selected_map_year), width="stretch")
            st.caption("Batas wilayah kecamatan pada peta ini menggunakan koordinat simplifikasi sebagai contoh. Silakan ganti dengan file GeoJSON batas wilayah resmi untuk visualisasi geografis yang presisi.")
        except Exception as error:
            st.warning(f"Peta gagal dimuat: {error}")
