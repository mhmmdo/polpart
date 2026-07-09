# Flowchart Alur Sistem (PolPart RF)

Berikut adalah diagram alir (*flowchart*) logika bisnis aplikasi PolPart RF yang menggambarkan proses registrasi, autentikasi login, pemeriksaan hak akses, pemrosesan prediksi, serta pembuatan laporan PDF.

---

## 1. Diagram Alir Sistem (Mermaid format)

```mermaid
flowchart TD
    A([Mulai Aplikasi]) --> B{Sudah Login?}
    B -- Tidak --> C{Pilih Menu?}
    C -- Daftar Akun --> D[Isi Username, Password, & Pilih Role]
    D --> E[Simpan ke Tabel pengguna]
    E --> F[Registrasi Sukses] --> C
    
    C -- Masuk Login --> G[Masukkan Username & Password]
    G --> H{Cek Kredensial di SQLite?}
    H -- Salah --> I[Tampilkan Eror Akun] --> G
    H -- Benar --> J[Set Session State: logged_in, username, role]
    J --> K[Rerun & Masuk Halaman Utama]
    
    B -- Ya --> L{Pilih Menu Navigasi?}
    
    L -- Dashboard / Visualisasi --> M[Baca data_partisipasi_tps]
    M --> N[Tampilkan Visualisasi, Peta, & Statistik]
    
    L -- Prediksi --> O[Muat Model Random Forest]
    O --> P[Isi Form: DPT, Rasio, Usia 17-24, 25-44, 45+]
    P --> Q[Klik Tombol Lakukan Prediksi]
    Q --> R[Hitung Prediksi & Simpan ke hasil_prediksi]
    R --> S[Tampilkan Output Prediksi]
    S --> T[Sediakan Opsi Unduh Rekap PDF]
    T --> U[Unduh PDF Laporan via fpdf2]
    
    L -- Data Historis --> V{Role Pengguna?}
    V -- Admin / Operator --> W[Tampilkan Tabel TPS & Menu Impor CSV]
    W --> X[Unggah File CSV]
    X --> Y[Bersihkan Data & Simpan ke data_partisipasi_tps]
    Y --> Z[Latih Ulang Model RF]
    
    V -- User / Masyarakat --> AA[Tampilkan Tabel TPS saja]
    
    L -- Keluar / Logout --> AB[Clear Session State]
    AB --> AC[Rerun ke Halaman Login]
    
    N --> AD([Selesai])
    U --> AD
    Z --> AD
    AA --> AD
    AC --> AD
```

---

## 2. Penjelasan Alur Proses

### A. Alur Autentikasi (Registrasi & Login)
1. Aplikasi dimulai dengan memeriksa status session `logged_in`. Jika tidak aktif, pengguna dipaksa masuk ke halaman **Login / Register**.
2. Pengguna baru dapat mendaftar dengan menentukan username dan password, serta memilih perannya (*Admin* atau *User*).
3. Saat login, sandi dienkripsi dengan SHA-256 lalu dicocokkan dengan tabel `pengguna`. Jika valid, session state diaktifkan dan halaman utama dimuat.

### B. Alur Penentuan Peran (Role Checks)
* **Role Admin (Operator KPU)**: Memiliki wewenang untuk memperbarui dataset. Tombol pengunggah CSV di sidebar diaktifkan. Admin dapat memasukkan data baru yang secara otomatis memicu proses *retraining* model Random Forest agar tetap akurat.
* **Role User (Masyarakat)**: Hanya memiliki hak akses baca (*read-only*). Tombol uploader di sidebar disembunyikan dan diganti dengan teks informasi. User dapat melakukan simulasi prediksi dan mengunduh laporan PDF.

### C. Alur Prediksi & Ekspor PDF
1. Pengguna memasukkan skenario data demografi TPS yang ingin disimulasikan.
2. Model Random Forest menghitung hasil tebakan persentase partisipasi.
3. Hasil disimpan di tabel log `hasil_prediksi` dan disajikan secara visual.
4. Sistem memanggil modul `src/pdf_generator.py` untuk menyusun file PDF secara dinamis yang berisi rincian input, hasil prediksi, performa model, dan tanda tangan digital pengguna aktif.
