import streamlit as st

from src.data_loader import filter_dataset
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters, custom_metric_card
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

# Check if there is any political participation data
has_partisipasi = filtered_df["partisipasi_politik"].notna().any()

if not has_partisipasi:
    st.warning("Data partisipasi politik belum tersedia.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.html(custom_metric_card("JUMLAH DATA", str(len(filtered_df)), "", "Data Sosio-Ekonomi", "neutral"))
    with col2:
        st.html(custom_metric_card("RATA-RATA PARTISIPASI", "N/A", "", "Data belum tersedia", "down"))
else:
    # Get summary safely
    summary = get_summary(filtered_df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.html(custom_metric_card("JUMLAH DATA", str(summary["rows"]), "", "Data Sosio-Ekonomi & Pemilu", "neutral"))
    with col2:
        st.html(custom_metric_card("RATA-RATA PARTISIPASI", format_percent(summary["average"]), "", "+2.5% dibanding target KPU", "up"))
    with col3:
        st.html(custom_metric_card("PARTISIPASI TERTINGGI", f"{summary['highest_value']:.1f}%", "", summary['highest_area'], "up"))
    with col4:
        st.html(custom_metric_card("PARTISIPASI TERENDAH", f"{summary['lowest_value']:.1f}%", "", summary['lowest_area'], "down"))

    st.markdown("---")
    # For political participation charts, filter out empty rows
    chart_df = filtered_df.dropna(subset=["partisipasi_politik"])
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(participation_by_area(chart_df), use_container_width=True, theme=None)
    with col_right:
        st.plotly_chart(participation_trend(chart_df), use_container_width=True, theme=None)

st.markdown("---")
st.markdown("### Statistik Sederhana")
st.dataframe(
    filtered_df.select_dtypes(include='number').describe().T,
    use_container_width=True,
)
