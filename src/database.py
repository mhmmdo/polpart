import sqlite3
import os
import pandas as pd
from src.config import DB_PATH

def get_connection():
    """Returns a sqlite3 connection to the local database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def database_exists() -> bool:
    """Helper to check if the database file exists and contains TPS records."""
    if not DB_PATH.exists():
        return False
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_partisipasi_tps'")
            if not cursor.fetchone():
                return False
            cursor.execute("SELECT COUNT(*) FROM data_partisipasi_tps")
            count = cursor.fetchone()[0]
            return count >= 1000
    except Exception:
        return False

def init_database():
    """Initializes the database schema using the schema.sql file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    schema_path = DB_PATH.parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
    with get_connection() as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()

def seed_kecamatan():
    """Seeds default kecamatan list into the kecamatan table."""
    default_kecamatan = [
        "BANJARMASIN SELATAN",
        "BANJARMASIN TIMUR",
        "BANJARMASIN BARAT",
        "BANJARMASIN TENGAH",
        "BANJARMASIN UTARA"
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for name in default_kecamatan:
            cursor.execute("""
                INSERT OR IGNORE INTO kecamatan (nama_kecamatan) VALUES (?)
            """, (name.upper(),))
        conn.commit()

def get_kecamatan_id_by_name(conn, name: str) -> int:
    """Finds or inserts a kecamatan by name and returns its ID."""
    name_clean = name.strip().upper()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kecamatan FROM kecamatan WHERE nama_kecamatan = ?", (name_clean,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    cursor.execute("INSERT INTO kecamatan (nama_kecamatan) VALUES (?)", (name_clean,))
    conn.commit()
    return cursor.lastrowid

def get_all_kecamatan() -> pd.DataFrame:
    """Retrieves all kecamatan rows from the database."""
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM kecamatan ORDER BY nama_kecamatan ASC", conn)

def get_dataset_final() -> pd.DataFrame:
    """Retrieves the full dataset from the dataset_final view."""
    with get_connection() as conn:
        return pd.read_sql_query("SELECT * FROM dataset_final ORDER BY tahun DESC, kecamatan ASC", conn)

def get_tps_data() -> pd.DataFrame:
    """Retrieves all raw TPS records from the database."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                id, tahun_pemilu, level_data, kecamatan, kelurahan, no_tps, id_record,
                dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                penduduk_total_kelurahan, penduduk_total_kecamatan, rasio_dpt_terhadap_penduduk_kelurahan,
                pendapatan_per_kapita, tingkat_pengangguran, kepadatan_penduduk, ipm,
                jumlah_usia_17_24_kec, jumlah_usia_25_44_kec, jumlah_usia_45_plus_kec,
                persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec,
                created_at
            FROM data_partisipasi_tps
            ORDER BY kecamatan ASC, kelurahan ASC, no_tps ASC
        """, conn)

def insert_or_update_tps_data(data: dict):
    """Inserts a new record or updates it in data_partisipasi_tps."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Calculate participation rate automatically if needed
        partisipasi = data.get('partisipasi_politik')
        dpt = data.get('dpt')
        pilih = data.get('pengguna_hak_pilih')
        if partisipasi is None and dpt and pilih:
            partisipasi = (float(pilih) / float(dpt)) * 100.0
            
        cursor.execute("""
            INSERT INTO data_partisipasi_tps (
                tahun_pemilu, level_data, kecamatan, kelurahan, no_tps, id_record,
                dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                penduduk_total_kelurahan, penduduk_total_kecamatan, rasio_dpt_terhadap_penduduk_kelurahan,
                pendapatan_per_kapita, tingkat_pengangguran, kepadatan_penduduk, ipm,
                jumlah_usia_17_24_kec, jumlah_usia_25_44_kec, jumlah_usia_45_plus_kec,
                persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('tahun_pemilu'),
            data.get('level_data', 'tps'),
            data.get('kecamatan', '').strip().upper(),
            data.get('kelurahan', '').strip().upper(),
            data.get('no_tps', '').strip(),
            data.get('id_record'),
            dpt,
            pilih,
            partisipasi,
            data.get('dpt_total_tps'),
            data.get('penduduk_total_kelurahan'),
            data.get('penduduk_total_kecamatan'),
            data.get('rasio_dpt_terhadap_penduduk_kelurahan'),
            data.get('pendapatan_per_kapita'),
            data.get('tingkat_pengangguran'),
            data.get('kepadatan_penduduk'),
            data.get('ipm'),
            data.get('jumlah_usia_17_24_kec'),
            data.get('jumlah_usia_25_44_kec'),
            data.get('jumlah_usia_45_plus_kec'),
            data.get('persen_usia_17_24_kec'),
            data.get('persen_usia_25_44_kec'),
            data.get('persen_usia_45_plus_kec')
        ))
        conn.commit()

