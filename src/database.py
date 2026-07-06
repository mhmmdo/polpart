"""
Modul yang berisi fungsi-fungsi untuk berinteraksi dengan database SQLite.
Menangani operasi CRUD (Create, Read, Update, Delete) untuk tabel-tabel:
- kecamatan
- data_sosio_ekonomi
- data_partisipasi_politik
- hasil_prediksi
- model_evaluasi
"""
import sqlite3
import os
import pandas as pd
from src.config import DB_PATH

def get_connection():
    """Returns a sqlite3 connection to the local database."""
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign keys support
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def database_exists() -> bool:
    """Helper to check if the database file exists and is seeded with kecamatan."""
    if not DB_PATH.exists():
        return False
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kecamatan'")
            if not cursor.fetchone():
                return False
            cursor.execute("SELECT COUNT(*) FROM kecamatan")
            count = cursor.fetchone()[0]
            return count > 0
    except Exception:
        return False

def init_database():
    """Initializes the database schema using the schema.sql file."""
    # Ensure directory exists
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
    """Seeds the default kecamatan if the table is empty."""
    default_kecamatan = [
        "Banjarmasin Selatan",
        "Banjarmasin Timur",
        "Banjarmasin Barat",
        "Banjarmasin Tengah",
        "Banjarmasin Utara"
    ]
    with get_connection() as conn:
        cursor = conn.cursor()
        for name in default_kecamatan:
            cursor.execute("""
                INSERT OR IGNORE INTO kecamatan (nama_kecamatan) VALUES (?)
            """, (name,))
        conn.commit()

def get_kecamatan_id_by_name(conn, name: str) -> int:
    """Finds or inserts a kecamatan by name and returns its ID."""
    name_clean = name.strip()
    cursor = conn.cursor()
    cursor.execute("SELECT id_kecamatan FROM kecamatan WHERE nama_kecamatan = ?", (name_clean,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # If not exists, insert it
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

def get_data_sosio_ekonomi() -> pd.DataFrame:
    """Retrieves all socio-economic data joined with kecamatan names."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                se.id_sosio,
                se.id_kecamatan,
                k.nama_kecamatan AS kecamatan,
                se.tahun,
                se.tingkat_pendidikan,
                se.pendapatan_per_kapita,
                se.tingkat_pengangguran,
                se.kepadatan_penduduk,
                se.ipm,
                se.created_at,
                se.updated_at
            FROM data_sosio_ekonomi se
            JOIN kecamatan k ON se.id_kecamatan = k.id_kecamatan
            ORDER BY se.tahun DESC, k.nama_kecamatan ASC
        """, conn)

def get_data_partisipasi_politik() -> pd.DataFrame:
    """Retrieves all political participation data joined with kecamatan names."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                pp.id_partisipasi,
                pp.id_kecamatan,
                k.nama_kecamatan AS kecamatan,
                pp.tahun,
                pp.dpt,
                pp.pengguna_hak_pilih,
                pp.partisipasi_politik,
                pp.sumber_data,
                pp.created_at,
                pp.updated_at
            FROM data_partisipasi_politik pp
            JOIN kecamatan k ON pp.id_kecamatan = k.id_kecamatan
            ORDER BY pp.tahun DESC, k.nama_kecamatan ASC
        """, conn)

