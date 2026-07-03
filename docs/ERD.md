# Entity Relationship Diagram (ERD) Database

Entity Relationship Diagram (ERD) menggambarkan hubungan logika antar-tabel dalam database SQLite. Tabel `kecamatan` menjadi master data yang direlasikan dengan data sosial ekonomi, data partisipasi politik, dan hasil prediksi.

---

## 1. Diagram ERD (Mermaid)

```mermaid
erDiagram
    KECAMATAN {
        int id_kecamatan PK
        string nama_kecamatan
    }

    DATA_SOSIO_EKONOMI {
        int id_sosio PK
        int id_kecamatan FK
        int tahun
        float tingkat_pendidikan
        float pendapatan_per_kapita
        float tingkat_pengangguran
        float kepadatan_penduduk
        float ipm
        datetime created_at
        datetime updated_at
    }

    DATA_PARTISIPASI_POLITIK {
        int id_partisipasi PK
        int id_kecamatan FK
        int tahun
        int dpt
        int pengguna_hak_pilih
        float partisipasi_politik
        string sumber_data
        datetime created_at
        datetime updated_at
    }

    HASIL_PREDIKSI {
        int id_prediksi PK
        int id_kecamatan FK
        int tahun
        float tingkat_pendidikan
        float pendapatan_per_kapita
        float tingkat_pengangguran
        float kepadatan_penduduk
        float ipm
        float hasil_prediksi
        datetime created_at
    }

    MODEL_EVALUASI {
        int id_evaluasi PK
        string nama_model
        float rmse
        float r2_score
        int jumlah_data
        int jumlah_training
        int jumlah_testing
        datetime tanggal_evaluasi
    }

    KECAMATAN ||--o{ DATA_SOSIO_EKONOMI : "memiliki"
    KECAMATAN ||--o{ DATA_PARTISIPASI_POLITIK : "memiliki"
    KECAMATAN ||--o{ HASIL_PREDIKSI : "memiliki"
```

---

## 2. Penjelasan Relasi ERD
1. **KECAMATAN ke DATA_SOSIO_EKONOMI (One-to-Many)**: Satu kecamatan dapat memiliki banyak data sosio-ekonomi dari tahun yang berbeda. Setiap baris di `DATA_SOSIO_EKONOMI` wajib merujuk pada satu `id_kecamatan` yang valid.
2. **KECAMATAN ke DATA_PARTISIPASI_POLITIK (One-to-Many)**: Satu kecamatan memiliki banyak data partisipasi pemilu dari tahun ke tahun. Kolom `id_kecamatan` menjadi kunci tamu (*foreign key*) yang menghubungkan data.
3. **KECAMATAN ke HASIL_PREDIKSI (One-to-Many, Opsional)**: Satu kecamatan dapat memiliki banyak log riwayat prediksi. Relasi ini bersifat opsional (`id_kecamatan` boleh bernilai kosong/NULL apabila pengguna melakukan prediksi tanpa memilih kecamatan tertentu).
4. **MODEL_EVALUASI (Berdiri Sendiri / Standalone)**: Tabel ini tidak memiliki hubungan langsung (*foreign key*) dengan tabel kecamatan, karena menyimpan log evaluasi model Random Forest yang dilatih secara agregat menggunakan seluruh data dari VIEW gabungan.
