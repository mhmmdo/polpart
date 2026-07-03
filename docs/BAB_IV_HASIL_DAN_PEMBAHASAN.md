# BAB IV: HASIL DAN PEMBAHASAN

## 4.1 Implementasi Sistem
Sistem Prediksi Partisipasi Politik diimplementasikan menggunakan bahasa pemrograman Python dengan memanfaatkan framework Streamlit untuk antarmuka pengguna web. Database utama menggunakan SQLite (`database/polpart.db`) yang dikonfigurasi secara lokal.

### 4.1.1 Implementasi Halaman Dashboard
Halaman Dashboard berfungsi sebagai halaman utama aplikasi (`pages/1_Dashboard.py`). Halaman ini memuat data dari database SQLite melalui VIEW `dataset_final`. Fitur yang terimplementasi meliputi:
- Pemfilteran data menggunakan widget sidebar (`multiselect` tahun dan kecamatan).
- Kartu metrik dinamis yang menampilkan jumlah baris data, rata-rata partisipasi politik, serta kecamatan dengan partisipasi tertinggi dan terendah berdasarkan hasil filter.
- Grafik visualisasi berupa grafik batang (bar chart) rata-rata partisipasi per kecamatan dan grafik garis (line chart) tren partisipasi tahunan.
- Tabel ringkasan statistik sederhana menggunakan fungsi deskriptif data numerik (`pandas.DataFrame.describe()`).
- Penanganan basis data kosong: jika database belum diinisialisasi atau data kosong, sistem menampilkan peringatan berwarna kuning (`st.warning`) berisi panduan pengisian data awal dan menghentikan eksekusi halaman secara aman.

### 4.1.2 Implementasi Halaman Data Historis
Halaman Data Historis (`pages/2_Data_Historis.py`) menyajikan antarmuka pengolahan data masa lalu dan evaluasi performa model:
- Menampilkan tabel representasi data dari VIEW `dataset_final` dengan penamaan kolom berlabel bahasa Indonesia.
- Menyediakan kolom pencarian kecamatan secara langsung menggunakan pencocokan teks (*substring matching*).
- Tombol unduh data hasil filter ke dalam berkas berekstensi CSV.
- Menampilkan nilai RMSE, koefisien determinasi R², jumlah data latih, dan jumlah data uji yang dihasilkan oleh proses fit model Random Forest terhadap dataset aktif.
- Menampilkan visualisasi tingkat kontribusi fitur (*feature importance*) dan diagram pencar (*scatter plot*) perbandingan nilai aktual vs prediksi.
- **Manajemen Input Data**: Menyediakan dua widget expander berisi formulir input manual:
  1. *Form Data Sosio-Ekonomi*: Memasukkan tahun, pilihan kecamatan, tingkat pendidikan, pendapatan per kapita, tingkat pengangguran, kepadatan penduduk, dan IPM.
  2. *Form Data Partisipasi Politik*: Memasukkan tahun, pilihan kecamatan, jumlah DPT, jumlah pengguna hak pilih, dan sumber data. Persentase partisipasi politik secara otomatis dihitung dengan rumus:
     $$\text{Partisipasi Politik} = \frac{\text{Pengguna Hak Pilih}}{\text{DPT}} \times 100$$
- Penyimpanan data baru menggunakan operasi SQL `INSERT ON CONFLICT DO UPDATE` (upsert) ke database SQLite. Halaman akan dimuat ulang (`st.rerun()`) otomatis setelah penyimpanan berhasil.

