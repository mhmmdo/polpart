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
    kecamatan TEXT NOT NULL,
    kelurahan TEXT NOT NULL,
    no_tps TEXT NOT NULL,
    id_record TEXT,
    jenis_kelamin TEXT,
    dpt INTEGER,
    pengguna_hak_pilih INTEGER,
    partisipasi_politik REAL,
    dpt_total_tps INTEGER,
    penduduk_total_kelurahan TEXT,
    rasio_dpt_terhadap_penduduk_kelurahan REAL,
    persen_usia_17_24_kec REAL,
    persen_usia_25_44_kec REAL,
    persen_usia_45_plus_kec REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hasil_prediksi (
    id_prediksi INTEGER PRIMARY KEY AUTOINCREMENT,
    kecamatan TEXT,
    kelurahan TEXT,
    no_tps TEXT,
    dpt INTEGER,
    rasio_dpt REAL,
    usia_17_24 REAL,
    usia_25_44 REAL,
    usia_45_plus REAL,
    hasil_prediksi REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_evaluasi (
    id_evaluasi INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_model TEXT NOT NULL,
    rmse REAL,
    r2_score REAL,
    jumlah_data INTEGER,
    jumlah_training INTEGER,
    jumlah_testing INTEGER,
    tanggal_evaluasi TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW IF NOT EXISTS dataset_final AS
SELECT
    tahun_pemilu AS tahun,
    kecamatan,
    kelurahan,
    no_tps,
    dpt,
    pengguna_hak_pilih,
    partisipasi_politik,
    rasio_dpt_terhadap_penduduk_kelurahan,
    persen_usia_17_24_kec,
    persen_usia_25_44_kec,
    persen_usia_45_plus_kec
FROM data_partisipasi_tps;
