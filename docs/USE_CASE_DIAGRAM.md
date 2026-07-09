# Analisis Use Case Diagram (Dua Aktor)

Dokumen ini mendeskripsikan rancangan **Use Case Diagram** untuk sistem PolPart RF yang melibatkan 2 (dua) aktor utama dengan hak akses yang berbeda.

---

## 1. Identifikasi Aktor (Actors)

1. **Admin (Operator KPU / Developer)**:
   * Pengguna internal yang bertanggung jawab atas validitas data pemilu.
   * Memiliki akses menulis (*write*) dan mengubah database melalui impor CSV.
   * Memiliki wewenang untuk melatih ulang (*retraining*) model Random Forest.
   
2. **User (Masyarakat / Tamu / Peneliti)**:
   * Pengguna publik/tamu yang menggunakan sistem untuk simulasi dan pembelajaran.
   * Memiliki akses baca (*read-only*) terhadap data historis, grafik korelasi, dan peta spasial.
   * Dapat melakukan simulasi prediksi dan mengunduh laporan PDF hasil prediksi.

---

## 2. Diagram Use Case (Mermaid format)

```mermaid
left-to-right-direction
actor Admin as "Operator KPU (Admin)"
actor User as "Masyarakat (User)"

rectangle "Sistem PolPart RF" {
    usecase UC1 as "Register Akun"
    usecase UC2 as "Login Sistem"
    usecase UC3 as "Melihat Dashboard & Statistik"
    usecase UC4 as "Melihat Grafik Visualisasi & Peta"
    usecase UC5 as "Melakukan Simulasi Prediksi"
    usecase UC6 as "Mengunduh Laporan PDF"
    usecase UC7 as "Mengelola Data TPS (Impor CSV)"
    usecase UC8 as "Melatih Ulang Model RF"
    usecase UC9 as "Logout Sistem"
}

Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC4
Admin --> UC5
Admin --> UC6
Admin --> UC7
Admin --> UC8
Admin --> UC9

User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC9
```

---

## 3. Definisi Use Case & Hak Akses

| ID Use Case | Nama Use Case | Deskripsi | Aktor yang Terlibat |
|---|---|---|---|
| **UC1** | Register Akun | Melakukan pendaftaran akun baru dengan mengisi username, password, dan memilih role (*admin*/*user*). | Admin, User |
| **UC2** | Login Sistem | Memvalidasi kredensial pengguna menggunakan SQLite untuk mengaktifkan session akses. | Admin, User |
| **UC3** | Melihat Dashboard & Statistik | Menampilkan rangkuman persentase partisipasi tertinggi/terendah dan rata-rata partisipasi politik TPS. | Admin, User |
| **UC4** | Melihat Grafik Visualisasi & Peta | Menampilkan heatmap korelasi antar variabel demografi dan peta choropleth kecamatan. | Admin, User |
| **UC5** | Melakukan Simulasi Prediksi | Memasukkan skenario parameter DPT dan demografi usia untuk memprediksi hasil partisipasi via model Random Forest. | Admin, User |
| **UC6** | Mengunduh Laporan PDF | Mengunduh hasil simulasi prediksi berupa berkas laporan PDF formal. | Admin, User |
| **UC7** | Mengelola Data TPS (Impor CSV) | Mengunggah berkas CSV data TPS pemilu tingkat kelurahan untuk memperbarui isi database SQLite. | **Hanya Admin** |
| **UC8** | Melatih Ulang Model RF | Memicu proses training algoritma model regresi Random Forest menggunakan data terbaru. | **Hanya Admin** |
| **UC9** | Logout Sistem | Mengakhiri session aktif dan mengarahkan kembali ke halaman login. | Admin, User |
