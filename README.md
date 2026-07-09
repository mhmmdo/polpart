# Sistem Analisa dan Prediksi Partisipasi Politik (PolPart RF)

Aplikasi web berbasis **Streamlit** dan **Machine Learning (Random Forest)** untuk menganalisis, memetakan, dan memprediksi persentase tingkat partisipasi politik masyarakat Kota Banjarmasin pada tingkat Tempat Pemungutan Suara (TPS).

Sistem menggunakan database relasional lokal **SQLite** untuk menyimpan seluruh data pemilu, log hasil prediksi, riwayat evaluasi model, serta tabel kredensial pengguna untuk sistem autentikasi masuk.

---

## 📂 Struktur Direktori

```text
polpart/
├── app.py                      # Main entrypoint aplikasi web (Tab Login/Register & routing)
├── requirements.txt            # Daftar dependensi library Python
├── database/
│   ├── polpart.db              # Database SQLite lokal (berisi data riil & akun pengguna)
│   └── schema.sql              # Rancangan skema tabel DDL SQLite
├── data/
│   ├── import/
│   │   └── data_final_template.csv  # Template format kolom CSV untuk upload
│   ├── raw/
│   │   └── data_partisipasi_per_tps.csv # Dataset riil pemilu 2024 (1.838 baris TPS)
│   └── geo/
│       └── kecamatan_5.geojson # Batas wilayah geografis koordinat kecamatan
├── docs/                       # Berkas draf laporan akademis Tugas Akhir (TA/PKL)
│   ├── README_SISTEM.md        # Indeks dokumentasi
│   ├── FLOWCHART_SISTEM.md     # Flowchart alur sistem detail per fitur
│   ├── USE_CASE_DIAGRAM.md     # Diagram Use Case (Admin vs User)
│   ├── RANCANGAN_DATABASE.md   # Skema kolom basis data SQLite
│   ├── ERD.md                  # Entity Relationship Diagram (Mermaid)
│   └── BAB_III_ANALISA_DAN_DESAIN.md # Draf Bab III Tugas Akhir
├── src/                        # Modul penggerak logika (Back-end)
│   ├── config.py               # Pengaturan konfigurasi, nama variabel, dan hyperparameter
│   ├── database.py             # Konektor, CRUD SQLite, dan hash SHA-256 sandi
│   ├── data_loader.py          # Loader data & penyiapan dataset siap latih
│   ├── model.py                # Pelatihan model Random Forest Regressor & fungsi hitung prediksi
│   ├── ui.py                   # UI helper, validasi peran sidebar, dan impor file CSV
│   ├── utils.py                # Utilitas kecil (persentase, pembulatan, summary)
│   ├── visualizations.py       # Visualisasi grafik interaktif Plotly & peta choropleth
│   └── pdf_generator.py        # Pembuat laporan rekapitulasi PDF menggunakan fpdf2
├── scripts/                    # Skrip CLI untuk inisialisasi & pemeliharaan model
│   ├── init_db.py              # Inisialisasi DB, seeding default, dan impor otomatis data TPS
│   ├── import_tps_csv.py       # Skrip penarik baris CSV ke tabel SQLite
│   └── train_model.py          # Skrip manual untuk pelatihan & penyimpanan model (.joblib)
└── models/                     # Tempat penyimpanan biner model terlatih (.joblib)
```

---

## 🔑 Akun Default Sistem
Tersedia dua peran pengguna bawaan yang dibuat otomatis saat inisialisasi database:

1. **Operator KPU (Admin)**:
   * **Username**: `admin`
   * **Password**: `admin123`
   * **Hak Akses**: Dapat melihat visualisasi, melakukan simulasi prediksi, mendownload PDF, mengunggah file CSV baru di sidebar, dan melatih ulang model secara otomatis.
   
2. **Masyarakat (User)**:
   * **Username**: `user`
   * **Password**: `user123`
   * **Hak Akses**: Dapat melihat visualisasi, melakukan simulasi prediksi, mendownload PDF, tetapi **tidak diizinkan** mengunggah file CSV.

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Kloning dan Masuk ke Folder Proyek
```bash
git clone https://github.com/mhmmdo/polpart.git
cd polpart
```

### 2. Pasang Dependensi
Pastikan python 3.9+ terinstal. Sangat disarankan menggunakan virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Instalasi Library
pip install -r requirements.txt
```

### 3. Inisialisasi Database Pertama Kali
Jalankan skrip berikut untuk membuat file database, menetapkan skema tabel, melakukan seeding akun admin/user bawaan, dan mengimpor 1.838 baris dataset TPS pemilu 2024:
```bash
python scripts/init_db.py
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```
Aplikasi web akan terbuka otomatis di alamat `http://localhost:8501`.

---

## 📄 Pembuatan Laporan PDF
Sistem dilengkapi modul pembuatan laporan PDF berbasis `fpdf2` yang merangkum parameter masukan prediksi pengguna, estimasi hasil keluaran prediksi, performa statistik model acuan (R² & RMSE), nama akun pencetak, serta stempel waktu cetak dalam tata letak yang rapi dan profesional.