def insert_or_update_sosio_ekonomi(data: dict):
    """Inserts or updates a record in data_sosio_ekonomi."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if 'id_kecamatan' not in data and 'kecamatan' in data:
            id_kec = get_kecamatan_id_by_name(conn, data['kecamatan'])
        else:
            id_kec = data['id_kecamatan']
            
        cursor.execute("""
            INSERT INTO data_sosio_ekonomi (
                id_kecamatan, tahun, tingkat_pendidikan, pendapatan_per_kapita,
                tingkat_pengangguran, kepadatan_penduduk, ipm, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(id_kecamatan, tahun) DO UPDATE SET
                tingkat_pendidikan=excluded.tingkat_pendidikan,
                pendapatan_per_kapita=excluded.pendapatan_per_kapita,
                tingkat_pengangguran=excluded.tingkat_pengangguran,
                kepadatan_penduduk=excluded.kepadatan_penduduk,
                ipm=excluded.ipm,
                updated_at=CURRENT_TIMESTAMP
        """, (
            id_kec,
            data['tahun'],
            data.get('tingkat_pendidikan'),
            data.get('pendapatan_per_kapita'),
            data.get('tingkat_pengangguran'),
            data.get('kepadatan_penduduk'),
            data.get('ipm')
        ))
        conn.commit()

def insert_or_update_partisipasi(data: dict):
    """Inserts or updates a record in data_partisipasi_politik."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if 'id_kecamatan' not in data and 'kecamatan' in data:
            id_kec = get_kecamatan_id_by_name(conn, data['kecamatan'])
        else:
            id_kec = data['id_kecamatan']
            
        dpt = data.get('dpt')
        pengguna_hak_pilih = data.get('pengguna_hak_pilih')
        partisipasi = data.get('partisipasi_politik')
        
        # Calculate automatically if dpt and pengguna_hak_pilih are available
        if partisipasi is None and dpt and pengguna_hak_pilih:
            partisipasi = (float(pengguna_hak_pilih) / float(dpt)) * 100.0
            
        cursor.execute("""
            INSERT INTO data_partisipasi_politik (
                id_kecamatan, tahun, dpt, pengguna_hak_pilih,
                partisipasi_politik, sumber_data, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(id_kecamatan, tahun) DO UPDATE SET
                dpt=excluded.dpt,
                pengguna_hak_pilih=excluded.pengguna_hak_pilih,
                partisipasi_politik=excluded.partisipasi_politik,
                sumber_data=excluded.sumber_data,
                updated_at=CURRENT_TIMESTAMP
        """, (
            id_kec,
            data['tahun'],
            dpt,
            pengguna_hak_pilih,
            partisipasi,
            data.get('sumber_data')
        ))
        conn.commit()

def save_prediction(data: dict):
    """Saves a model prediction to hasil_prediksi table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if 'id_kecamatan' not in data and 'kecamatan' in data and data['kecamatan'] is not None:
            id_kec = get_kecamatan_id_by_name(conn, data['kecamatan'])
        else:
            id_kec = data.get('id_kecamatan')
            
        cursor.execute("""
            INSERT INTO hasil_prediksi (
                id_kecamatan, tahun, tingkat_pendidikan, pendapatan_per_kapita,
                tingkat_pengangguran, kepadatan_penduduk, ipm, hasil_prediksi, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            id_kec,
            data.get('tahun'),
            data['tingkat_pendidikan'],
            data['pendapatan_per_kapita'],
            data['tingkat_pengangguran'],
            data['kepadatan_penduduk'],
            data['ipm'],
            data['hasil_prediksi']
        ))
        conn.commit()

def save_model_evaluation(data: dict):
    """Saves a model evaluation run to model_evaluasi table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_evaluasi (
                nama_model, rmse, r2_score, jumlah_data, jumlah_training, jumlah_testing, tanggal_evaluasi
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data['nama_model'],
            data.get('rmse'),
            data.get('r2_score'),
            data.get('jumlah_data'),
            data.get('jumlah_training'),
            data.get('jumlah_testing')
        ))
        conn.commit()

def get_prediction_history() -> pd.DataFrame:
    """Retrieves all prediction history records."""
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                h.id_prediksi,
                k.nama_kecamatan AS kecamatan,
                h.tahun,
                h.tingkat_pendidikan,
                h.pendapatan_per_kapita,
                h.tingkat_pengangguran,
                h.kepadatan_penduduk,
                h.ipm,
                h.hasil_prediksi,
                h.created_at
            FROM hasil_prediksi h
            LEFT JOIN kecamatan k ON h.id_kecamatan = k.id_kecamatan
            ORDER BY h.created_at DESC
        """, conn)

def delete_sosio_ekonomi(id_sosio: int):
    """Deletes a record from data_sosio_ekonomi."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data_sosio_ekonomi WHERE id_sosio = ?", (id_sosio,))
        conn.commit()

def delete_partisipasi(id_partisipasi: int):
    """Deletes a record from data_partisipasi_politik."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM data_partisipasi_politik WHERE id_partisipasi = ?", (id_partisipasi,))
        conn.commit()

