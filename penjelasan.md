# Penjelasan Sistem Prediksi Partisipasi Politik (PolPart RF)

Sistem Prediksi Partisipasi Politik adalah sebuah aplikasi web berbasis **Streamlit** yang memanfaatkan algoritma *Machine Learning* **Random Forest Regressor** untuk menganalisis dan memprediksi tingkat partisipasi politik masyarakat di berbagai kecamatan berdasarkan faktor-faktor sosio-ekonomi (seperti tingkat pendidikan, pendapatan per kapita, tingkat pengangguran, kepadatan penduduk, dan IPM).

## 🔄 Alur Sistem (System Flow)

Secara garis besar, sistem ini bekerja dengan alur sebagai berikut:

1. **Pengumpulan & Impor Data**
   Pengguna dapat mengimpor data mentah (CSV) ke dalam sistem melalui halaman web (Sidebar) atau menggunakan script CLI (`scripts/import_csv_to_sqlite.py`). Data yang masuk akan disimpan ke dalam database **SQLite** lokal (`polpart.db`).
2. **Pemrosesan Data (Data Preprocessing)**
   Data di dalam database ditarik oleh modul `src/data_loader.py`, di mana data dibersihkan dari nilai kosong (NaN), disesuaikan format tipe datanya, dan digabungkan menjadi satu tabel utuh (`dataset_final`).
3. **Pelatihan Model (Model Training)**
   Jika data telah siap, algoritma Random Forest (`src/model.py`) akan mempelajari pola kaitan antara faktor sosio-ekonomi (Fitur/X) dengan partisipasi politik (Target/Y). Proses ini mengevaluasi kinerja algoritma dan menghasilkan metrik seperti **RMSE** dan **R2 Score**, serta menyimpan "otak" (*trained model*) ke dalam file `.joblib`.
4. **Prediksi (Prediction)**
   Pengguna dapat memasukkan skenario angka sosio-ekonomi baru pada Halaman Prediksi. Model yang sudah dilatih tadi akan dipanggil untuk menebak berapakah tingkat partisipasi politik jika kondisi angkanya seperti yang dimasukkan. Hasil tebakan disimpan ke histori database.
5. **Visualisasi Data**
   Sistem menyajikan diagram tren historis, matriks korelasi, diagram perbandingan nilai aktual vs prediksi, dan **Peta Spasial (Choropleth)** interaktif untuk memudahkan pemahaman.

---

## 📂 Struktur Direktori & Penjelasan Kode

Aplikasi ini dirancang secara terstruktur (modular) agar mudah dikelola. Berikut adalah penjelasan fungsi tiap folder dan file:

### 1. File Utama
- **`app.py`**
  Ini adalah gerbang utama aplikasi. Menjalankan konfigurasi halaman dasar (layout luas, ikon), menyuntikkan file CSS kustom, serta mengatur menu navigasi sidebar (`streamlit-option-menu`). File ini yang menghubungkan dan memanggil semua halaman di folder `pages/`.

### 2. Folder `pages/` (Antarmuka Halaman)
Folder ini berisi script tampilan tiap halaman di dalam aplikasi.
- **`1_Dashboard.py`**: Halaman beranda yang menampilkan Ringkasan (angka rata-rata, tertinggi, terendah), metrik evaluasi model (RMSE, R2), serta grafik interaktif 5 wilayah tertinggi.
- **`2_Data_Historis.py`**: Halaman untuk melihat wujud tabel database secara langsung (Tabel Sosio-Ekonomi & Tabel Partisipasi). Dilengkapi fitur pencarian dan filter tahun/wilayah.
- **`3_Prediksi.py`**: Halaman interaktif di mana pengguna bisa mengatur *slider* untuk memasukkan parameter tingkat pendidikan, pendapatan, dsb., lalu mesin akan memunculkan nilai prediksi partisipasi politik beserta tabel riwayat prediksi.
- **`4_Visualisasi.py`**: Menampilkan analitik mendalam dengan bantuan *Plotly*, seperti korelasi antar variabel (*heatmap*), faktor fitur yang paling berpengaruh (*feature importance*), peta wilayah kecamatan, serta scatter plot prediksi vs aktual.
- **`5_Tentang.py`**: Berisi panduan, informasi teknis tentang sistem, dan ucapan pembuat.

### 3. Folder `src/` (Source Code Logika)
Folder ini adalah mesin penggerak (Back-end) dari aplikasi ini.
- **`config.py`**: Pusat pengaturan aplikasi. Di sini kita menentukan alamat-alamat file (*path*), list nama kolom dataset, dan mengatur hyperparameter untuk mesin Random Forest (misalnya `n_estimators`, `max_depth`).
- **`database.py`**: Jembatan interaksi dengan database **SQLite**. Berisi perintah SQL murni (Query) untuk melakukan Insert, Update, Delete, dan Select tabel (Tabel Kecamatan, Sosio-Ekonomi, Partisipasi Politik).
- **`data_loader.py`**: Modul yang memuat (Load) data mentah dari database, melakukan pembersihan data (*Drop NaN*), merapikan penamaan kolom, hingga menarik data peta wilayah format `.geojson`.
- **`model.py`**: Berisi logika *Machine Learning*. Di dalamnya terdapat fungsi untuk membagi data *train/test*, melatih (`fit`) algoritma `RandomForestRegressor`, menghitung eror (RMSE, R2), melihat variabel paling penting, dan melakukan prediksi.
- **`ui.py`**: Mengatur elemen antarmuka komponen Streamlit yang dipakai berulang. Contoh: desain kotak *metric card*, judul hero, dan proses sidebar pengunggahan file CSV.
- **`utils.py`**: Kumpulan fungsi bantuan yang sifatnya kecil/minor, seperti mengubah angka desimal menjadi persentase `%` dan menambahkan format mata uang `Rp`.
- **`visualizations.py`**: Kumpulan *blueprint* pembuat grafik. Berisi integrasi dengan library **Plotly Express** untuk menggambar peta spasial (`choropleth_mapbox`), diagram batang, tren garis, dan matriks.

### 4. Folder `scripts/` (Operasi Terminal/CLI)
File yang ada di sini bukan untuk tampilan web, melainkan dijalankan manual via terminal/CMD (*Command Prompt*).
- **`init_db.py`**: Dijalankan **pertama kali** untuk menyusun dan membuat tabel-tabel kosong di dalam database sesuai rancangan `schema.sql`.
- **`import_csv_to_sqlite.py`**: Script otomatisasi untuk menyedot jutaan/ribuan baris data dari file CSV mentah lalu disuntikkan ke dalam database aplikasi.
- **`train_model.py`**: Script manual untuk memancing proses belajar mesin (*training*) Random Forest dan menyimpan hasilnya menjadi file model yang siap pakai (`models/random_forest_partisipasi.joblib`).
