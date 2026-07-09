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
                id, tahun_pemilu, kecamatan, kelurahan, no_tps, id_record, jenis_kelamin,
                dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                penduduk_total_kelurahan, rasio_dpt_terhadap_penduduk_kelurahan,
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
                tahun_pemilu, kecamatan, kelurahan, no_tps, id_record, jenis_kelamin,
                dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                penduduk_total_kelurahan, rasio_dpt_terhadap_penduduk_kelurahan,
                persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('tahun_pemilu'),
            data.get('kecamatan', '').strip().upper(),
            data.get('kelurahan', '').strip().upper(),
            data.get('no_tps', '').strip(),
            data.get('id_record'),
            data.get('jenis_kelamin', 'JML'),
            dpt,
            pilih,
            partisipasi,
            data.get('dpt_total_tps'),
            data.get('penduduk_total_kelurahan'),
            data.get('rasio_dpt_terhadap_penduduk_kelurahan'),
            data.get('persen_usia_17_24_kec'),
            data.get('persen_usia_25_44_kec'),
            data.get('persen_usia_45_plus_kec')
        ))
        conn.commit()

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
                kecamatan, kelurahan, no_tps, dpt, rasio_dpt,
                usia_17_24, usia_25_44, usia_45_plus, hasil_prediksi, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('kecamatan'),
            data.get('kelurahan'),
            data.get('no_tps'),
            data.get('dpt'),
            data.get('rasio_dpt'),
            data.get('usia_17_24'),
            data.get('usia_25_44'),
            data.get('usia_45_plus'),
            data.get('hasil_prediksi')
        ))
        conn.commit()

def get_prediction_history() -> pd.DataFrame:
    """Retrieves all prediction logs."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                id_prediksi, kecamatan, kelurahan, no_tps, dpt, rasio_dpt,
                usia_17_24, usia_25_44, usia_45_plus, hasil_prediksi, created_at
            FROM hasil_prediksi
            ORDER BY created_at DESC
        """, conn)

def save_model_evaluation(data: dict):
    """Saves model evaluation scores after training."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_evaluasi (
                nama_model, rmse, r2_score, jumlah_data, jumlah_training, jumlah_testing
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['nama_model'],
            data.get('rmse'),
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
