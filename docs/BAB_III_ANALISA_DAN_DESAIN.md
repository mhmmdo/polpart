# BAB III: Analisa dan Desain Sistem

Bab ini membahas analisis kebutuhan sistem, pemodelan sistem menggunakan diagram UML, perancangan basis data, serta perancangan antarmuka untuk aplikasi **PolPart RF (Prediksi Partisipasi Politik Berbasis Random Forest)**.

---

## 3.1 Analisis Kebutuhan Sistem
Analisis kebutuhan dilakukan untuk memetakan apa saja fungsionalitas yang harus dipenuhi oleh sistem guna membantu operator KPU dan masyarakat umum.

### 3.1.1 Kebutuhan Fungsional (Functional Requirements)
1. **Sistem Autentikasi**:
   - Sistem wajib menyediakan halaman pendaftaran akun (*Register*) untuk pengguna baru.
   - Sistem wajib membatasi akses aplikasi menggunakan halaman masuk (*Login*) dengan verifikasi sandi aman SHA-256.
   - Sistem harus memiliki dua peran (*role*): Admin (Operator KPU) dan User (Masyarakat).
2. **Manajemen Data (Tingkat TPS)**:
   - Admin dapat mengunggah (*upload*) berkas CSV pemilu tingkat TPS (>1800 baris data).
   - Sistem harus membersihkan dan menyimpan data secara otomatis ke basis data SQLite.
   - Tamu/User umum hanya diizinkan membaca tabel tanpa hak edit/unggah.
3. **Simulasi Prediksi Random Forest**:
   - Pengguna (Admin dan User) dapat memasukkan nilai demografi (DPT, Rasio DPT Kelurahan, persentase usia 17-24, 25-44, dan 45+).
   - Sistem memanggil model Random Forest untuk menampilkan perkiraan tingkat partisipasi politik.
   - Riwayat simulasi tersimpan ke database secara otomatis.
4. **Pelaporan & Ekspor Data**:
   - Sistem dapat mencetak laporan rekapitulasi simulasi prediksi dalam bentuk **berkas PDF**.
   - Berkas PDF memuat parameter input, hasil prediksi, performa model statistik (RMSE & R²), dan identitas pencetak.
5. **Visualisasi Interaktif**:
   - Sistem wajib menampilkan ringkasan metrik statistik (rata-rata, tertinggi, terendah).
   - Sistem menyajikan diagram tren partisipasi tahunan, perbandingan kecamatan, heatmap korelasi, dan peta spasial (*choropleth*) berbasis GeoJSON.

### 3.1.2 Kebutuhan Non-Fungsional (Non-Functional Requirements)
1. **Usability**: Antarmuka bertema terang (*light mode*) dengan warna latar belakang soft mint (`#eaf8f8`), kartu putih (`#ffffff`), dan aksen warna coral (`#ff7f66`) untuk kenyamanan mata pengguna non-IT.
2. **Security**: Sandi akun pengguna di-hash dengan SHA-256 sebelum disimpan ke SQLite.
3. **Availability**: Aplikasi dapat dideploy ke VPS berbasis Linux Ubuntu Server menggunakan Apache Reverse Proxy dan systemd agar berjalan stabil 24/7.

---

## 3.2 Pemodelan Sistem (Diagram UML)

### 3.2.1 Use Case Diagram
Sistem memiliki 2 aktor utama dengan detail fungsionalitas berikut:
- **Operator KPU (Admin)**: Melakukan pendaftaran akun, login, melihat dashboard, visualisasi, melakukan prediksi, mengunduh PDF, mengimpor berkas CSV data TPS, dan memicu training ulang model.
- **Masyarakat (User)**: Melakukan pendaftaran akun, login, melihat dashboard, visualisasi, melakukan prediksi, dan mengunduh PDF.

*(Detail gambar diagram Use Case dapat dilihat pada berkas [USE_CASE_DIAGRAM.md](file:///d:/TA/polpart/docs/USE_CASE_DIAGRAM.md))*

### 3.2.2 Flowchart Sistem
Alur proses sistem dimulai dari pemeriksaan status login. Pengguna yang belum terautentikasi diarahkan ke form Login/Register. Setelah login, sistem memuat menu navigasi utama. Menu Prediksi memungkinkan pengisian form, kalkulasi regresi Random Forest, penyimpanan log, dan pembuatan laporan PDF instan menggunakan modul `fpdf2`. Menu Data Historis pada akun Admin menyediakan widget impor CSV untuk mengganti/memperbarui database.

*(Detail gambar diagram alur dapat dilihat pada berkas [FLOWCHART_SISTEM.md](file:///d:/TA/polpart/docs/FLOWCHART_SISTEM.md))*

---

## 3.3 Perancangan Basis Data (Database Design)
Basis data dirancang menggunakan SQLite (`polpart.db`) dengan skema tabel utama:
1. `pengguna`: Kredensial akun dan perannya (Admin/User).
2. `kecamatan`: Daftar wilayah administratif.
3. `data_partisipasi_tps`: Data utama pemilu level TPS untuk input training model.
4. `hasil_prediksi`: Log histori simulasi yang dilakukan.
5. `model_evaluasi`: Catatan performa statistik model regresi.

*(Detail struktur kolom dan relasi data dapat dilihat pada berkas [RANCANGAN_DATABASE.md](file:///d:/TA/polpart/docs/RANCANGAN_DATABASE.md) dan [ERD.md](file:///d:/TA/polpart/docs/ERD.md))*
