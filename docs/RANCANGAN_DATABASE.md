# Rancangan Database SQLite (PolPart RF)

Sistem menggunakan database relasional ringan **SQLite** (`database/polpart.db`) sebagai penyimpanan utama data tingkat TPS dan autentikasi pengguna.

---

## 1. Skema Tabel

### A. Tabel `pengguna`
Menyimpan data akun pengguna untuk keperluan registrasi dan login.
* **`id_pengguna`** (INTEGER, Primary Key, Auto Increment): ID unik pengguna.
* **`username`** (TEXT, Unique, Not Null): Nama pengguna unik untuk login.
* **`password_hash`** (TEXT, Not Null): Sandi terenkripsi (SHA-256).
* **`role`** (TEXT, Not Null, Default 'user'): Peran akses pengguna (`admin` atau `user`).
* **`created_at`** (TEXT): Tanggal registrasi akun.

### B. Tabel `kecamatan`
Daftar kecamatan resmi di wilayah administrasi.
* **`id_kecamatan`** (INTEGER, Primary Key, Auto Increment): ID unik kecamatan.
* **`nama_kecamatan`** (TEXT, Unique, Not Null): Nama kecamatan (huruf kapital).

### C. Tabel `data_partisipasi_tps`
Penyimpanan utama data mentah pemilu tingkat Tempat Pemungutan Suara (TPS).
* **`id`** (INTEGER, Primary Key, Auto Increment): ID baris data.
* **`tahun_pemilu`** (INTEGER, Not Null): Tahun penyelenggaraan pemilu.
* **`kecamatan`** (TEXT, Not Null): Nama kecamatan.
* **`kelurahan`** (TEXT, Not Null): Nama kelurahan/desa.
* **`no_tps`** (TEXT, Not Null): Nomor TPS.
* **`id_record`** (TEXT): Kode ID rekaman unik dari KPU.
* **`jenis_kelamin`** (TEXT): Pengelompokan gender (contoh: JML untuk Jumlah).
* **`dpt`** (INTEGER): Jumlah Daftar Pemilih Tetap di TPS tersebut.
* **`pengguna_hak_pilih`** (INTEGER): Jumlah pemilih yang datang memberikan suara.
* **`partisipasi_politik`** (REAL): Persentase partisipasi politik (`pengguna_hak_pilih / dpt * 100`).
* **`dpt_total_tps`** (INTEGER): Total DPT.
* **`penduduk_total_kelurahan`** (TEXT): Jumlah estimasi penduduk di tingkat kelurahan.
* **`rasio_dpt_terhadap_penduduk_kelurahan`** (REAL): Perbandingan DPT dengan penduduk kelurahan.
* **`persen_usia_17_24_kec`** (REAL): Persentase pemilih muda (17-24 tahun) di tingkat kecamatan.
* **`persen_usia_25_44_kec`** (REAL): Persentase pemilih produktif (25-44 tahun) di tingkat kecamatan.
* **`persen_usia_45_plus_kec`** (REAL): Persentase pemilih senior (45+ tahun) di tingkat kecamatan.

### D. Tabel `hasil_prediksi`
Mencatat seluruh log input skenario simulasi dan output tebakan model.
* **`id_prediksi`** (INTEGER, Primary Key, Auto Increment): ID riwayat prediksi.
* **`kecamatan`** (TEXT): Nama kecamatan input.
* **`kelurahan`** (TEXT): Nama kelurahan input.
* **`no_tps`** (TEXT): Nomor TPS input.
* **`dpt`** (INTEGER): Nilai input DPT.
* **`rasio_dpt`** (REAL): Nilai input rasio DPT.
* **`usia_17_24`** (REAL): Nilai input % pemilih usia 17-24.
* **`usia_25_44`** (REAL): Nilai input % pemilih usia 25-44.
* **`usia_45_plus`** (REAL): Nilai input % pemilih usia 45+.
* **`hasil_prediksi`** (REAL): Angka persentase hasil prediksi model.
* **`created_at`** (TEXT): Tanggal & waktu pencatatan simulasi.

### E. Tabel `model_evaluasi`
Mencatat performa evaluasi statistik model Random Forest yang dilatih.
* **`id_evaluasi`** (INTEGER, Primary Key, Auto Increment): ID unik evaluasi.
* **`nama_model`** (TEXT, Not Null): Nama model (*Random Forest*).
* **`rmse`** (REAL): Nilai deviasi error Root Mean Squared Error.
* **`r2_score`** (REAL): Koefisien determinasi R-Squared.
* **`jumlah_data`** (INTEGER): Jumlah baris dataset yang digunakan.
* **`jumlah_training`** (INTEGER): Jumlah sampel untuk melatih model.
* **`jumlah_testing`** (INTEGER): Jumlah sampel untuk menguji model.
* **`tanggal_evaluasi`** (TEXT): Tanggal pelatihan model.

---

## 2. Struktur VIEW `dataset_final`
Merupakan query gabungan dinamis untuk menyajikan data siap latih bagi model:
```sql
CREATE VIEW dataset_final AS
SELECT
    tahun_pemilu AS tahun,
    kecamatan,
    kelurahan,
    no_tps,
    dpt,
    pengguna_hak_pilih,
    partisipasi_politik,
    rasio_dpt_terhadap_penduduk_kelurahan,
    persen_usia_17_24_kec,
    persen_usia_25_44_kec,
    persen_usia_45_plus_kec
FROM data_partisipasi_tps;
```
