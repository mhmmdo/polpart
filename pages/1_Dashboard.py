import streamlit as st

from src.data_loader import filter_dataset
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.utils import format_percent, get_summary
from src.visualizations import participation_by_area, participation_trend

setup_page("Dashboard")
render_header("Dashboard", "Ringkasan data partisipasi politik, grafik per kecamatan, dan statistik sederhana.")

df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan jalankan `python scripts/init_db.py` dan `python scripts/import_csv_to_sqlite.py` untuk menginisialisasi database dan mengimpor data awal.")
    st.stop()

selected_years, selected_areas = sidebar_filters(df)
filtered_df = filter_dataset(df, selected_years, selected_areas)

if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

summary = get_summary(filtered_df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Data", summary["rows"])
col2.metric("Rata-rata Partisipasi", format_percent(summary["average"]))
col3.metric("Tertinggi", f"{summary['highest_area']} ({summary['highest_value']:.1f}%)")
col4.metric("Terendah", f"{summary['lowest_area']} ({summary['lowest_value']:.1f}%)")

st.markdown("---")
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(participation_by_area(filtered_df), use_container_width=True)
with col_right:
    st.plotly_chart(participation_trend(filtered_df), use_container_width=True)

st.markdown("### Statistik Sederhana")
st.dataframe(
    filtered_df.select_dtypes(include='number').describe().T,
    use_container_width=True,
)
