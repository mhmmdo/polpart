import streamlit as st

# Mengimpor fungsi-fungsi dari folder src untuk mengambil data, mengatur tampilan, dan membuat visualisasi
from src.data_loader import filter_dataset
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters, custom_metric_card
from src.utils import format_percent, get_summary
from src.visualizations import participation_by_area, participation_trend

# Mengatur judul tab pada browser dan tampilan awal halaman
setup_page("Dashboard")

# Menampilkan judul dan deskripsi di bagian atas halaman aplikasi
render_header("Dashboard", "Ringkasan data partisipasi politik, grafik per kecamatan, dan statistik sederhana.")

# Mengambil data dari database dan menampilkannya sebagai opsi filter di sidebar
df = load_data_from_sidebar()

# Mengecek apakah database kosong (belum ada data)
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Hubungi Admin untuk mengunggah CSV data awal.")
    st.stop() # Menghentikan eksekusi kode di bawahnya jika data kosong

# Menangkap pilihan tahun dan kecamatan dari filter di sidebar (menu sebelah kiri)
selected_years, selected_areas = sidebar_filters(df)

# Menyaring (memfilter) data berdasarkan tahun dan kecamatan yang dipilih
filtered_df = filter_dataset(df, selected_years, selected_areas)

# Mengecek lagi apakah setelah difilter, datanya menjadi kosong
if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

# Mengecek apakah ada data spesifik untuk 'partisipasi_politik' (bukan NaN/kosong)
has_partisipasi = filtered_df["partisipasi_politik"].notna().any()

# Jika data partisipasi belum ada, tampilkan kotak informasi sederhana
if not has_partisipasi:
    st.warning("Data partisipasi politik belum tersedia.")
    
    col1, col2 = st.columns(2) # Membagi layar menjadi 2 kolom
    with col1:
        st.html(custom_metric_card("JUMLAH DATA", str(len(filtered_df)), "", "Data Demografi & Pemilu", "neutral"))
    with col2:
        st.html(custom_metric_card("RATA-RATA PARTISIPASI", "N/A", "", "Data belum tersedia", "down"))
else:
    # Mengambil ringkasan statistik (seperti rata-rata, nilai tertinggi/terendah)
    summary = get_summary(filtered_df)
    col1, col2, col3, col4 = st.columns(4) # Membagi layar menjadi 4 kolom untuk menampilkan metrik (kartu angka)
    with col1:
        st.html(custom_metric_card("JUMLAH DATA", str(summary["rows"]), "", "Data Demografi & Pemilu", "neutral"))
    with col2:
        st.html(custom_metric_card("RATA-RATA PARTISIPASI", format_percent(summary["average"]), "", "+2.5% dibanding target KPU", "up"))
    with col3:
        st.html(custom_metric_card("PARTISIPASI TERTINGGI", f"{summary['highest_value']:.1f}%", "", summary['highest_area'], "up"))
    with col4:
        st.html(custom_metric_card("PARTISIPASI TERENDAH", f"{summary['lowest_value']:.1f}%", "", summary['lowest_area'], "down"))

    st.markdown("---") # Membuat garis pemisah
    
    # Membuang baris data yang nilai 'partisipasi_politik'-nya kosong khusus untuk menggambar grafik
    chart_df = filtered_df.dropna(subset=["partisipasi_politik"])
    
    col_left, col_right = st.columns(2) # Membagi area grafik menjadi 2 (kiri dan kanan)
    with col_left:
        st.plotly_chart(participation_by_area(chart_df), use_container_width=True, theme=None)
    with col_right:
        st.plotly_chart(participation_trend(chart_df), use_container_width=True, theme=None)

st.markdown("---") # Membuat garis pemisah
st.markdown("### Statistik Sederhana")
# Menampilkan tabel statistik dasar (rata-rata, min, max) dari seluruh data yang berupa angka
st.dataframe(
    filtered_df.select_dtypes(include='number').describe().T,
    width="stretch",
)
