import streamlit as st

from src.ui import render_header, setup_page

# Mengatur judul halaman web
setup_page("Tentang")
# Menampilkan teks header di bagian atas
render_header("Tentang Aplikasi", "Penjelasan metode Random Forest, alur sistem, dan sumber data.")

# st.markdown digunakan untuk menuliskan teks panjang yang diformat dengan gaya markdown (seperti huruf tebal, list, dll)
st.markdown(
    """
### Metode Random Forest

Random Forest adalah metode machine learning berbasis banyak decision tree. Model ini membuat banyak pohon keputusan, lalu menggabungkan hasilnya agar prediksi lebih stabil dibanding satu pohon saja.

Pada aplikasi ini, Random Forest digunakan untuk memprediksi **tingkat partisipasi politik** pada tingkat TPS berdasarkan parameter demografi pemilu:

1. Jumlah Daftar Pemilih Tetap (DPT) TPS
2. Rasio DPT Terhadap Penduduk Kelurahan
3. Persentase Pemilih Usia 17 - 24 Tahun (Kecamatan)
4. Persentase Pemilih Usia 25 - 44 Tahun (Kecamatan)
5. Persentase Pemilih Usia 45 Tahun Keatas (Kecamatan)

### Alur Sistem

1. Pengguna membuka aplikasi Streamlit dan harus melalui halaman **Login / Register**.
2. Tersedia dua tingkat hak akses (role):
   - **Operator KPU (Admin)**: Dapat melakukan impor data baru via file CSV di sidebar.
   - **Masyarakat (User)**: Dapat melihat dashboard, visualisasi, melakukan simulasi prediksi, dan mengunduh laporan PDF.
3. Sistem membaca dataset dari **database SQLite (polpart.db)** melalui VIEW `dataset_final`.
4. Data ditampilkan pada dashboard dan tabel historis.
5. Sistem melatih model Random Forest menggunakan data historis tingkat TPS dari database secara otomatis.
6. Pengguna mengisi form input variabel pada menu Prediksi.
7. Sistem menampilkan hasil prediksi partisipasi politik, **menyediakan opsi Unduh Laporan PDF**, dan **menyimpan riwayat hasil prediksi ke database**.
8. Sistem menampilkan evaluasi model seperti RMSE, R², dan Feature Importance.
9. Halaman Visualisasi menampilkan heatmap korelasi, grafik tren & perbandingan, serta peta choropleth menggunakan Plotly + GeoJSON.

### Sumber Data yang Digunakan

- **Socio-Economic & Demography**: Badan Pusat Statistik (BPS) Kota Banjarmasin dan Dinas Kependudukan dan Pencatatan Sipil.
- **Partisipasi Politik**: Komisi Pemilihan Umum (KPU) Kota Banjarmasin (Data riil 1.838 baris TPS tahun 2024).
- **Batas Wilayah Geografis**: File GeoJSON kecamatan Banjarmasin (`kecamatan_5.geojson`).

### Struktur Database SQLite

Database lokal tersimpan di `database/polpart.db` dengan tabel-tabel utama:
- `kecamatan`: Daftar wilayah administratif kecamatan.
- `pengguna`: Menyimpan username, password (hash SHA-256), dan role (admin/user) untuk autentikasi masuk.
- `data_partisipasi_tps`: Data tingkat TPS meliputi DPT, pengguna hak pilih, partisipasi, dan rasio kependudukan.
- `hasil_prediksi`: Log input formulir prediksi dan hasil output model.
- `model_evaluasi`: Riwayat skor performa model (RMSE, R²).
"""
)
