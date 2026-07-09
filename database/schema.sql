CREATE TABLE IF NOT EXISTS kecamatan (
    id_kecamatan INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_kecamatan TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pengguna (
    id_pengguna INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- 'admin' atau 'user'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

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
FROM data_partisipasi_tps
WHERE tahun_pemilu = 2024;