def insert_data_agregat(data: dict):
    """Inserts a record into data_partisipasi_agregat."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO data_partisipasi_agregat (
                tahun_pemilu, level_data, dapil, kecamatan, dpt_total,
                pengguna_total, partisipasi_politik, sumber_data, catatan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('tahun_pemilu'),
            data.get('level_data', 'agregat'),
            data.get('dapil'),
            data.get('kecamatan', '').strip().upper(),
            data.get('dpt_total'),
            data.get('pengguna_total'),
            data.get('partisipasi_politik'),
            data.get('sumber_data'),
            data.get('catatan')
        ))
        conn.commit()

def get_dataset_2019_agregat() -> pd.DataFrame:
    """Retrieves all 2019 aggregated records from database."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT * FROM data_partisipasi_agregat
            WHERE tahun_pemilu = 2019
            ORDER BY kecamatan ASC
        """, conn)

def delete_tps_data(id_tps: int):
    """Deletes a TPS record by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data_partisipasi_tps WHERE id = ?", (id_tps,))
        conn.commit()

def save_prediction(data: dict):
    """Saves a model prediction scenario into hasil_prediksi table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hasil_prediksi (
                kecamatan, kelurahan, no_tps, dpt, rasio_dpt_terhadap_penduduk_kelurahan,
                pendapatan_per_kapita, tingkat_pengangguran, kepadatan_penduduk, ipm,
                persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec,
                hasil_prediksi, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('kecamatan'),
            data.get('kelurahan'),
            data.get('no_tps'),
            data.get('dpt'),
            data.get('rasio_dpt_terhadap_penduduk_kelurahan'),
            data.get('pendapatan_per_kapita'),
            data.get('tingkat_pengangguran'),
            data.get('kepadatan_penduduk'),
            data.get('ipm'),
            data.get('persen_usia_17_24_kec'),
            data.get('persen_usia_25_44_kec'),
            data.get('persen_usia_45_plus_kec'),
            data.get('hasil_prediksi')
        ))
        conn.commit()

def get_prediction_history() -> pd.DataFrame:
    """Retrieves all prediction logs."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                id_prediksi, kecamatan, kelurahan, no_tps, dpt, rasio_dpt_terhadap_penduduk_kelurahan,
                pendapatan_per_kapita, tingkat_pengangguran, kepadatan_penduduk, ipm,
                persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec,
                hasil_prediksi, created_at
            FROM hasil_prediksi
            ORDER BY created_at DESC
        """, conn)

def save_model_evaluation(data: dict):
    """Saves model evaluation scores after training."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_evaluasi (
                nama_model, rmse, mae, r2_score, jumlah_data, jumlah_training, jumlah_testing
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['nama_model'],
            data.get('rmse'),
            data.get('mae'),
            data.get('r2_score'),
            data.get('jumlah_data'),
            data.get('jumlah_training'),
            data.get('jumlah_testing')
        ))
        conn.commit()

def seed_admin():
    """Seeds the default admin and user credentials into database if table is empty."""
    import hashlib
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Admin default: admin / admin123
        admin_hash = hashlib.sha256(b"admin123").hexdigest()
        cursor.execute("""
            INSERT OR IGNORE INTO pengguna (username, password_hash, role) VALUES (?, ?, ?)
        """, ("admin", admin_hash, "admin"))
        
        # User default: user / user123
        user_hash = hashlib.sha256(b"user123").hexdigest()
        cursor.execute("""
            INSERT OR IGNORE INTO pengguna (username, password_hash, role) VALUES (?, ?, ?)
        """, ("user", user_hash, "user"))
        
        conn.commit()

def check_login(username, password) -> dict or None:
    """Verifies user credentials using SHA-256 and returns role details if valid."""
    import hashlib
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, role FROM pengguna WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        row = cursor.fetchone()
        if row:
            return {"username": row[0], "role": row[1]}
        return None

