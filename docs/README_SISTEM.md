# README Sistem: Sistem Prediksi Partisipasi Politik Menggunakan Random Forest Berbasis Python dan Streamlit

## 1. Deskripsi Sistem
Sistem Prediksi Partisipasi Politik adalah sebuah aplikasi berbasis web yang dirancang untuk membantu dalam menganalisis dan memprediksi tingkat partisipasi politik masyarakat di tingkat kecamatan. Aplikasi ini menyajikan:
- **Dashboard**: Menampilkan ringkasan statistik dan grafik partisipasi per kecamatan serta tren tahunan.
- **Data Historis**: Menyajikan tabel data sosio-ekonomi dan partisipasi politik langsung dari database, serta dilengkapi formulir untuk penambahan/pembaruan data secara manual.
- **Prediksi RF**: Melakukan prediksi persentase partisipasi politik menggunakan algoritma Random Forest Regression berdasarkan indikator sosial ekonomi.
- **Visualisasi & Peta**: Menyajikan visualisasi korelasi antar-variabel, plot evaluasi aktual vs prediksi, dan peta choropleth berbasis koordinat geografis.
- **Tentang Aplikasi**: Menyediakan penjelasan metodologi, alur sistem, dan deskripsi database.

---

## 2. Teknologi yang Digunakan
Sistem dikembangkan menggunakan tumpukan teknologi modern berbasis Python berikut:
- **Bahasa Pemrograman**: Python
- **Web Framework**: Streamlit (untuk antarmuka pengguna interaktif)
- **Basis Data**: SQLite (sebagai penyimpanan lokal utama)
- **Analisis Data**: Pandas dan NumPy
- **Machine Learning**: Scikit-learn (Random Forest Regressor)
- **Visualisasi Grafik**: Plotly
- **Visualisasi Peta**: Folium & Streamlit-Folium (menggunakan berkas GeoJSON)

---

## 3. Struktur Folder Project
Berikut adalah struktur folder dari project **polpart_streamlit_rf_pro**:

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

## 4. Lokasi Berkas Penting
- **Database Utama**: `database/polpart.db` (SQLite)
- **Skema Database**: `database/schema.sql`
- **Data GeoJSON Kecamatan**: `data/geo/kecamatan_5.geojson`
- **Template Impor Data Awal**: `data/import/data_final_template.csv`

> [!IMPORTANT]
> Sistem menggunakan database SQLite sebagai penyimpanan utama. File CSV (`data_final_template.csv`) hanya digunakan untuk proses impor data awal (seeding) ke dalam database SQLite. Setelah proses impor selesai, sistem akan membaca dan menulis data secara dinamis dari dan ke database SQLite.

---

## 5. Cara Menjalankan Sistem

Lakukan langkah-langkah berikut di terminal untuk menjalankan sistem di lingkungan lokal Anda:

### Langkah 1: Instalasi Library/Dependency
Instal paket pustaka Python yang didefinisikan dalam `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Langkah 2: Inisialisasi Database
Jalankan skrip inisialisasi untuk membuat database `polpart.db` beserta tabel-tabelnya dan memasukkan data kecamatan default:
```bash
python scripts/init_db.py
```

### Langkah 3: Impor Data Awal dari CSV
Jalankan skrip berikut untuk membaca data dari template CSV (`data/import/data_final_template.csv`) dan menyimpannya ke dalam database SQLite:
```bash
python scripts/import_csv_to_sqlite.py
```

### Langkah 4: Menjalankan Aplikasi Streamlit
Jalankan server Streamlit untuk membuka aplikasi di web browser Anda:
```bash
streamlit run app.py
```
Aplikasi secara otomatis akan terbuka di peramban web pada alamat default `http://localhost:8501`.
