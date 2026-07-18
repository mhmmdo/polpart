-- ====================================================================
-- TABEL MASTER DATA (MINIMAL 7 TABEL)
-- ====================================================================

-- 1. Master Pengguna (User)
CREATE TABLE IF NOT EXISTS pengguna (
    id_pengguna INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- 'admin' atau 'user'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. Master Kecamatan
CREATE TABLE IF NOT EXISTS kecamatan (
    id_kecamatan INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_kecamatan TEXT NOT NULL UNIQUE
);

-- 3. Master Kelurahan (Berelasi ke Kecamatan)
CREATE TABLE IF NOT EXISTS kelurahan (
    id_kelurahan INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_kelurahan TEXT NOT NULL UNIQUE,
    id_kecamatan INTEGER,
    FOREIGN KEY (id_kecamatan) REFERENCES kecamatan(id_kecamatan) ON DELETE CASCADE
);

-- 4. Master TPS (Berelasi ke Kelurahan)
CREATE TABLE IF NOT EXISTS tps (
    id_tps INTEGER PRIMARY KEY AUTOINCREMENT,
    no_tps TEXT NOT NULL,
    id_kelurahan INTEGER,
    FOREIGN KEY (id_kelurahan) REFERENCES kelurahan(id_kelurahan) ON DELETE CASCADE
);

-- 5. Master Dapil (Daerah Pemilihan)
CREATE TABLE IF NOT EXISTS dapil (
    id_dapil INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_dapil TEXT NOT NULL UNIQUE,
    wilayah_cakupan TEXT
);

-- 6. Master Partai Politik
CREATE TABLE IF NOT EXISTS partai (
    id_partai INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_partai TEXT NOT NULL UNIQUE,
    singkatan TEXT NOT NULL UNIQUE,
    nomor_urut INTEGER
);

-- 7. Master Pemilu (Periode Pemilu)
CREATE TABLE IF NOT EXISTS pemilu (
    id_pemilu INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_pemilu INTEGER NOT NULL UNIQUE,
    jenis_pemilu TEXT DEFAULT 'Pileg & Pilpres',
    status_aktif INTEGER DEFAULT 0 -- 1 jika aktif, 0 jika tidak
);


-- ====================================================================
-- TABEL TRANSAKSI / LOG DATA (MINIMAL 5 TABEL / VARIAN)
-- ====================================================================

-- 1. Transaksi Partisipasi TPS
CREATE TABLE IF NOT EXISTS data_partisipasi_tps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_pemilu INTEGER NOT NULL,
    level_data TEXT DEFAULT 'tps',
    kecamatan TEXT NOT NULL,
    kelurahan TEXT NOT NULL,
    no_tps TEXT NOT NULL,
    id_record TEXT,
    dpt INTEGER,
    pengguna_hak_pilih INTEGER,
    partisipasi_politik REAL,
    dpt_total_tps INTEGER,
    penduduk_total_kelurahan TEXT,
    penduduk_total_kecamatan INTEGER,
    rasio_dpt_terhadap_penduduk_kelurahan REAL,
    pendapatan_per_kapita REAL,
    tingkat_pengangguran REAL,
    kepadatan_penduduk REAL,
    ipm REAL,
    jumlah_usia_17_24_kec INTEGER,
    jumlah_usia_25_44_kec INTEGER,
    jumlah_usia_45_plus_kec INTEGER,
    persen_usia_17_24_kec REAL,
    persen_usia_25_44_kec REAL,
    persen_usia_45_plus_kec REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 2. Transaksi Partisipasi Agregat Historis
CREATE TABLE IF NOT EXISTS data_partisipasi_agregat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_pemilu INTEGER,
    level_data TEXT DEFAULT 'agregat',
    dapil TEXT,
    kecamatan TEXT,
    dpt_total INTEGER,
    pengguna_total INTEGER,
    partisipasi_politik REAL,
    sumber_data TEXT,
    catatan TEXT
);

-- 3. Transaksi Log Hasil Prediksi (Simulasi Pengguna)
CREATE TABLE IF NOT EXISTS hasil_prediksi (
    id_prediksi INTEGER PRIMARY KEY AUTOINCREMENT,
    kecamatan TEXT,
    kelurahan TEXT,
    no_tps TEXT,
    dpt INTEGER,
    rasio_dpt_terhadap_penduduk_kelurahan REAL,
    pendapatan_per_kapita REAL,
    tingkat_pengangguran REAL,
    kepadatan_penduduk REAL,
    ipm REAL,
    persen_usia_17_24_kec REAL,
    persen_usia_25_44_kec REAL,
    persen_usia_45_plus_kec REAL,
    hasil_prediksi REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 4. Transaksi Log Model Evaluasi (Training Random Forest)
CREATE TABLE IF NOT EXISTS model_evaluasi (
    id_evaluasi INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_model TEXT NOT NULL,
    rmse REAL,
    mae REAL,
    r2_score REAL,
    jumlah_data INTEGER,
    jumlah_training INTEGER,
    jumlah_testing INTEGER,
    tanggal_evaluasi TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 5. Transaksi Perolehan Suara Partai per TPS (Varian Transaksi Tambahan)
CREATE TABLE IF NOT EXISTS suara_partai_tps (
    id_suara INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tps INTEGER,
    id_partai INTEGER,
    jumlah_suara INTEGER DEFAULT 0,
    FOREIGN KEY (id_tps) REFERENCES tps(id_tps) ON DELETE CASCADE,
    FOREIGN KEY (id_partai) REFERENCES partai(id_partai) ON DELETE CASCADE
);


-- ====================================================================
-- VIEWS
-- ====================================================================

-- View Dataset Final untuk Kebutuhan Model Machine Learning
DROP VIEW IF EXISTS dataset_final;
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
FROM data_partisipasi_tps;

-- View Laporan Partisipasi Politik (Memenuhi Ketentuan C: minimal 5 atribut dan >1000 data)
DROP VIEW IF EXISTS laporan_partisipasi_politik;
CREATE VIEW laporan_partisipasi_politik AS
SELECT 
    id AS id_laporan,
    tahun_pemilu AS tahun_pemilu,
    kecamatan AS nama_kecamatan,
    kelurahan AS nama_kelurahan,
    no_tps AS nomor_tps,
    dpt AS jumlah_dpt,
    pengguna_hak_pilih AS hak_pilih_digunakan,
    partisipasi_politik AS persentase_partisipasi,
    ipm AS indeks_pembangunan_manusia,
    kepadatan_penduduk AS kepadatan_penduduk
FROM data_partisipasi_tps;
