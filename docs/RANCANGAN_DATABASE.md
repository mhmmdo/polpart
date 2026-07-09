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
* **`level_data`** (TEXT): Tingkat wilayah data (default 'tps').
* **`kecamatan`** (TEXT, Not Null): Nama kecamatan.
* **`kelurahan`** (TEXT, Not Null): Nama kelurahan/desa.
* **`no_tps`** (TEXT, Not Null): Nomor TPS.
* **`id_record`** (TEXT): Kode ID rekaman unik dari KPU.
* **`dpt`** (INTEGER): Jumlah Daftar Pemilih Tetap di TPS tersebut.
* **`pengguna_hak_pilih`** (INTEGER): Jumlah pemilih yang datang memberikan suara.
* **`partisipasi_politik`** (REAL): Persentase partisipasi politik (`pengguna_hak_pilih / dpt * 100`).
* **`dpt_total_tps`** (INTEGER): Total DPT.
* **`penduduk_total_kelurahan`** (TEXT): Jumlah estimasi penduduk di tingkat kelurahan.
* **`penduduk_total_kecamatan`** (INTEGER): Jumlah penduduk di tingkat kecamatan.
* **`rasio_dpt_terhadap_penduduk_kelurahan`** (REAL): Perbandingan DPT dengan penduduk kelurahan.
* **`pendapatan_per_kapita`** (REAL): Rata-rata pendapatan per kapita kelurahan.
* **`tingkat_pengangguran`** (REAL): Persentase tingkat pengangguran kecamatan.
* **`kepadatan_penduduk`** (REAL): Kepadatan penduduk (jiwa/km²).
* **`ipm`** (REAL): Indeks Pembangunan Manusia kecamatan.
* **`jumlah_usia_17_24_kec`** (INTEGER): Jumlah penduduk usia 17-24 tahun di kecamatan.
* **`jumlah_usia_25_44_kec`** (INTEGER): Jumlah penduduk usia 25-44 tahun di kecamatan.
* **`jumlah_usia_45_plus_kec`** (INTEGER): Jumlah penduduk usia 45+ tahun di kecamatan.
* **`persen_usia_17_24_kec`** (REAL): Persentase pemilih muda (17-24 tahun) di tingkat kecamatan.
* **`persen_usia_25_44_kec`** (REAL): Persentase pemilih produktif (25-44 tahun) di tingkat kecamatan.
* **`persen_usia_45_plus_kec`** (REAL): Persentase pemilih senior (45+ tahun) di tingkat kecamatan.

### D. Tabel `data_partisipasi_agregat`
Menyimpan data historis pemilu 2019 tingkat agregat dapil/kecamatan.
* **`id`** (INTEGER, Primary Key, Auto Increment): ID baris data.
* **`tahun_pemilu`** (INTEGER): Tahun pemilu (2019).
* **`level_data`** (TEXT): Level data ('agregat').
* **`dapil`** (TEXT): Daerah pemilihan (contoh: BANJARMASIN 1).
* **`kecamatan`** (TEXT): Nama kecamatan.
* **`dpt_total`** (INTEGER): Jumlah DPT total di dapil/kecamatan.
* **`pengguna_total`** (INTEGER): Jumlah pemilih yang hadir total.
* **`partisipasi_politik`** (REAL): Rata-rata persentase partisipasi politik.
* **`sumber_data`** (TEXT): Sumber asal data (contoh: KPU).
* **`catatan`** (TEXT): Catatan/Keterangan tambahan.

### E. Tabel `hasil_prediksi`
Mencatat seluruh log input skenario simulasi dan output tebakan model.
* **`id_prediksi`** (INTEGER, Primary Key, Auto Increment): ID riwayat prediksi.
* **`kecamatan`** (TEXT): Nama kecamatan input.
* **`kelurahan`** (TEXT): Nama kelurahan input.
* **`no_tps`** (TEXT): Nomor TPS input.
* **`dpt`** (INTEGER): Nilai input DPT.
* **`rasio_dpt_terhadap_penduduk_kelurahan`** (REAL): Nilai input rasio DPT.
* **`pendapatan_per_kapita`** (REAL): Nilai input pendapatan per kapita.
* **`tingkat_pengangguran`** (REAL): Nilai input tingkat pengangguran.
* **`kepadatan_penduduk`** (REAL): Nilai input kepadatan penduduk.
* **`ipm`** (REAL): Nilai input IPM.
* **`persen_usia_17_24_kec`** (REAL): Nilai input % pemilih usia 17-24.
* **`persen_usia_25_44_kec`** (REAL): Nilai input % pemilih usia 25-44.
* **`persen_usia_45_plus_kec`** (REAL): Nilai input % pemilih usia 45+.
* **`hasil_prediksi`** (REAL): Angka persentase hasil prediksi model.
* **`created_at`** (TEXT): Tanggal & waktu pencatatan simulasi.

### F. Tabel `model_evaluasi`
Mencatat performa evaluasi statistik model Random Forest yang dilatih.
* **`id_evaluasi`** (INTEGER, Primary Key, Auto Increment): ID unik evaluasi.
* **`nama_model`** (TEXT, Not Null): Nama model (*Random Forest*).
* **`rmse`** (REAL): Nilai deviasi error Root Mean Squared Error.
* **`mae`** (REAL): Nilai deviasi error Mean Absolute Error.
* **`r2_score`** (REAL): Koefisien determinasi R-Squared.
* **`jumlah_data`** (INTEGER): Jumlah baris dataset yang digunakan.
* **`jumlah_training`** (INTEGER): Jumlah sampel untuk melatih model.
* **`jumlah_testing`** (INTEGER): Jumlah sampel untuk menguji model.
* **`tanggal_evaluasi`** (TEXT): Tanggal pelatihan model.

---

## 2. Struktur VIEW `dataset_final`
Merupakan query gabungan dinamis untuk menyajikan data siap latih bagi model pemilu 2024:
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
    pendapatan_per_kapita,
    tingkat_pengangguran,
    kepadatan_penduduk,
    ipm,
    persen_usia_17_24_kec,
    persen_usia_25_44_kec,
    persen_usia_45_plus_kec
FROM data_partisipasi_tps
WHERE tahun_pemilu = 2024;
```
