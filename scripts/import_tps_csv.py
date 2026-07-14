import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.config import DB_PATH
from src.database import get_connection

CSV_2024_PATH = ROOT_DIR / "data" / "raw" / "dataset_2024_tps_model_final.csv"
CSV_2019_PATH = ROOT_DIR / "data" / "raw" / "dataset_2019_tps_model_final.csv"
CSV_2029_PATH = ROOT_DIR / "data" / "raw" / "dataset_2029_tps_model_final.csv"

def import_csv_file(cursor, file_path):
    if not file_path.exists():
        print(f"Warning: File CSV tidak ditemukan di {file_path}")
        return 0, 0
        
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error saat membaca file CSV {file_path}: {e}")
        return 0, 0
        
    # Standardize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )
    
    # Required columns check
    required = ["tahun_pemilu", "kecamatan", "kelurahan", "no_tps", "partisipasi_politik"]
    for col in required:
        if col not in df.columns:
            print(f"Error: Kolom wajib '{col}' tidak ditemukan di CSV {file_path}.")
            return 0, 0
            
    success_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        tahun = row.get("tahun_pemilu")
        kec = row.get("kecamatan")
        kel = row.get("kelurahan")
        tps = row.get("no_tps")
        
        if pd.isna(tahun) or pd.isna(kec) or pd.isna(kel) or pd.isna(tps):
            skipped_count += 1
            continue
            
        def clean_float(val):
            try:
                if pd.isna(val):
                    return None
                if isinstance(val, str):
                    val = val.replace(",", "")
                return float(val)
            except Exception:
                return None
                
        def clean_int(val):
            try:
                if pd.isna(val):
                    return None
                if isinstance(val, str):
                    val = val.replace(",", "")
                return int(float(val))
            except Exception:
                return None
        
        dpt = clean_int(row.get("dpt"))
        pilih = clean_int(row.get("pengguna_hak_pilih"))
        partisipasi = clean_float(row.get("partisipasi_politik"))
        dpt_total = clean_int(row.get("dpt_total_tps"))
        
        penduduk_kel = row.get("penduduk_total_kelurahan")
        if pd.isna(penduduk_kel):
            penduduk_kel = None
        else:
            penduduk_kel = str(penduduk_kel).strip()
            
        pend_kec = clean_int(row.get("penduduk_total_kecamatan"))
        rasio_dpt = clean_float(row.get("rasio_dpt_terhadap_penduduk_kelurahan"))
        
        pendapatan = clean_float(row.get("pendapatan_per_kapita"))
        pengangguran = clean_float(row.get("tingkat_pengangguran"))
        kepadatan = clean_float(row.get("kepadatan_penduduk"))
        ipm = clean_float(row.get("ipm"))
        
        j_usia_17_24 = clean_int(row.get("jumlah_usia_17_24_kec"))
        j_usia_25_44 = clean_int(row.get("jumlah_usia_25_44_kec"))
        j_usia_45_plus = clean_int(row.get("jumlah_usia_45_plus_kec"))
        
        p_usia_17_24 = clean_float(row.get("persen_usia_17_24_kec"))
        p_usia_25_44 = clean_float(row.get("persen_usia_25_44_kec"))
        p_usia_45_plus = clean_float(row.get("persen_usia_45_plus_kec"))
        
        id_rec = row.get("id_record")
        if pd.isna(id_rec):
            id_rec = f"{tahun}-{kec}-{kel}-{tps}".strip().upper()
        else:
            id_rec = str(id_rec).strip().upper()
            
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
            int(tahun),
            'tps',
            str(kec).strip().upper(),
            str(kel).strip().upper(),
            str(tps).strip(),
            id_rec,
            dpt,
            pilih,
            partisipasi,
            dpt_total,
            penduduk_kel,
            pend_kec,
            rasio_dpt,
            pendapatan,
            pengangguran,
            kepadatan,
            ipm,
            j_usia_17_24,
            j_usia_25_44,
            j_usia_45_plus,
            p_usia_17_24,
            p_usia_25_44,
            p_usia_45_plus
        ))
        success_count += 1
        
    return success_count, skipped_count

def main():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing TPS data
            cursor.execute("DELETE FROM data_partisipasi_tps")
            
            print("Mengimpor data TPS 2024...")
            s1, sk1 = import_csv_file(cursor, CSV_2024_PATH)
            print(f"TPS 2024: {s1} diimpor, {sk1} dilewati.")
            
            print("Mengimpor data TPS 2019...")
            s2, sk2 = import_csv_file(cursor, CSV_2019_PATH)
            print(f"TPS 2019: {s2} diimpor, {sk2} dilewati.")
            
            print("Mengimpor data TPS 2029...")
            s3, sk3 = import_csv_file(cursor, CSV_2029_PATH)
            print(f"TPS 2029: {s3} diimpor, {sk3} dilewati.")
            
            conn.commit()
            
        print("Pengisi tabel master kelurahan, tps, dan suara_partai_tps...")
        from src.database import seed_relational_tables_from_tps
        seed_relational_tables_from_tps()
        print("Inisialisasi data sukses.")
    except Exception as e:
        print(f"Error saat impor TPS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
