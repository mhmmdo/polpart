# BAB III: ANALISA DAN DESAIN SISTEM

## 3.1 Tabel Kegiatan Pelaksanaan
Kegiatan pelaksanaan pengembangan Sistem Prediksi Partisipasi Politik disusun dalam tabel berikut:

| No | Tahapan Kegiatan | Output Kegiatan |
| :--- | :--- | :--- |
| 1 | Analisa Kebutuhan | Dokumen spesifikasi kebutuhan fungsional dan non-fungsional |
| 2 | Perancangan Skema Database | Skema database SQLite (`schema.sql`) |
| 3 | Perancangan Antarmuka (UI) | Wireframe dan layout halaman Streamlit |
| 4 | Pembuatan Database & Impor | Database `polpart.db` dan skrip impor data |
| 5 | Pengembangan Logika Model RF | Algoritma latih model Random Forest di Python |
| 6 | Pembuatan Antarmuka Streamlit| Dashboard, Data Historis, Prediksi, Visualisasi |
| 7 | Pengujian Sistem | Lembar pengujian Black Box |
| 8 | Penyusunan Laporan | Draft dokumen laporan pkl/TA |

---

## 3.2 Uraian Kegiatan
Berikut adalah penjelasan singkat mengenai uraian kegiatan pelaksanaan:
1. **Analisa Kebutuhan**: Mengidentifikasi variabel sosio-ekonomi yang mempengaruhi partisipasi politik (IPM, pengangguran, pendidikan, dll.) serta merumuskan fungsi-fungsi pada UI.
2. **Perancangan Basis Data**: Merancang tabel relational yang fleksibel guna membagi data sosio-ekonomi dan partisipasi politik pemilu untuk meminimalisir inkonsistensi.
3. **Pengembangan Sistem**: Mengintegrasikan `sqlite3`, `pandas`, `scikit-learn` untuk melatih Random Forest dan memetakan data kecamatan dengan koordinat spasial GeoJSON ke dalam peta web.
4. **Verifikasi & Validasi**: Menguji fungsionalitas sistem secara keseluruhan (Black Box) untuk menjamin stabilitas integrasi database lokal.

---

## 3.3 Analisa Sistem

### 3.3.1 Sistem yang Sedang Berjalan
Sebelum adanya sistem terkomputerisasi ini, pengolahan data sosio-ekonomi dan partisipasi politik di instansi terkait masih memiliki beberapa kelemahan, antara lain:
- Penyimpanan data historis masih terpisah dalam format berkas Microsoft Excel atau PDF per tahun anggaran/kegiatan.
- Kesulitan dalam melakukan integrasi data lintas tahun untuk keperluan pemodelan statistik.
- Analisis dan prediksi tingkat partisipasi pemilu selanjutnya masih dilakukan secara manual dengan perkiraan kasar (intuitif) tanpa pembuktian model statistik terukur.
- Visualisasi peta batas kecamatan tidak terintegrasi langsung dengan angka statistik real-time.

### 3.3.2 Usulan Pemecahan Masalah
Untuk mengatasi kelemahan di atas, diusulkan sebuah sistem prediksi partisipasi politik berbasis web dengan spesifikasi:
- **Penyimpanan Utama SQLite**: Menggunakan database relasional lokal `database/polpart.db` sebagai penyimpanan utama. File CSV hanya digunakan sekali sebagai pengunggah data awal (impor data).
- **Pemodelan Random Forest Regression**: Memanfaatkan machine learning untuk menemukan pola korelasi dari indikator tingkat pendidikan, pendapatan per kapita, tingkat pengangguran, kepadatan penduduk, dan IPM untuk memproyeksikan persentase partisipasi politik.
- **Framework Streamlit**: Menyediakan antarmuka web interaktif yang responsif, mudah dipahami, dan beroperasi di server lokal.
- **Peta Interaktif Berbasis GeoJSON**: Menyajikan visualisasi geospasial kecamatan Banjarmasin menggunakan berkas GeoJSON (`kecamatan_5.geojson`) yang dicocokkan langsung dengan data SQLite.

Sistem dibagi menjadi 5 modul antarmuka:
1. **Dashboard**: Menyajikan metrik ringkasan data, grafik partisipasi per kecamatan, dan tren tahunan.
2. **Data Historis**: Menyajikan tabel data terpadu, fitur pencarian/filter, download CSV, serta evaluasi model Random Forest. Data diperbarui melalui unggah CSV di sidebar.
3. **Prediksi**: Form input variabel sosio-ekonomi untuk menghitung estimasi persentase partisipasi politik dilengkapi tabel riwayat prediksi.
4. **Visualisasi**: Menyajikan grafik heatmap korelasi variabel, grafik tren & perbandingan partisipasi, dan peta choropleth interaktif menggunakan Plotly + GeoJSON.
5. **Tentang**: Menyajikan informasi dokumentasi alur kerja sistem.

---

## 3.4 Desain Sistem

### 3.4.1 Flowchart
Sistem ini menggunakan flowchart terpisah untuk masing-masing fungsionalitas utama (Pengolahan Dataset, Impor Data, Dashboard, Pelatihan Random Forest, Prediksi, Visualisasi dan Peta) guna menggambarkan alur jalannya sistem secara logis.
*(Diagram alir proses dapat dilihat pada dokumen [FLOWCHART_SISTEM.md](FLOWCHART_SISTEM.md))*

### 3.4.2 Use Case Diagram
Pengguna berinteraksi secara penuh dengan aplikasi untuk mengimpor data, melihat metrik performa model, mengeksekusi fungsi prediksi, dan menganalisa grafik visualisasi.
*(Diagram use case dapat dilihat pada dokumen [USE_CASE_DIAGRAM.md](USE_CASE_DIAGRAM.md))*

