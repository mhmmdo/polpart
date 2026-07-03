import streamlit as st

from src.ui import render_header, setup_page

setup_page("Tentang")
render_header("Tentang Aplikasi", "Penjelasan metode Random Forest, alur sistem, dan sumber data.")

st.markdown(
    """
### Metode Random Forest

Random Forest adalah metode machine learning berbasis banyak decision tree. Model ini membuat banyak pohon keputusan, lalu menggabungkan hasilnya agar prediksi lebih stabil dibanding satu pohon saja.

Pada aplikasi ini, Random Forest digunakan untuk memprediksi **tingkat partisipasi politik** berdasarkan variabel sosio-ekonomi:

1. Tingkat pendidikan
2. Pendapatan per kapita
3. Tingkat pengangguran
4. Kepadatan penduduk
5. Indeks Pembangunan Manusia (IPM)

### Alur Sistem

1. Pengguna membuka aplikasi Streamlit.
2. Sistem membaca dataset dari **database SQLite (polpart.db)** melalui VIEW `dataset_final`.
3. Data ditampilkan pada dashboard dan tabel historis.
4. Sistem melatih model Random Forest menggunakan data historis dari database.
5. Pengguna mengisi form input variabel pada menu Prediksi.
6. Sistem menampilkan hasil prediksi partisipasi politik dan **menyimpan riwayat hasil prediksi ke database**.
7. Sistem menampilkan evaluasi model seperti RMSE, R², dan Feature Importance, serta menyimpan log evaluasi ke database.
8. Halaman Visualisasi memetakan tingkat partisipasi politik menggunakan file GeoJSON yang dicocokkan dengan nama kecamatan dari database.

### Sumber Data yang Digunakan

- **Socio-Economic & Demography**: Badan Pusat Statistik (BPS) Kota Banjarmasin dan Data Agregat Kependudukan (DAK) Dinas Kependudukan dan Pencatatan Sipil.
- **Partisipasi Politik**: Komisi Pemilihan Umum (KPU) Kota Banjarmasin.
- **Batas Wilayah Geografis**: File GeoJSON kecamatan Banjarmasin (`kecamatan_5.geojson`).

### Struktur Database SQLite

Database lokal tersimpan di `database/polpart.db` dengan tabel-tabel utama:
- `kecamatan`: Daftar wilayah administratif kecamatan.
- `data_sosio_ekonomi`: Data indikator pembangunan dan demografi per kecamatan per tahun.
- `data_partisipasi_politik`: Data tingkat DPT, pengguna hak pilih, dan persentase partisipasi per kecamatan per tahun.
- `hasil_prediksi`: Log input formulir dan hasil prediksi model.
- `model_evaluasi`: Riwayat skor performa model (RMSE, R²).

### Catatan Penting

Dataset bawaan aplikasi ini merupakan data simulasi/template untuk tujuan demonstrasi sistem. Untuk analisis akademik, laporan resmi, atau pengambilan kebijakan, Anda dapat menambahkan data valid secara dinamis melalui form input di halaman **Data Historis**.
"""
)
