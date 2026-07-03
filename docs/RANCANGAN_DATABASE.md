# Rancangan Database SQLite: Sistem Prediksi Partisipasi Politik

Sistem menggunakan SQLite sebagai basis data lokal karena ringan, tidak membutuhkan konfigurasi server, dan sesuai untuk aplikasi prototype berbasis Python dan Streamlit. Database disimpan dalam file `database/polpart.db`.

Berikut adalah rancangan tabel dan VIEW yang digunakan dalam sistem:

---

## 1. Tabel `kecamatan`
Tabel ini berfungsi sebagai tabel master untuk menyimpan nama-nama kecamatan di Kota Banjarmasin.

| Nama Field | Tipe Data | Nullable | Keterangan |
| :--- | :--- | :--- | :--- |
| `id_kecamatan` | INTEGER | NO (PK, AUTOINCREMENT) | ID unik kecamatan |
| `nama_kecamatan` | TEXT | NO (UNIQUE) | Nama wilayah kecamatan |

---

## 2. Tabel `data_sosio_ekonomi`
Tabel ini digunakan untuk menyimpan variabel-variabel sosio-ekonomi per kecamatan per tahun, yang berfungsi sebagai fitur input model Random Forest.

| Nama Field | Tipe Data | Nullable | Keterangan |
| :--- | :--- | :--- | :--- |
| `id_sosio` | INTEGER | NO (PK, AUTOINCREMENT) | ID unik data sosio ekonomi |
| `id_kecamatan` | INTEGER | NO (FK) | Relasi ke tabel `kecamatan` |
| `tahun` | INTEGER | NO | Tahun pengambilan data |
| `tingkat_pendidikan` | REAL | YES | Persentase tingkat pendidikan masyarakat (%) |
| `pendapatan_per_kapita`| REAL | YES | Nilai rata-rata pendapatan per kapita (Rupiah) |
| `tingkat_pengangguran` | REAL | YES | Persentase tingkat pengangguran (%) |
| `kepadatan_penduduk`  | REAL | YES | Rasio jumlah penduduk per kilometer persegi |
| `ipm` | REAL | YES | Skor Indeks Pembangunan Manusia (skala 0-100) |
| `created_at` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu data dibuat |
| `updated_at` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu data diperbarui |

*Catatan: Terdapat constraint `UNIQUE(id_kecamatan, tahun)` untuk memastikan tidak ada duplikasi data sosio-ekonomi untuk kecamatan dan tahun yang sama.*

---

## 3. Tabel `data_partisipasi_politik`
Tabel ini digunakan untuk menyimpan data hasil pemilu/partisipasi politik per kecamatan per tahun, yang berfungsi sebagai target prediksi model.

| Nama Field | Tipe Data | Nullable | Keterangan |
| :--- | :--- | :--- | :--- |
| `id_partisipasi` | INTEGER | NO (PK, AUTOINCREMENT) | ID unik data partisipasi politik |
| `id_kecamatan` | INTEGER | NO (FK) | Relasi ke tabel `kecamatan` |
| `tahun` | INTEGER | NO | Tahun pemilu/pengambilan data |
| `dpt` | INTEGER | YES | Jumlah Daftar Pemilih Tetap |
| `pengguna_hak_pilih` | INTEGER | YES | Jumlah pemilih yang menggunakan hak suara |
| `partisipasi_politik` | REAL | YES | Persentase tingkat partisipasi politik (%) |
| `sumber_data` | TEXT | YES | Sumber asal data (misal: KPU) |
| `created_at` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu data dibuat |
| `updated_at` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu data diperbarui |

*Catatan: Terdapat constraint `UNIQUE(id_kecamatan, tahun)` untuk memastikan tidak ada duplikasi data partisipasi untuk kecamatan dan tahun yang sama.*

---

## 4. Tabel `hasil_prediksi`
Tabel ini menyimpan data log masukan variabel dan hasil estimasi tingkat partisipasi politik yang telah diprediksi oleh pengguna.

| Nama Field | Tipe Data | Nullable | Keterangan |
| :--- | :--- | :--- | :--- |
| `id_prediksi` | INTEGER | NO (PK, AUTOINCREMENT) | ID unik hasil prediksi |
| `id_kecamatan` | INTEGER | YES (FK) | Relasi ke tabel `kecamatan` (opsional) |
| `tahun` | INTEGER | YES | Tahun target prediksi (opsional) |
| `tingkat_pendidikan` | REAL | NO | Fitur input tingkat pendidikan (%) |
| `pendapatan_per_kapita`| REAL | NO | Fitur input pendapatan per kapita (Rupiah) |
| `tingkat_pengangguran` | REAL | NO | Fitur input tingkat pengangguran (%) |
| `kepadatan_penduduk`  | REAL | NO | Fitur input kepadatan penduduk |
| `ipm` | REAL | NO | Fitur input IPM |
| `hasil_prediksi` | REAL | NO | Persentase hasil prediksi model (%) |
| `created_at` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu prediksi dilakukan |

---

## 5. Tabel `model_evaluasi`
Tabel ini mencatat riwayat performa model Random Forest setiap kali model tersebut dilatih ulang (fit).

| Nama Field | Tipe Data | Nullable | Keterangan |
| :--- | :--- | :--- | :--- |
| `id_evaluasi` | INTEGER | NO (PK, AUTOINCREMENT) | ID unik evaluasi model |
| `nama_model` | TEXT | NO | Nama algoritma model (Random Forest) |
| `rmse` | REAL | YES | Skor Root Mean Squared Error model |
| `r2_score` | REAL | YES | Skor koefisien determinasi R² model |
| `jumlah_data` | INTEGER | YES | Total baris data yang digunakan |
| `jumlah_training` | INTEGER | YES | Jumlah baris data latih (training set) |
| `jumlah_testing` | INTEGER | YES | Jumlah baris data uji (testing set) |
| `tanggal_evaluasi` | TEXT | YES (Default: CURRENT_TIMESTAMP) | Waktu pengujian model dilakukan |

---

## 6. VIEW `dataset_final`
`dataset_final` merupakan tabel virtual (VIEW) yang mempermudah pembacaan dataset secara utuh oleh program Python. VIEW ini menggabungkan data sosio-ekonomi dan partisipasi politik dengan melakukan relasi (JOIN) ke tabel kecamatan.

### Kueri SQL Pembuatan VIEW:
```sql
CREATE VIEW IF NOT EXISTS dataset_final AS
SELECT
    se.tahun,
    k.nama_kecamatan AS kecamatan,
    se.tingkat_pendidikan,
    se.pendapatan_per_kapita,
    se.tingkat_pengangguran,
    se.kepadatan_penduduk,
    se.ipm,
    pp.partisipasi_politik
FROM data_sosio_ekonomi se
JOIN kecamatan k ON se.id_kecamatan = k.id_kecamatan
LEFT JOIN data_partisipasi_politik pp
    ON pp.id_kecamatan = se.id_kecamatan
    AND pp.tahun = se.tahun;
```

### Fungsi VIEW:
VIEW ini menggabungkan indikator sosio-ekonomi sebagai fitur independen (X) dengan tingkat partisipasi politik sebagai fitur dependen (y). VIEW ini menjadi sumber data utama yang dibaca oleh modul `src/data_loader.py` untuk mensuplai data ke Dashboard, Visualisasi, dan proses Pelatihan Model Random Forest.