### 3.4.3 Class Diagram
Aplikasi dimodelkan secara modular membagi fungsi akses database (`Database`), pemuatan data (`DataLoader`), pelatihan algoritma (`RandomForestModel`), pengendali layanan (`PredictionService`), dan pembuatan grafik (`VisualizationService`).
*(Diagram kelas dapat dilihat pada dokumen [CLASS_DIAGRAM.md](CLASS_DIAGRAM.md))*

### 3.4.4 Entity Relationship Diagram (ERD)
Database dirancang menggunakan model relasional. Hubungan satu-ke-banyak (*one-to-many*) terjalin antara tabel `kecamatan` dengan tabel `data_sosio_ekonomi`, `data_partisipasi_politik`, dan tabel log `hasil_prediksi`.
*(Diagram hubungan entitas dapat dilihat pada dokumen [ERD.md](ERD.md))*

### 3.4.5 Rancangan Database
Struktur tabel database SQLite `polpart.db` dirancang sebagai berikut:

#### 1. Tabel `kecamatan`
Menyimpan master data nama kecamatan.
- `id_kecamatan` (INTEGER, PK, AUTOINCREMENT)
- `nama_kecamatan` (TEXT, UNIQUE, NOT NULL)

#### 2. Tabel `data_sosio_ekonomi`
Menyimpan indikator sosio-ekonomi tahunan.
- `id_sosio` (INTEGER, PK, AUTOINCREMENT)
- `id_kecamatan` (INTEGER, FK)
- `tahun` (INTEGER, NOT NULL)
- `tingkat_pendidikan` (REAL)
- `pendapatan_per_kapita` (REAL)
- `tingkat_pengangguran` (REAL)
- `kepadatan_penduduk` (REAL)
- `ipm` (REAL)
- `created_at` / `updated_at` (TEXT)

#### 3. Tabel `data_partisipasi_politik`
Menyimpan indikator dpt, suara, dan persentase partisipasi.
- `id_partisipasi` (INTEGER, PK, AUTOINCREMENT)
- `id_kecamatan` (INTEGER, FK)
- `tahun` (INTEGER, NOT NULL)
- `dpt` (INTEGER)
- `pengguna_hak_pilih` (INTEGER)
- `partisipasi_politik` (REAL)
- `sumber_data` (TEXT)
- `created_at` / `updated_at` (TEXT)

#### 4. Tabel `hasil_prediksi`
Menyimpan log hasil prediksi user.
- `id_prediksi` (INTEGER, PK, AUTOINCREMENT)
- `id_kecamatan` (INTEGER, FK, Nullable)
- `tahun` (INTEGER, Nullable)
- Fitur-fitur sosio-ekonomi (REAL)
- `hasil_prediksi` (REAL, NOT NULL)
- `created_at` (TEXT)

#### 5. Tabel `model_evaluasi`
Menyimpan log akurasi model Random Forest.
- `id_evaluasi` (INTEGER, PK, AUTOINCREMENT)
- `nama_model` (TEXT)
- `rmse` / `r2_score` (REAL)
- `jumlah_data` / `jumlah_training` / `jumlah_testing` (INTEGER)
- `tanggal_evaluasi` (TEXT)

#### 6. VIEW `dataset_final`
VIEW yang digunakan untuk menggabungkan tabel `data_sosio_ekonomi` dan `data_partisipasi_politik` berdasarkan kecamatan dan tahun untuk diumpankan ke model regresi.

*(Detail struktur tabel markdown lengkap dapat dilihat pada dokumen [RANCANGAN_DATABASE.md](RANCANGAN_DATABASE.md))*

### 3.4.6 Desain Interface
Rancangan antarmuka dirancang bersih dengan skema tata letak (*wireframe*) berbasis Streamlit:

1. **Dashboard**: 
   - Sidebar: Informasi sumber data dan filter multiselect kecamatan/tahun.
   - Halaman Utama: Header pahlawan (*hero*), diikuti 4 kartu metrik performa statistik (Jumlah Data, Rata-rata Partisipasi, Kecamatan Tertinggi, Kecamatan Terendah), grafik batang partisipasi per kecamatan, dan grafik garis tren tahunan.
2. **Data Historis**:
   - Pencarian: Input teks pencarian kecamatan.
   - Tabel: Menampilkan tabel `dataset_final` dengan penamaan kolom berlabel Indonesia.
   - Tombol Download: Mengunduh CSV hasil filter.
   - Metrik Evaluasi: Menampilkan performa model (RMSE, R²) dan grafik feature importance serta scatter aktual vs prediksi.
   - Expander Input: Dua expander terpisah berisi form isian data baru dengan tombol simpan.
3. **Prediksi**:
   - Formulir Input: Dropdown pilihan kecamatan (opsional), tahun (opsional), slider persentase pendidikan, input angka pendapatan per kapita, slider pengangguran, input kepadatan penduduk, dan slider IPM.
   - Tombol Prediksi: Memicu penghitungan model dan menyimpan hasil ke SQLite.
   - Kartu Output: Menampilkan angka estimasi partisipasi politik berukuran besar di dalam wadah berbayang.
   - Tabel Riwayat: Menampilkan daftar riwayat pengujian prediksi sebelumnya.
4. **Visualisasi**:
   - Menampilkan Heatmap matriks korelasi, bagan batang pentingnya fitur, dan peta choropleth kecamatan Banjarmasin dengan gradasi warna partisipasi politik.
5. **Tentang**:
   - Penjelasan tekstual alur program dan pemodelan database.
