import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.config import DB_PATH
from src.database import get_connection

CSV_PATH = ROOT_DIR / "data" / "raw" / "data_partisipasi_per_tps.csv"

def main():
    if not CSV_PATH.exists():
        print(f"Error: File CSV TPS tidak ditemukan di {CSV_PATH}")
        sys.exit(1)
        
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error saat membaca file CSV: {e}")
        sys.exit(1)
        
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
            print(f"Error: Kolom wajib '{col}' tidak ditemukan di CSV.")
            sys.exit(1)
            
    success_count = 0
    skipped_count = 0
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing TPS data to avoid duplicates on re-import
            cursor.execute("DELETE FROM data_partisipasi_tps")
            
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
                        # Remove commas from numeric strings
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
                
                # Total penduduk kelurahan can contain commas
                penduduk_kel = row.get("penduduk_total_kelurahan")
                if pd.isna(penduduk_kel):
                    penduduk_kel = None
                else:
                    penduduk_kel = str(penduduk_kel).strip()
                    
                rasio_dpt = clean_float(row.get("rasio_dpt_terhadap_penduduk_kelurahan"))
                u17_24 = clean_float(row.get("persen_usia_17_24_kec"))
                u25_44 = clean_float(row.get("persen_usia_25_44_kec"))
                u45_plus = clean_float(row.get("persen_usia_45_plus_kec"))
                
                cursor.execute("""
                    INSERT INTO data_partisipasi_tps (
                        tahun_pemilu, kecamatan, kelurahan, no_tps, id_record, jenis_kelamin,
                        dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                        penduduk_total_kelurahan, rasio_dpt_terhadap_penduduk_kelurahan,
                        persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(tahun),
                    str(kec).strip().upper(),
                    str(kel).strip().upper(),
                    str(tps).strip(),
                    row.get("id_record"),
                    row.get("jenis_kelamin"),
                    dpt,
                    pilih,
                    partisipasi,
                    dpt_total,
                    penduduk_kel,
                    rasio_dpt,
                    u17_24,
                    u25_44,
                    u45_plus
                ))
                success_count += 1
                
            conn.commit()
            
        print("Proses Impor TPS Selesai!")
        print(f"Jumlah baris berhasil diimpor: {success_count}")
        print(f"Jumlah baris dilewati: {skipped_count}")
    except Exception as e:
        print(f"Error sistem saat impor TPS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
