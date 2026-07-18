import streamlit as st

from src.ui import render_header, setup_page

# Mengatur judul halaman web
setup_page("Tentang")
render_header("Tentang Aplikasi", "Penjelasan metode Random Forest, alur sistem, dan sumber data.")

st.markdown(
    """
### Metode Random Forest

Random Forest adalah metode machine learning berbasis banyak decision tree. Model ini membuat banyak pohon keputusan, lalu menggabungkan hasilnya agar prediksi lebih stabil dibanding satu pohon saja.

Pada aplikasi ini, Random Forest digunakan sebagai **regressor** untuk memprediksi **tingkat partisipasi politik** pada tingkat TPS berdasarkan 9 parameter demografi dan sosio-ekonomi pemilu:

1. Jumlah Daftar Pemilih Tetap (DPT) TPS
2. Rasio DPT Terhadap Penduduk Kelurahan
3. Pendapatan Per Kapita Kelurahan (Rp)
4. Tingkat Pengangguran Kecamatan (%)
5. Kepadatan Penduduk (jiwa/km²)
6. Indeks Pembangunan Manusia (IPM) Kecamatan
7. Persentase Pemilih Usia 17 - 24 Tahun (Kecamatan)
8. Persentase Pemilih Usia 25 - 44 Tahun (Kecamatan)
9. Persentase Pemilih Usia 45 Tahun Keatas (Kecamatan)

### Konsep Data Pemilu

Untuk menjamin kualitas model dan keakuratan analisis, sistem membagi data secara logis:
- **Data Pemilu Tingkat TPS**: Digunakan sebagai data untuk melatih (*training*), menguji (*testing*), dan memprediksi persentase partisipasi politik menggunakan algoritma Random Forest secara dinamis berdasarkan tahun pemilu terpilih.
- **Data Pemilu Tingkat Agregat**: Digunakan sebagai data historis pembanding per kecamatan untuk melihat tren kenaikan/penurunan tingkat partisipasi dari tahun ke tahun.

### Evaluasi Model Regresi
Karena model yang digunakan memprediksi nilai kontinu (persentase partisipasi politik), maka evaluasi kinerja model diukur menggunakan metrik regresi standar:
* **Root Mean Squared Error (RMSE)**: Mengukur akar dari rata-rata kuadrat selisih prediksi dengan nilai aktual. Semakin kecil nilainya, semakin akurat modelnya.
* **Mean Absolute Error (MAE)**: Rata-rata absolut dari selisih antara nilai prediksi dan aktual. MAE memberikan gambaran deviasi error rata-rata dalam satuan persen yang mudah dipahami.
* **R² Score (Koefisien Determinasi)**: Mengukur seberapa baik variasi nilai target dapat dijelaskan oleh 9 fitur input. Sempurna jika bernilai 1.0 (100%).

### Alur Sistem

1. Pengguna membuka aplikasi Streamlit dan harus melalui halaman **Login / Register**.
2. Tersedia dua tingkat hak akses (role):
   - **Operator KPU (Admin)**: Dapat melakukan impor data baru via file CSV, serta mengelola data partai dan data TPS (CRUD) pada menu Kelola Data.
   - **Masyarakat (User)**: Dapat melihat dashboard, visualisasi, melakukan simulasi prediksi, dan mengunduh laporan PDF.
3. Sistem membaca dataset dari **database SQLite (polpart.db)** melalui VIEW `dataset_final`.
4. Data ditampilkan pada dashboard dan tabel historis.
5. Sistem melatih model Random Forest menggunakan data tingkat TPS dari database secara otomatis berdasarkan tahun pemilu terpilih.
6. Pengguna memilih Kecamatan, Kelurahan, dan TPS pada menu Prediksi untuk memuat parameter secara otomatis.
7. Sistem menampilkan hasil prediksi partisipasi politik, **menyediakan opsi Unduh Laporan PDF**, dan **menyimpan riwayat hasil prediksi ke database**.
8. Sistem menampilkan evaluasi model seperti RMSE, MAE, R², dan Feature Importance.
9. Halaman Visualisasi menampilkan heatmap korelasi, grafik tren & perbandingan, serta peta choropleth menggunakan Plotly + GeoJSON.

### Sumber Data yang Digunakan

- **Demografi & Sosio-Ekonomi**: Badan Pusat Statistik (BPS) Kota Banjarmasin dan Dinas Kependudukan dan Pencatatan Sipil.
- **Partisipasi Politik**: Komisi Pemilihan Umum (KPU) Kota Banjarmasin (Data riil tingkat TPS & Data agregat dapil).
- **Batas Wilayah Geografis**: File GeoJSON kecamatan Banjarmasin (`kecamatan_5.geojson`).
"""
)
