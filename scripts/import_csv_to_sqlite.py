import sqlite3
import pandas as pd
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.config import DB_PATH
from src.database import get_connection, get_kecamatan_id_by_name

CSV_PATH = ROOT_DIR / "data" / "import" / "data_final_template.csv"

def main():
    if not CSV_PATH.exists():
        print(f"Error: File CSV tidak ditemukan di {CSV_PATH}")
        print("Pastikan Anda sudah meletakkan template CSV di folder tersebut.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error saat membaca file CSV: {e}")
        sys.exit(1)
        
    # Standardize column names (lowercase and underscore)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    
    # Required columns check
    required = ["tahun", "kecamatan"]
    for col in required:
        if col not in df.columns:
            print(f"Error: Kolom wajib '{col}' tidak ditemukan di CSV.")
            sys.exit(1)
            
    success_count = 0
    skipped_count = 0
    
    # Open connection and import rows
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for idx, row in df.iterrows():
                tahun = row.get("tahun")
                kecamatan = row.get("kecamatan")
                
                # Ignore row if tahun or kecamatan is empty/NaN
                if pd.isna(tahun) or pd.isna(kecamatan) or str(kecamatan).strip() == "":
                    skipped_count += 1
                    continue
                    
                try:
                    tahun = int(float(tahun))  # Convert to float first in case it has decimal string representation
                    kecamatan = str(kecamatan).strip()
                except Exception:
                    skipped_count += 1
                    continue
                
                # Get or create id_kecamatan
                try:
                    id_kecamatan = get_kecamatan_id_by_name(conn, kecamatan)
                except Exception as e:
                    print(f"Error saat memproses kecamatan '{kecamatan}' pada baris {idx+1}: {e}")
                    skipped_count += 1
                    continue
                
                # Clean metric values
                def clean_float(val):
                    try:
                        return float(val) if pd.notna(val) else None
                    except Exception:
                        return None
                        
                tingkat_pendidikan = clean_float(row.get("tingkat_pendidikan"))
                pendapatan_per_kapita = clean_float(row.get("pendapatan_per_kapita"))
                tingkat_pengangguran = clean_float(row.get("tingkat_pengangguran"))
                kepadatan_penduduk = clean_float(row.get("kepadatan_penduduk"))
                ipm = clean_float(row.get("ipm"))
                partisipasi_politik = clean_float(row.get("partisipasi_politik"))
                
                # Upsert into data_sosio_ekonomi
                try:
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
                        id_kecamatan,
                        tahun,
                        tingkat_pendidikan,
                        pendapatan_per_kapita,
                        tingkat_pengangguran,
                        kepadatan_penduduk,
                        ipm
                    ))
                    
                    # Upsert into data_partisipasi_politik
                    cursor.execute("""
                        INSERT INTO data_partisipasi_politik (
                            id_kecamatan, tahun, dpt, pengguna_hak_pilih,
                            partisipasi_politik, sumber_data, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ON CONFLICT(id_kecamatan, tahun) DO UPDATE SET
                            partisipasi_politik=excluded.partisipasi_politik,
                            sumber_data=excluded.sumber_data,
                            updated_at=CURRENT_TIMESTAMP
                    """, (
                        id_kecamatan,
                        tahun,
                        None, # dpt is not in csv template
                        None, # pengguna_hak_pilih is not in csv template
                        partisipasi_politik,
                        "Import CSV"
                    ))
                    success_count += 1
                except Exception as e:
                    print(f"Error saat menyimpan data baris {idx+1}: {e}")
                    skipped_count += 1
                    
            conn.commit()
            
        print(f"Proses Impor Selesai!")
        print(f"Jumlah baris berhasil diimpor: {success_count}")
        print(f"Jumlah baris dilewati/gagal: {skipped_count}")
    except Exception as e:
        print(f"Error sistem saat impor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