def register_user(username, password, role) -> bool:
    """Registers a new user into the database."""
    import hashlib
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pengguna (username, password_hash, role) VALUES (?, ?, ?)
            """, (username.strip(), password_hash, role))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def seed_dapil():
    """Seeds default dapil list into the dapil table."""
    dapils = [
        ("BANJARMASIN 1", "Kecamatan Banjarmasin Tengah"),
        ("BANJARMASIN 2", "Kecamatan Banjarmasin Utara"),
        ("BANJARMASIN 3", "Kecamatan Banjarmasin Timur"),
        ("BANJARMASIN 4", "Kecamatan Banjarmasin Selatan"),
        ("BANJARMASIN 5", "Kecamatan Banjarmasin Barat")
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for nama, wilayah in dapils:
            cursor.execute("""
                INSERT OR IGNORE INTO dapil (nama_dapil, wilayah_cakupan) VALUES (?, ?)
            """, (nama, wilayah))
        conn.commit()

def seed_partai():
    """Seeds major political parties into the partai table."""
    partai_list = [
        ("Partai Kebangkitan Bangsa", "PKB", 1),
        ("Partai Gerakan Indonesia Raya", "GERINDRA", 2),
        ("Partai Demokrasi Indonesia Perjuangan", "PDIP", 3),
        ("Partai Golongan Karya", "GOLKAR", 4),
        ("Partai NasDem", "NASDEM", 5),
        ("Partai Buruh", "BURUH", 6),
        ("Partai Gelombang Rakyat Indonesia", "GELORA", 7),
        ("Partai Keadilan Sejahtera", "PKS", 8),
        ("Partai Kebangkitan Nusantara", "PKN", 9),
        ("Partai Hati Nurani Rakyat", "HANURA", 10),
        ("Partai Garda Republik Indonesia", "GARUDA", 11),
        ("Partai Amanat Nasional", "PAN", 12),
        ("Partai Bulan Bintang", "PBB", 13),
        ("Partai Demokrat", "DEMOKRAT", 14),
        ("Partai Solidaritas Indonesia", "PSI", 15),
        ("Partai Perindo", "PERINDO", 16),
        ("Partai Persatuan Pembangunan", "PPP", 17),
        ("Partai Ummat", "UMMAT", 24)
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for nama, singkatan, no_urut in partai_list:
            cursor.execute("""
                INSERT OR IGNORE INTO partai (nama_partai, singkatan, nomor_urut) VALUES (?, ?, ?)
            """, (nama, singkatan, no_urut))
        conn.commit()

def seed_pemilu():
    """Seeds election periods into the pemilu table."""
    pemilu_list = [
        (2019, "Pemilu Serentak 2019 (Pileg & Pilpres)", 0),
        (2024, "Pemilu Serentak 2024 (Pileg & Pilpres)", 1)
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for tahun, jenis, status in pemilu_list:
            cursor.execute("""
                INSERT OR IGNORE INTO pemilu (tahun_pemilu, jenis_pemilu, status_aktif) VALUES (?, ?, ?)
            """, (tahun, jenis, status))
        conn.commit()

def seed_relational_tables_from_tps():
    """Extracts unique kelurahan and tps from data_partisipasi_tps, and inserts them into master tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Populate kelurahan
        cursor.execute("SELECT DISTINCT kecamatan, kelurahan FROM data_partisipasi_tps")
        rows = cursor.fetchall()
        for kec_name, kel_name in rows:
            cursor.execute("SELECT id_kecamatan FROM kecamatan WHERE nama_kecamatan = ?", (kec_name.strip().upper(),))
            kec_row = cursor.fetchone()
            kec_id = kec_row[0] if kec_row else None
            if kec_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO kelurahan (nama_kelurahan, id_kecamatan) VALUES (?, ?)
                """, (kel_name.strip().upper(), kec_id))
        conn.commit()
        
        # 2. Populate tps
        cursor.execute("SELECT DISTINCT kelurahan, no_tps FROM data_partisipasi_tps")
        tps_rows = cursor.fetchall()
        for kel_name, no_tps in tps_rows:
            cursor.execute("SELECT id_kelurahan FROM kelurahan WHERE nama_kelurahan = ?", (kel_name.strip().upper(),))
            kel_row = cursor.fetchone()
            kel_id = kel_row[0] if kel_row else None
            if kel_id:
                cursor.execute("SELECT id_tps FROM tps WHERE no_tps = ? AND id_kelurahan = ?", (no_tps.strip(), kel_id))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO tps (no_tps, id_kelurahan) VALUES (?, ?)
                    """, (no_tps.strip(), kel_id))
        conn.commit()
        
        # 3. Populate suara_partai_tps with mock votes for Indonesian political parties
        cursor.execute("SELECT id_tps FROM tps")
        tps_ids = [r[0] for r in cursor.fetchall()]
        
        cursor.execute("SELECT id_partai FROM partai")
        partai_ids = [r[0] for r in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM suara_partai_tps")
        exist_count = cursor.fetchone()[0]
        if exist_count == 0 and tps_ids and partai_ids:
            suara_data = []
            for t_id in tps_ids[:100]: # Seed for first 100 TPS to keep it fast
                for p_id in partai_ids:
                    jumlah_suara = (t_id * p_id + 7) % 45
                    suara_data.append((t_id, p_id, jumlah_suara))
            
            cursor.executemany("""
                INSERT INTO suara_partai_tps (id_tps, id_partai, jumlah_suara) VALUES (?, ?, ?)
            """, suara_data)
            conn.commit()
