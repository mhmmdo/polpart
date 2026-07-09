# Entity Relationship Diagram (ERD) - SQLite

Diagram di bawah ini menggambarkan struktur entitas tabel dan relasi logika data di dalam database `polpart.db` setelah penyesuaian level TPS dan penambahan autentikasi peran (*role*).

```mermaid
erDiagram
    PENGGUNA {
        integer id_pengguna PK
        text username
        text password_hash
        text role
        text created_at
    }

    DATA_PARTISIPASI_TPS {
        integer id PK
        integer tahun_pemilu
        text level_data
        text kecamatan
        text kelurahan
        text no_tps
        text id_record
        integer dpt
        integer pengguna_hak_pilih
        real partisipasi_politik
        integer dpt_total_tps
        text penduduk_total_kelurahan
        integer penduduk_total_kecamatan
        real rasio_dpt_terhadap_penduduk_kelurahan
        real pendapatan_per_kapita
        real tingkat_pengangguran
        real kepadatan_penduduk
        real ipm
        integer jumlah_usia_17_24_kec
        integer jumlah_usia_25_44_kec
        integer jumlah_usia_45_plus_kec
        real persen_usia_17_24_kec
        real persen_usia_25_44_kec
        real persen_usia_45_plus_kec
        text created_at
    }

    DATA_PARTISIPASI_AGREGAT {
        integer id PK
        integer tahun_pemilu
        text level_data
        text dapil
        text kecamatan
        integer dpt_total
        integer pengguna_total
        real partisipasi_politik
        text sumber_data
        text catatan
    }

    HASIL_PREDIKSI {
        integer id_prediksi PK
        text kecamatan
        text kelurahan
        text no_tps
        integer dpt
        real rasio_dpt_terhadap_penduduk_kelurahan
        real pendapatan_per_kapita
        real tingkat_pengangguran
        real kepadatan_penduduk
        real ipm
        real persen_usia_17_24_kec
        real persen_usia_25_44_kec
        real persen_usia_45_plus_kec
        real hasil_prediksi
        text created_at
    }

    MODEL_EVALUASI {
        integer id_evaluasi PK
        text nama_model
        real rmse
        real mae
        real r2_score
        integer jumlah_data
        integer jumlah_training
        integer jumlah_testing
        text tanggal_evaluasi
    }
```

### Penjelasan Relasi:
* **`PENGGUNA`**: Berdiri sendiri sebagai entitas pengelola sistem. Akun dengan `role = 'admin'` memiliki hak akses istimewa untuk mengunggah dan melakukan pembaruan massal (*bulk upsert*) pada tabel `DATA_PARTISIPASI_TPS`.
* **`DATA_PARTISIPASI_TPS`**: Menyimpan baris data riil pemilu tingkat TPS tahun 2024. Data dari tabel ini diproyeksikan langsung ke VIEW `dataset_final` untuk melatih algoritma *Random Forest Regressor*.
* **`DATA_PARTISIPASI_AGREGAT`**: Menyimpan data pemilu historis 2019 tingkat agregat dapil/kecamatan.
* **`HASIL_PREDIKSI`**: Menjadi log riwayat transaksi prediksi yang dilakukan baik oleh `Admin` maupun `User`.
* **`MODEL_EVALUASI`**: Menampung log evaluasi statistik performa model (*RMSE*, *MAE*, dan *R² Score*) hasil training secara berkala.
