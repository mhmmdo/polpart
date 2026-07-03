# Prediksi Partisipasi Politik Berbasis Random Forest & SQLite

Aplikasi ini dibuat menggunakan **Python + Streamlit** untuk menampilkan dashboard data partisipasi politik, data historis, prediksi Random Forest, visualisasi korelasi, feature importance, dan peta sederhana berbasis GeoJSON.

Sistem ini telah dimigrasi untuk menggunakan **database SQLite** sebagai penyimpanan utama, menggantikan pembacaan CSV langsung.

> [!NOTE]
> Database tersimpan di `database/polpart.db`. CSV hanya dipakai untuk import awal, bukan penyimpanan utama. Setelah data masuk SQLite, sistem membaca data secara dinamis dari database. GeoJSON tetap digunakan untuk peta kecamatan.

---

## Struktur Folder

```text
polpart_streamlit_rf_pro/
├── app.py
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Data_Historis.py
│   ├── 3_Prediksi.py
│   ├── 4_Visualisasi.py
│   └── 5_Tentang.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── data_loader.py
│   ├── model.py
│   ├── ui.py
│   ├── utils.py
│   └── visualizations.py
├── database/
│   ├── polpart.db
│   └── schema.sql
├── data/
│   ├── import/
│   │   └── data_final_template.csv
│   └── geo/
│       └── kecamatan_5.geojson
├── scripts/
│   ├── init_db.py
│   ├── import_csv_to_sqlite.py
│   └── train_model.py
├── models/
├── assets/
│   └── style.css
├── requirements.txt
└── README.md
```

---

## Fitur Utama

1. **Dashboard**: Ringkasan data (rata-rata, tertinggi, terendah), grafik partisipasi per kecamatan, dan tren tahunan yang diambil dari SQLite.
2. **Data Historis**: Tabel data dari database, fitur pencarian, filter tahun/wilayah, serta evaluasi model Random Forest (RMSE, R²). Menyediakan formulir manual untuk memasukkan data sosio-ekonomi dan partisipasi politik baru secara dinamis ke database.
3. **Prediksi**: Memprediksi tingkat partisipasi politik berdasarkan input variabel sosio-ekonomi. Riwayat prediksi disimpan ke database dan ditampilkan di tabel bagian bawah.
4. **Visualisasi**: Matriks korelasi antar variabel, grafik aktual vs prediksi, dan peta choropleth kecamatan Banjarmasin menggunakan GeoJSON.
5. **Tentang**: Informasi detail metode Random Forest, alur sistem, dan deskripsi tabel database.

---

## Cara Menjalankan

### 1. Install Dependency
Pastikan Anda berada di folder root proyek ini dan jalankan perintah berikut untuk menginstal paket Python yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### 2. Inisialisasi Database
Jalankan skrip berikut untuk membuat folder database, file database `polpart.db`, menerapkan skema tabel, dan memasukkan data kecamatan default:

```bash
python scripts/init_db.py
```

### 3. Letakkan CSV Template untuk Import Awal
Letakkan file CSV data di path berikut:
`data/import/data_final_template.csv`

Format kolom CSV wajib:
```text
tahun,kecamatan,tingkat_pendidikan,pendapatan_per_kapita,tingkat_pengangguran,kepadatan_penduduk,ipm,partisipasi_politik
```

### 4. Import Data dari CSV ke SQLite
Jalankan skrip import berikut untuk memuat data dari CSV template ke database SQLite:

```bash
python scripts/import_csv_to_sqlite.py
```

### 5. Jalankan Aplikasi Streamlit
Setelah database terisi, jalankan aplikasi web Streamlit:

```bash
streamlit run app.py
```

---

## Catatan Tambahan

* **Training Model via Script**: Selain training otomatis dari aplikasi web, Anda juga dapat melatih model secara manual dari terminal:
  ```bash
  python scripts/train_model.py
  ```
  Model yang dilatih akan disimpan ke `models/random_forest_partisipasi.joblib`.
* **GeoJSON**: Peta kecamatan dicocokkan menggunakan kode/nama kecamatan pada atribut GeoJSON `WADMKC` dengan nama kecamatan yang tersimpan di database.
