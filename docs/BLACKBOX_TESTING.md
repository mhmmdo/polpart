# Pengujian Black Box: Validasi Fungsionalitas Sistem

Pengujian Black Box digunakan untuk memvalidasi fungsionalitas antarmuka dan integrasi database SQLite pada Sistem Prediksi Partisipasi Politik. Hasil pengujian menunjukkan seluruh fitur utama berjalan sesuai harapan.

---

## Tabel Hasil Pengujian Black Box

| No | Fitur | Skenario Pengujian | Hasil yang Diharapkan | Status |
| :--- | :--- | :--- | :--- | :---: |
| 1 | Dashboard Ringkasan | Membuka halaman Dashboard setelah data diimpor ke database SQLite | Metrik kartu menampilkan jumlah data, rata-rata, tertinggi, dan terendah secara akurat | Berhasil |
| 2 | Data Historis SQLite | Mengakses halaman Data Historis | Sistem memuat seluruh dataset dari VIEW `dataset_final` ke dalam tabel Streamlit | Berhasil |
| 3 | Filter Tahun | Memilih tahun tertentu pada filter multiselect di sidebar | Tabel historis dan dashboard menyaring data hanya untuk tahun terpilih | Berhasil |
| 4 | Filter Kecamatan | Memilih nama kecamatan pada filter multiselect di sidebar | Tabel historis dan dashboard menyaring data hanya untuk kecamatan terpilih | Berhasil |
| 5 | Impor CSV ke SQLite | Menjalankan perintah terminal `python scripts/import_csv_to_sqlite.py` dengan berkas CSV yang benar | Data berhasil ditransfer ke database SQLite dan menampilkan pesan jumlah baris sukses | Berhasil |
| 6 | Proteksi Kolom Impor | Menjalankan skrip impor CSV dengan berkas yang kolom wajibnya (`tahun` atau `kecamatan`) salah/tidak ada | Sistem menampilkan pesan error spesifik dan membatalkan proses impor data | Berhasil |
| 7 | Prediksi Random Forest | Mengisi formulir indikator sosio-ekonomi secara lengkap dan menekan tombol "Prediksi" | Sistem menampilkan persentase estimasi partisipasi politik dalam kartu khusus | Berhasil |
| 8 | Validasi Data Minim | Melatih model menggunakan total baris dataset bersih yang kurang dari 8 baris | Sistem menampilkan pesan warning bahwa data tidak cukup untuk menghasilkan model valid | Berhasil |
| 9 | Tampilan Metrik Akurasi | Membuka bagian evaluasi model di halaman Data Historis/Prediksi | Angka RMSE dan koefisien determinasi R² terhitung dan ditampilkan dengan benar | Berhasil |
| 10| Feature Importance | Mengakses halaman Prediksi atau Data Historis | Menampilkan grafik plotly horizontal pentingnya variabel kontributor model | Berhasil |
| 11| Visualisasi Korelasi | Membuka halaman Visualisasi | Grafik korelasi berbentuk heatmap antar-variabel ter-render secara lengkap | Berhasil |
| 12| Peta GeoJSON | Membuka halaman Visualisasi bagian Peta Partisipasi Politik | Peta choropleth interaktif kecamatan ter-render dan warna gradasi terisi sesuai data | Berhasil |
| 13| Halaman Tentang | Mengklik menu Tentang Aplikasi pada navigasi | Menampilkan informasi penjelasan alur sistem, metode Random Forest, dan rancangan database | Berhasil |
| 14| Log Riwayat Prediksi | Menjalankan fitur prediksi lalu melihat tabel Riwayat Prediksi di bagian bawah | Parameter input beserta nilai persentase estimasi hasil prediksi tersimpan ke SQLite dan muncul di tabel | Berhasil |
| 15| Upload CSV via Sidebar | Unggah file CSV melalui sidebar uploader | Data di-upsert ke SQLite, uploader di-reset, muncul pesan sukses, data baru muncul di tabel | Berhasil |
| 16| Filter & Download | Gunakan filter tahun/kecamatan lalu klik tombol download CSV | File CSV terdownload sesuai hasil filter yang aktif | Berhasil |