### 4.1.3 Implementasi Halaman Prediksi
Halaman Prediksi (`pages/3_Prediksi.py`) digunakan oleh pengguna untuk melakukan estimasi tingkat partisipasi politik baru secara interaktif:
- Menyediakan formulir masukan variabel sosial ekonomi (pendidikan, pendapatan, pengangguran, kepadatan penduduk, IPM) beserta isian opsional untuk kecamatan dan tahun target.
- Setelah tombol "Prediksi" ditekan, sistem memanggil fungsi `predict_participation()` yang mengumpankan data input ke model Random Forest Regressor yang telah dilatih.
- Menampilkan output estimasi persentase partisipasi politik di dalam kotak berlatar belakang biru dengan ukuran huruf tebal dan besar.
- **Penyimpanan Hasil Prediksi**: Secara otomatis menyimpan nilai masukan dan output estimasi ke tabel `hasil_prediksi` di database SQLite.
- **Tabel Riwayat Prediksi**: Menampilkan tabel riwayat pencatatan hasil prediksi pengguna sebelumnya di bagian bawah halaman secara urut berdasarkan waktu pembuatan terbaru (*descending*).

### 4.1.4 Implementasi Halaman Visualisasi
Halaman Visualisasi (`pages/4_Visualisasi.py`) menampilkan visualisasi analisis data terpadu:
- Grafik heatmap matriks korelasi Pearson antar-variabel masukan dan target untuk melihat tingkat hubungan (positif/negatif).
- Grafik aktual vs prediksi dan pentingnya variabel.
- **Peta Partisipasi Politik**: Menampilkan peta choropleth wilayah kecamatan Banjarmasin menggunakan integrasi berkas `data/geo/kecamatan_5.geojson`. Sistem memetakan warna wilayah secara dinamis dengan mencocokkan nama kecamatan dari basis data ke atribut `properties.WADMKC` pada file GeoJSON.

### 4.1.5 Implementasi Halaman Tentang
Halaman Tentang (`pages/5_Tentang.py`) menyajikan dokumentasi aplikasi secara komprehensif bagi pengguna. Halaman ini menjelaskan dasar teori metode Random Forest Regressor, alur jalannya data dalam sistem, daftar sumber data resmi (BPS dan KPU), serta diagram struktur tabel database SQLite lokal.

### 4.1.6 Implementasi Database SQLite
Database SQLite diimplementasikan dalam berkas fisik `database/polpart.db`. Hubungan relasional antar-tabel (relasi kunci tamu) dipaksakan aktif menggunakan perintah SQL `PRAGMA foreign_keys = ON;` pada modul `src/database.py`. Data ditarik ke dalam program menggunakan library Pandas melalui fungsi `pandas.read_sql_query()` untuk diubah menjadi DataFrame. Modul database menyediakan 15 fungsi API internal untuk menunjang operasi baca, tulis, perbarui, hapus, dan pengecekan status inisialisasi basis data.

### 4.1.7 Implementasi Model Random Forest
Model Random Forest diimplementasikan menggunakan kelas `RandomForestRegressor` dari pustaka `scikit-learn`. Model dikonfigurasi dengan parameter:
- `n_estimators`: 300 (jumlah decision tree)
- `max_depth`: 8 (kedalaman maksimal pohon)
- `random_state`: 42 (menjamin konsistensi hasil pembelahan data)
- `min_samples_leaf`: 1

Model dilatih menggunakan fitur-fitur independen (X): `tingkat_pendidikan`, `pendapatan_per_kapita`, `tingkat_pengangguran`, `kepadatan_penduduk`, dan `ipm`. Target estimasi (y) adalah `partisipasi_politik`. Sebelum pelatihan, sistem secara otomatis menghapus baris data yang bernilai kosong (`NaN`) pada kolom fitur atau target. Evaluasi performa dihitung menggunakan metrik akurasi Root Mean Squared Error (RMSE) dan Koefisien Determinasi ($R^2$). Log hasil pelatihan disimpan ke tabel `model_evaluasi` setiap kali model diperbarui.

---

## 4.2 Pengujian Sistem

### 4.2.1 Black Box Testing
Pengujian fungsionalitas sistem dilakukan menggunakan metode Black Box Testing untuk menguji kesesuaian output terhadap skenario masukan pengguna tanpa melihat kode program secara internal.
*(Tabel hasil pengujian Black Box lengkap dapat dilihat pada dokumen [BLACKBOX_TESTING.md](BLACKBOX_TESTING.md))*
