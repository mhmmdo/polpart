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
CSV_2019_PATH = ROOT_DIR / "data" / "raw" / "dataset_2019_agregat_historis.csv"

def import_2019_agregat():
    if not CSV_2019_PATH.exists():
        print(f"Warning: File CSV 2019 tidak ditemukan di {CSV_2019_PATH}")
        return
        
    try:
        df = pd.read_csv(CSV_2019_PATH)
    except Exception as e:
        print(f"Error saat membaca file CSV 2019: {e}")
        return
        
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    success_count = 0
    skipped_count = 0
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data_partisipasi_agregat")
            
            for idx, row in df.iterrows():
                tahun = row.get("tahun_pemilu")
                kec = row.get("kecamatan")
                dapil = row.get("dapil")
                
                if pd.isna(tahun) or pd.isna(kec):
                    skipped_count += 1
                    continue
                    
                def clean_float(val):
                    try:
                        if pd.isna(val): return None
                        if isinstance(val, str): val = val.replace(",", "")
                        return float(val)
                    except:
                        return None
                        
                def clean_int(val):
                    try:
                        if pd.isna(val): return None
                        if isinstance(val, str): val = val.replace(",", "")
                        return int(float(val))
                    except:
                        return None
                        
                cursor.execute("""
                    INSERT INTO data_partisipasi_agregat (
                        tahun_pemilu, level_data, dapil, kecamatan, dpt_total,
                        pengguna_total, partisipasi_politik, sumber_data, catatan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(tahun),
                    'agregat',
                    str(dapil) if not pd.isna(dapil) else None,
                    str(kec).strip().upper(),
                    clean_int(row.get("dpt_total")),
                    clean_int(row.get("pengguna_hak_pilih_total")),
                    clean_float(row.get("partisipasi_politik")),
                    'KPU',
                    'Data Historis 2019'
                ))
                success_count += 1
            conn.commit()
        print("Proses Impor Agregat 2019 Selesai!")
        print(f"Jumlah baris berhasil diimpor: {success_count}")
    except Exception as e:
        print(f"Error saat impor 2019 agregat: {e}")

def main():
    if not CSV_2024_PATH.exists():
        print(f"Error: File CSV TPS tidak ditemukan di {CSV_2024_PATH}")
        sys.exit(1)
        
    try:
        df = pd.read_csv(CSV_2024_PATH)
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
                    
                pend_kec = clean_int(row.get("penduduk_total_kecamatan"))
                rasio_dpt = clean_float(row.get("rasio_dpt_terhadap_penduduk_kelurahan"))
                
                # Socio-economic features
                pendapatan = clean_float(row.get("pendapatan_per_kapita"))
                pengangguran = clean_float(row.get("tingkat_pengangguran"))
                kepadatan = clean_float(row.get("kepadatan_penduduk"))
                ipm = clean_float(row.get("ipm"))
                
                # Age distributions
                j_usia_17_24 = clean_int(row.get("jumlah_usia_17_24_kec"))
                j_usia_25_44 = clean_int(row.get("jumlah_usia_25_44_kec"))
                j_usia_45_plus = clean_int(row.get("jumlah_usia_45_plus_kec"))
                
                p_usia_17_24 = clean_float(row.get("persen_usia_17_24_kec"))
                p_usia_25_44 = clean_float(row.get("persen_usia_25_44_kec"))
                p_usia_45_plus = clean_float(row.get("persen_usia_45_plus_kec"))
                
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
                    row.get("id_record"),
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
                
            conn.commit()
            
        print("Proses Impor TPS Selesai!")
        print(f"Jumlah baris berhasil diimpor: {success_count}")
        print(f"Jumlah baris dilewati: {skipped_count}")
        
        # Now import 2019 Agregat data
        print("Mengimpor data agregat 2019...")
        import_2019_agregat()
        
        # Populate new master and transaction tables from the imported TPS data
        print("Mengisi tabel master kelurahan, tps, dan suara_partai_tps...")
        from src.database import seed_relational_tables_from_tps
        seed_relational_tables_from_tps()
        print("Pengisian tabel relasional baru selesai.")
        
    except Exception as e:
        print(f"Error sistem saat impor TPS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
