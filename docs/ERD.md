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
        text kecamatan
        text kelurahan
        text no_tps
        text id_record
        text jenis_kelamin
        integer dpt
        integer pengguna_hak_pilih
        real partisipasi_politik
        integer dpt_total_tps
        text penduduk_total_kelurahan
        real rasio_dpt_terhadap_penduduk_kelurahan
        real persen_usia_17_24_kec
        real persen_usia_25_44_kec
        real persen_usia_45_plus_kec
        text created_at
    }

    HASIL_PREDIKSI {
        integer id_prediksi PK
        text kecamatan
        text kelurahan
        text no_tps
        integer dpt
        real rasio_dpt
        real usia_17_24
        real usia_25_44
        real usia_45_plus
        real hasil_prediksi
        text created_at
    }

    MODEL_EVALUASI {
        integer id_evaluasi PK
        text nama_model
        real rmse
        real r2_score
        integer jumlah_data
        integer jumlah_training
        integer jumlah_testing
        text tanggal_evaluasi
    }
```

### Penjelasan Relasi:
* **`PENGGUNA`**: Berdiri sendiri sebagai entitas pengelola sistem. Akun dengan `role = 'admin'` memiliki hak akses istimewa untuk mengunggah dan melakukan pembaruan massal (*bulk upsert*) pada tabel `DATA_PARTISIPASI_TPS`.
* **`DATA_PARTISIPASI_TPS`**: Menyimpan baris data riil pemilu tingkat TPS. Data dari tabel ini diproyeksikan langsung ke VIEW `dataset_final` untuk melatih algoritma *Random Forest Regressor*.
* **`HASIL_PREDIKSI`**: Menjadi log riwayat transaksi prediksi yang dilakukan baik oleh `Admin` maupun `User`.
* **`MODEL_EVALUASI`**: Menampung log evaluasi statistik performa model (*RMSE* dan *R² Score*) hasil training secara berkala.
