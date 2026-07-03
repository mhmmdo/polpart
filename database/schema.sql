CREATE TABLE IF NOT EXISTS kecamatan (
    id_kecamatan INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_kecamatan TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS data_sosio_ekonomi (
    id_sosio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_kecamatan INTEGER NOT NULL,
    tahun INTEGER NOT NULL,
    tingkat_pendidikan REAL,
    pendapatan_per_kapita REAL,
    tingkat_pengangguran REAL,
    kepadatan_penduduk REAL,
    ipm REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_kecamatan) REFERENCES kecamatan(id_kecamatan),
    UNIQUE(id_kecamatan, tahun)
);

CREATE TABLE IF NOT EXISTS data_partisipasi_politik (
    id_partisipasi INTEGER PRIMARY KEY AUTOINCREMENT,
    id_kecamatan INTEGER NOT NULL,
    tahun INTEGER NOT NULL,
    dpt INTEGER,
    pengguna_hak_pilih INTEGER,
    partisipasi_politik REAL,
    sumber_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_kecamatan) REFERENCES kecamatan(id_kecamatan),
    UNIQUE(id_kecamatan, tahun)
);

CREATE TABLE IF NOT EXISTS hasil_prediksi (
    id_prediksi INTEGER PRIMARY KEY AUTOINCREMENT,
    id_kecamatan INTEGER,
    tahun INTEGER,
    tingkat_pendidikan REAL NOT NULL,
    pendapatan_per_kapita REAL NOT NULL,
    tingkat_pengangguran REAL NOT NULL,
    kepadatan_penduduk REAL NOT NULL,
    ipm REAL NOT NULL,
    hasil_prediksi REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_kecamatan) REFERENCES kecamatan(id_kecamatan)
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
    se.tahun,
    k.nama_kecamatan AS kecamatan,
    se.tingkat_pendidikan,
    se.pendapatan_per_kapita,
    se.tingkat_pengangguran,
    se.kepadatan_penduduk,
    se.ipm,
    pp.partisipasi_politik
FROM data_sosio_ekonomi se
JOIN kecamatan k ON se.id_kecamatan = k.id_kecamatan
LEFT JOIN data_partisipasi_politik pp
    ON pp.id_kecamatan = se.id_kecamatan
    AND pp.tahun = se.tahun;
